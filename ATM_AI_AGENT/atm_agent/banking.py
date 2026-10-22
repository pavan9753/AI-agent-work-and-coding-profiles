"""SQLite-backed operations for the fictional demo ATM."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator

DB_PATH = Path(os.getenv("ATM_DB_PATH", Path(__file__).with_name("atm_demo.db")))
MAX_FAILED_ATTEMPTS = 5
MAX_SINGLE_WITHDRAWAL_PAISE = 2_500_000  # ₹25,000
DAILY_WITHDRAWAL_LIMIT_PAISE = 5_000_000  # ₹50,000
MAX_TRANSACTION_PAISE = 100_000_000_000  # ₹1,000,000,000 demo cap for SQLite safety
BANK_TIMEZONE = timezone(timedelta(hours=5, minutes=30), name="IST")


@contextmanager
def connection(*, immediate: bool = False) -> Iterator[sqlite3.Connection]:
    """Open a short-lived connection and commit or roll back atomically."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if immediate:
        conn.execute("BEGIN IMMEDIATE")
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
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pin_salt BLOB NOT NULL,
                pin_hash BLOB NOT NULL,
                balance_paise INTEGER NOT NULL DEFAULT 0 CHECK(balance_paise >= 0),
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL REFERENCES accounts(customer_id),
                kind TEXT NOT NULL,
                amount_paise INTEGER NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_transactions_customer
                ON transactions(customer_id, id DESC);
            """
        )


def _hash_pin(pin: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 310_000)


def _valid_pin(pin: str) -> bool:
    return pin.isascii() and pin.isdigit() and len(pin) == 4


def _money_to_paise(value: str | float | int | Decimal) -> int:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid amount in INR.") from None
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be positive and have at most two decimal places.")
    if amount > Decimal(MAX_TRANSACTION_PAISE) / 100:
        raise ValueError("Amount exceeds the maximum supported demo transaction.")
    paise = int(amount * 100)
    return paise


def _inr(paise: int) -> str:
    return f"₹{paise / 100:,.2f}"


def seed_demo_account() -> None:
    """Create the two fictional sample accounts once, preserving later balances."""
    init_db()
    with connection() as conn:
        for customer_id, name, pin, balance_paise in (
            ("100001", "Demo Customer", "1234", 250_000),
            ("100002", "Demo Recipient", "2345", 100_000),
        ):
            salt = secrets.token_bytes(16)
            conn.execute(
                """INSERT OR IGNORE INTO accounts
                   (customer_id, name, pin_salt, pin_hash, balance_paise)
                   VALUES (?, ?, ?, ?, ?)""",
                (customer_id, name, salt, _hash_pin(pin, salt), balance_paise),
            )


def authenticate(customer_id: str, pin: str) -> dict[str, str]:
    init_db()
    customer_id = customer_id.strip()
    if not customer_id or not _valid_pin(pin):
        return {"status": "error", "message": "Customer ID or PIN is incorrect."}
    with connection() as conn:
        account = conn.execute(
            "SELECT * FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        # Do not reveal whether an account exists.
        if account is None:
            return {"status": "error", "message": "Customer ID or PIN is incorrect."}
        if account["locked"]:
            return {"status": "error", "message": "This demo account is locked. Contact the bank."}
        if not secrets.compare_digest(
            _hash_pin(pin, account["pin_salt"]), account["pin_hash"]
        ):
            attempts = account["failed_attempts"] + 1
            locked = int(attempts >= MAX_FAILED_ATTEMPTS)
            conn.execute(
                "UPDATE accounts SET failed_attempts = ?, locked = ? WHERE customer_id = ?",
                (attempts, locked, customer_id),
            )
            message = (
                "This demo account is locked after too many attempts."
                if locked
                else "Customer ID or PIN is incorrect."
            )
            return {"status": "error", "message": message}
        conn.execute(
            "UPDATE accounts SET failed_attempts = 0 WHERE customer_id = ?",
            (customer_id,),
        )
        return {
            "status": "success",
            "customer_id": account["customer_id"],
            "name": account["name"],
            "message": f"Welcome, {account['name']}. You are signed in.",
        }


def balance(customer_id: str) -> dict[str, str]:
    with connection() as conn:
        account = conn.execute(
            "SELECT balance_paise FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
    if account is None:
        return {"status": "error", "message": "Account not found."}
    return {"status": "success", "balance": _inr(account["balance_paise"]), "currency": "INR"}


def _record(
    conn: sqlite3.Connection,
    customer_id: str,
    kind: str,
    amount_paise: int,
    description: str,
) -> int:
    cursor = conn.execute(
        """INSERT INTO transactions
           (customer_id, kind, amount_paise, description, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (
            customer_id,
            kind,
            amount_paise,
            description,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )
    return int(cursor.lastrowid)


def deposit(customer_id: str, amount: str | float | int | Decimal) -> dict[str, str]:
    amount_paise = _money_to_paise(amount)
    with connection(immediate=True) as conn:
        cursor = conn.execute(
            "UPDATE accounts SET balance_paise = balance_paise + ? WHERE customer_id = ?",
            (amount_paise, customer_id),
        )
        if cursor.rowcount != 1:
            return {"status": "error", "message": "Account not found."}
        transaction_id = _record(conn, customer_id, "deposit", amount_paise, "Cash deposit")
        new_balance = conn.execute(
            "SELECT balance_paise FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()[0]
    return {
        "status": "success",
        "transaction_id": str(transaction_id),
        "deposited": _inr(amount_paise),
        "balance": _inr(new_balance),
    }


def _withdrawn_today(conn: sqlite3.Connection, customer_id: str) -> int:
    today_ist = datetime.now(BANK_TIMEZONE).date()
    start_utc = datetime.combine(today_ist, time.min, BANK_TIMEZONE).astimezone(timezone.utc)
    end_utc = datetime.combine(
        today_ist + timedelta(days=1), time.min, BANK_TIMEZONE
    ).astimezone(timezone.utc)
    row = conn.execute(
        """SELECT COALESCE(SUM(amount_paise), 0) FROM transactions
           WHERE customer_id = ? AND kind = 'withdrawal'
             AND created_at >= ? AND created_at < ?""",
        (
            customer_id,
            start_utc.isoformat(timespec="seconds"),
            end_utc.isoformat(timespec="seconds"),
        ),
    ).fetchone()
    return int(row[0])


def withdrawal_limits(customer_id: str) -> dict[str, str | int]:
    """Return configured per-transaction and remaining daily cash limits."""
    with connection() as conn:
        exists = conn.execute(
            "SELECT 1 FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        if exists is None:
            return {"status": "error", "message": "Account not found."}
        withdrawn = _withdrawn_today(conn, customer_id)
    remaining = max(0, DAILY_WITHDRAWAL_LIMIT_PAISE - withdrawn)
    return {
        "status": "success",
        "currency": "INR",
        "per_withdrawal_limit": _inr(MAX_SINGLE_WITHDRAWAL_PAISE),
        "daily_limit": _inr(DAILY_WITHDRAWAL_LIMIT_PAISE),
        "withdrawn_today": _inr(withdrawn),
        "remaining_today": _inr(remaining),
        "remaining_today_paise": remaining,
    }


def withdraw(customer_id: str, amount: str | float | int | Decimal) -> dict[str, str | int]:
    amount_paise = _money_to_paise(amount)
    if amount_paise > MAX_SINGLE_WITHDRAWAL_PAISE:
        return {
            "status": "error",
            "message": f"This demo ATM allows up to {_inr(MAX_SINGLE_WITHDRAWAL_PAISE)} per withdrawal.",
        }
    with connection(immediate=True) as conn:
        account = conn.execute(
            "SELECT balance_paise FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        if account is None:
            return {"status": "error", "message": "Account not found."}
        withdrawn = _withdrawn_today(conn, customer_id)
        if withdrawn + amount_paise > DAILY_WITHDRAWAL_LIMIT_PAISE:
            remaining = max(0, DAILY_WITHDRAWAL_LIMIT_PAISE - withdrawn)
            return {
                "status": "error",
                "message": f"Daily withdrawal limit reached. Remaining today: {_inr(remaining)}.",
            }
        if account["balance_paise"] < amount_paise:
            return {"status": "error", "message": "Insufficient funds."}
        cursor = conn.execute(
            "UPDATE accounts SET balance_paise = balance_paise - ? WHERE customer_id = ?",
            (amount_paise, customer_id),
        )
        transaction_id = _record(conn, customer_id, "withdrawal", amount_paise, "Cash withdrawal")
        new_balance = conn.execute(
            "SELECT balance_paise FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()[0]
    return {
        "status": "success",
        "transaction_id": str(transaction_id),
        "withdrawn": _inr(amount_paise),
        "balance": _inr(new_balance),
    }


def transfer(
    customer_id: str, recipient_id: str, amount: str | float | int | Decimal
) -> dict[str, str]:
    amount_paise = _money_to_paise(amount)
    recipient_id = recipient_id.strip()
    if recipient_id == customer_id:
        return {"status": "error", "message": "You cannot transfer to the same account."}
    with connection(immediate=True) as conn:
        recipient = conn.execute(
            "SELECT 1 FROM accounts WHERE customer_id = ?", (recipient_id,)
        ).fetchone()
        if recipient is None:
            return {"status": "error", "message": "Recipient account not found."}
        cursor = conn.execute(
            """UPDATE accounts SET balance_paise = balance_paise - ?
               WHERE customer_id = ? AND balance_paise >= ?""",
            (amount_paise, customer_id, amount_paise),
        )
        if cursor.rowcount != 1:
            return {"status": "error", "message": "Insufficient funds or source account not found."}
        conn.execute(
            "UPDATE accounts SET balance_paise = balance_paise + ? WHERE customer_id = ?",
            (amount_paise, recipient_id),
        )
        transaction_id = _record(
            conn, customer_id, "transfer_out", amount_paise, f"Transfer to {recipient_id}"
        )
        _record(conn, recipient_id, "transfer_in", amount_paise, f"Transfer from {customer_id}")
        new_balance = conn.execute(
            "SELECT balance_paise FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()[0]
    return {
        "status": "success",
        "transaction_id": str(transaction_id),
        "transferred": _inr(amount_paise),
        "recipient": recipient_id,
        "balance": _inr(new_balance),
    }


def history(customer_id: str, limit: int = 10) -> dict[str, object]:
    limit = max(1, min(int(limit), 20))
    with connection() as conn:
        rows = conn.execute(
            """SELECT id, kind, amount_paise, description, created_at FROM transactions
               WHERE customer_id = ? ORDER BY id DESC LIMIT ?""",
            (customer_id, limit),
        ).fetchall()
    return {
        "status": "success",
        "transactions": [
            {
                "transaction_id": str(row["id"]),
                "type": row["kind"],
                "amount": _inr(row["amount_paise"]),
                "description": row["description"],
                "date": row["created_at"],
            }
            for row in rows
        ],
    }


def change_pin(customer_id: str, current_pin: str, new_pin: str) -> dict[str, str]:
    if not _valid_pin(new_pin):
        return {"status": "error", "message": "New PIN must contain exactly four ASCII digits."}
    with connection(immediate=True) as conn:
        account = conn.execute(
            "SELECT pin_salt, pin_hash FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        if account is None or not _valid_pin(current_pin) or not secrets.compare_digest(
            _hash_pin(current_pin, account["pin_salt"]), account["pin_hash"]
        ):
            return {"status": "error", "message": "Current PIN is incorrect."}
        salt = secrets.token_bytes(16)
        conn.execute(
            "UPDATE accounts SET pin_salt = ?, pin_hash = ? WHERE customer_id = ?",
            (salt, _hash_pin(new_pin, salt), customer_id),
        )
    return {"status": "success", "message": "Your demo PIN was changed."}
