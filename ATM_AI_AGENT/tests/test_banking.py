from __future__ import annotations

import pytest

from atm_agent import banking


def test_demo_accounts_seed_once_and_authenticate(demo_db):
    assert banking.authenticate("100001", "1234")["status"] == "success"
    assert banking.authenticate("100002", "2345")["status"] == "success"
    banking.deposit("100001", "2.50")
    banking.seed_demo_account()
    assert banking.balance("100001")["balance"] == "₹2,502.50"


def test_authentication_uses_generic_errors_and_locks_after_five_attempts(demo_db):
    missing = banking.authenticate("999999", "1234")
    wrong = banking.authenticate("100001", "0000")
    assert missing["message"] == wrong["message"]

    for _ in range(banking.MAX_FAILED_ATTEMPTS - 1):
        banking.authenticate("100001", "0000")
    locked = banking.authenticate("100001", "0000")
    assert locked["status"] == "error"
    assert "locked" in locked["message"].lower()
    assert banking.authenticate("100001", "1234")["status"] == "error"


@pytest.mark.parametrize(
    "amount", [0, -1, "NaN", "Infinity", "1.001", "not-money", "1e100", "1e1000000"]
)
def test_money_operations_reject_invalid_amounts_without_changing_balance(demo_db, amount):
    before = banking.balance("100001")["balance"]
    with pytest.raises(ValueError):
        banking.deposit("100001", amount)
    assert banking.balance("100001")["balance"] == before


def test_deposit_returns_receipt_and_history(demo_db):
    deposit = banking.deposit("100001", "100.25")
    assert deposit["status"] == "success"
    assert deposit["deposited"] == "₹100.25"
    assert deposit["balance"] == "₹2,600.25"
    assert deposit["transaction_id"].isdigit()
    transaction = banking.history("100001")["transactions"][0]
    assert transaction["type"] == "deposit"
    assert transaction["transaction_id"] == deposit["transaction_id"]


def test_withdrawal_enforces_per_transaction_and_daily_limits(demo_db):
    banking.deposit("100001", "60000")
    single_limit = banking.withdraw("100001", "25000.01")
    assert single_limit["status"] == "error"
    assert "per withdrawal" in single_limit["message"].lower()

    first = banking.withdraw("100001", "25000")
    second = banking.withdraw("100001", "25000")
    over_daily = banking.withdraw("100001", "0.01")
    assert first["status"] == second["status"] == "success"
    assert over_daily["status"] == "error"
    assert "daily withdrawal limit" in over_daily["message"].lower()
    limits = banking.withdrawal_limits("100001")
    assert limits["remaining_today"] == "₹0.00"
    assert banking.balance("100001")["balance"] == "₹12,500.00"


def test_withdrawal_rejects_insufficient_funds(demo_db):
    result = banking.withdraw("100001", "2500.01")
    assert result == {"status": "error", "message": "Insufficient funds."}
    assert banking.balance("100001")["balance"] == "₹2,500.00"


def test_transfer_updates_both_accounts_and_records_both_sides(demo_db):
    transfer = banking.transfer("100001", "100002", "125.50")
    assert transfer["status"] == "success"
    assert transfer["transferred"] == "₹125.50"
    assert transfer["balance"] == "₹2,374.50"
    assert banking.balance("100002")["balance"] == "₹1,125.50"
    assert banking.history("100001")["transactions"][0]["type"] == "transfer_out"
    assert banking.history("100002")["transactions"][0]["type"] == "transfer_in"


@pytest.mark.parametrize(
    ("recipient", "amount", "expected"),
    [
        ("100001", 10, "same account"),
        ("999999", 10, "recipient account not found"),
        ("100002", 9999, "insufficient funds"),
    ],
)
def test_transfer_rejects_invalid_recipient_or_funds(demo_db, recipient, amount, expected):
    result = banking.transfer("100001", recipient, amount)
    assert result["status"] == "error"
    assert expected in result["message"].lower()
    assert banking.balance("100001")["balance"] == "₹2,500.00"
    assert banking.balance("100002")["balance"] == "₹1,000.00"


def test_pin_change_validates_current_pin_and_new_pin(demo_db):
    assert banking.change_pin("100001", "9999", "5678")["status"] == "error"
    assert banking.change_pin("100001", "1234", "12ab")["status"] == "error"
    assert banking.change_pin("100001", "1234", "5678")["status"] == "success"
    assert banking.authenticate("100001", "1234")["status"] == "error"
    assert banking.authenticate("100001", "5678")["status"] == "success"


def test_history_is_bounded_and_missing_account_is_reported(demo_db):
    for amount in range(1, 25):
        banking.deposit("100001", amount)
    history = banking.history("100001", 500)["transactions"]
    assert len(history) == 20
    assert banking.balance("missing")["status"] == "error"
