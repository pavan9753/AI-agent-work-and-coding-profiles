"""SQLite-backed demo ATM operations for the Google ADK agent."""
from __future__ import annotations
import hashlib, os, secrets, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator

DB_PATH = Path(os.getenv("ATM_DB_PATH", Path(__file__).with_name("atm_demo.db")))
MAX_FAILED_ATTEMPTS = 5

@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    with connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                customer_id TEXT PRIMARY KEY, name TEXT NOT NULL, pin_salt BLOB NOT NULL,
                pin_hash BLOB NOT NULL, balance_paise INTEGER NOT NULL DEFAULT 0 CHECK(balance_paise >= 0),
                failed_attempts INTEGER NOT NULL DEFAULT 0, locked INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT NOT NULL REFERENCES accounts(customer_id),
                kind TEXT NOT NULL, amount_paise INTEGER NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id, id DESC);
        """)

def _hash_pin(pin: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 310_000)

def _valid_pin(pin: str) -> bool:
    return pin.isdigit() and len(pin) == 4

def _money_to_paise(value: str | float | int) -> int:
    try: amount = Decimal(str(value))
    except (InvalidOperation, ValueError): raise ValueError("Enter a valid amount in INR.") from None
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be positive and have at most two decimal places.")
    return int(amount * 100)

def _inr(paise: int) -> str: return f"₹{paise / 100:,.2f}"

def seed_demo_account() -> None:
    init_db(); salt = secrets.token_bytes(16)
    with connection() as conn:
        conn.execute("INSERT OR IGNORE INTO accounts(customer_id,name,pin_salt,pin_hash,balance_paise) VALUES(?,?,?,?,?)",
                     ("100001", "Demo Customer", salt, _hash_pin("1234", salt), 250_000))
        second_salt = secrets.token_bytes(16)
        conn.execute("INSERT OR IGNORE INTO accounts(customer_id,name,pin_salt,pin_hash,balance_paise) VALUES(?,?,?,?,?)",
                     ("100002", "Demo Recipient", second_salt, _hash_pin("2345", second_salt), 100_000))

def authenticate(customer_id: str, pin: str) -> dict[str, str]:
    init_db(); customer_id = customer_id.strip()
    with connection() as conn:
        row = conn.execute("SELECT * FROM accounts WHERE customer_id=?", (customer_id,)).fetchone()
        if row is None: return {"status":"error", "message":"Customer ID or PIN is incorrect."}
        if row["locked"]: return {"status":"error", "message":"This demo account is locked. Contact the bank."}
        if not secrets.compare_digest(_hash_pin(pin, row["pin_salt"]), row["pin_hash"]):
            attempts = row["failed_attempts"] + 1; locked = int(attempts >= MAX_FAILED_ATTEMPTS)
            conn.execute("UPDATE accounts SET failed_attempts=?,locked=? WHERE customer_id=?", (attempts,locked,customer_id))
            message = "This demo account is locked after too many attempts." if locked else "Customer ID or PIN is incorrect."
            return {"status":"error", "message":message}
        conn.execute("UPDATE accounts SET failed_attempts=0 WHERE customer_id=?", (customer_id,))
        return {"status":"success", "customer_id":row["customer_id"], "name":row["name"], "message":f"Welcome, {row['name']}. You are signed in."}

def balance(customer_id: str) -> dict[str, str]:
    with connection() as conn: row=conn.execute("SELECT balance_paise FROM accounts WHERE customer_id=?",(customer_id,)).fetchone()
    if row is None: return {"status":"error","message":"Account not found."}
    return {"status":"success","balance":_inr(row["balance_paise"]),"currency":"INR"}

def _record(conn, customer_id, kind, amount, description):
    conn.execute("INSERT INTO transactions(customer_id,kind,amount_paise,description,created_at) VALUES(?,?,?,?,?)",
                 (customer_id,kind,amount,description,datetime.now(timezone.utc).isoformat(timespec="seconds")))

def deposit(customer_id: str, amount: str | float | int) -> dict[str,str]:
    paise=_money_to_paise(amount)
    with connection() as conn:
        cur=conn.execute("UPDATE accounts SET balance_paise=balance_paise+? WHERE customer_id=?",(paise,customer_id))
        if cur.rowcount != 1: return {"status":"error","message":"Account not found."}
        _record(conn,customer_id,"deposit",paise,"Cash deposit")
        new=conn.execute("SELECT balance_paise FROM accounts WHERE customer_id=?",(customer_id,)).fetchone()[0]
    return {"status":"success","deposited":_inr(paise),"balance":_inr(new)}

def withdraw(customer_id: str, amount: str | float | int) -> dict[str,str]:
    paise=_money_to_paise(amount)
    with connection() as conn:
        cur=conn.execute("UPDATE accounts SET balance_paise=balance_paise-? WHERE customer_id=? AND balance_paise>=?",(paise,customer_id,paise))
        if cur.rowcount != 1:
            exists=conn.execute("SELECT 1 FROM accounts WHERE customer_id=?",(customer_id,)).fetchone()
            return {"status":"error","message":"Insufficient funds." if exists else "Account not found."}
        _record(conn,customer_id,"withdrawal",paise,"Cash withdrawal")
        new=conn.execute("SELECT balance_paise FROM accounts WHERE customer_id=?",(customer_id,)).fetchone()[0]
    return {"status":"success","withdrawn":_inr(paise),"balance":_inr(new)}

def transfer(customer_id: str, recipient_id: str, amount: str | float | int) -> dict[str,str]:
    paise=_money_to_paise(amount); recipient_id=recipient_id.strip()
    if recipient_id == customer_id: return {"status":"error","message":"You cannot transfer to the same account."}
    with connection() as conn:
        if not conn.execute("SELECT 1 FROM accounts WHERE customer_id=?",(recipient_id,)).fetchone():
            return {"status":"error","message":"Recipient account not found."}
        cur=conn.execute("UPDATE accounts SET balance_paise=balance_paise-? WHERE customer_id=? AND balance_paise>=?",(paise,customer_id,paise))
        if cur.rowcount != 1: return {"status":"error","message":"Insufficient funds or source account not found."}
        conn.execute("UPDATE accounts SET balance_paise=balance_paise+? WHERE customer_id=?",(paise,recipient_id))
        _record(conn,customer_id,"transfer_out",paise,f"Transfer to {recipient_id}")
        _record(conn,recipient_id,"transfer_in",paise,f"Transfer from {customer_id}")
        new=conn.execute("SELECT balance_paise FROM accounts WHERE customer_id=?",(customer_id,)).fetchone()[0]
    return {"status":"success","transferred":_inr(paise),"recipient":recipient_id,"balance":_inr(new)}

def history(customer_id: str, limit: int=10) -> dict[str,object]:
    limit=max(1,min(limit,20))
    with connection() as conn:
        rows=conn.execute("SELECT kind,amount_paise,description,created_at FROM transactions WHERE customer_id=? ORDER BY id DESC LIMIT ?",(customer_id,limit)).fetchall()
    return {"status":"success","transactions":[{"type":r["kind"],"amount":_inr(r["amount_paise"]),"description":r["description"],"date":r["created_at"]} for r in rows]}

def change_pin(customer_id: str, current_pin: str, new_pin: str) -> dict[str,str]:
    if not _valid_pin(new_pin): return {"status":"error","message":"New PIN must contain exactly four digits."}
    with connection() as conn:
        row=conn.execute("SELECT pin_salt,pin_hash FROM accounts WHERE customer_id=?",(customer_id,)).fetchone()
        if row is None or not secrets.compare_digest(_hash_pin(current_pin,row["pin_salt"]),row["pin_hash"]):
            return {"status":"error","message":"Current PIN is incorrect."}
        salt=secrets.token_bytes(16)
        conn.execute("UPDATE accounts SET pin_salt=?,pin_hash=? WHERE customer_id=?",(salt,_hash_pin(new_pin,salt),customer_id))
    return {"status":"success","message":"Your demo PIN was changed."}
