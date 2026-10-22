"""ADK-callable tools: authenticated ATM actions plus a read-only MCP lookup."""

from __future__ import annotations

import asyncio
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from google.adk.tools import ToolContext
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from . import banking

FRANKFURTER_MCP_URL = "https://mcp.frankfurter.dev/"
MAX_REFERENCE_AMOUNT = Decimal("1000000000000")
_CURRENCY_CODE = re.compile(r"^[A-Za-z]{3}$")


def _signed_in_customer(tool_context: ToolContext) -> str | None:
    customer_id = tool_context.state.get("customer_id")
    return customer_id if isinstance(customer_id, str) and customer_id else None


async def login_customer(
    customer_id: str, pin: str, tool_context: ToolContext
) -> dict[str, str]:
    """Sign in to this fictional ATM demo with a customer ID and four-digit demo PIN."""
    result = banking.authenticate(customer_id, pin)
    if result["status"] == "success":
        tool_context.state["customer_id"] = result["customer_id"]
        tool_context.state["customer_name"] = result["name"]
    return result


async def check_balance(tool_context: ToolContext) -> dict[str, str]:
    """Show the signed-in demo customer's current INR account balance."""
    customer_id = _signed_in_customer(tool_context)
    return banking.balance(customer_id) if customer_id else {
        "status": "error", "message": "Please sign in first."
    }


async def deposit_cash(amount: str, tool_context: ToolContext) -> dict[str, str]:
    """Record a simulated INR cash deposit to the signed-in demo account."""
    customer_id = _signed_in_customer(tool_context)
    if not customer_id:
        return {"status": "error", "message": "Please sign in first."}
    try:
        return banking.deposit(customer_id, amount)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}


async def withdraw_cash(amount: str, tool_context: ToolContext) -> dict[str, str | int]:
    """Withdraw simulated INR cash; limited to ₹25,000 per withdrawal and ₹50,000 daily."""
    customer_id = _signed_in_customer(tool_context)
    if not customer_id:
        return {"status": "error", "message": "Please sign in first."}
    try:
        return banking.withdraw(customer_id, amount)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}


async def check_withdrawal_limits(tool_context: ToolContext) -> dict[str, str | int]:
    """Show the signed-in customer's per-withdrawal limit and remaining daily cash limit."""
    customer_id = _signed_in_customer(tool_context)
    return banking.withdrawal_limits(customer_id) if customer_id else {
        "status": "error", "message": "Please sign in first."
    }


async def transfer_money(
    recipient_customer_id: str, amount: str, tool_context: ToolContext
) -> dict[str, str]:
    """Transfer simulated INR to another demo customer after the user confirms both details."""
    customer_id = _signed_in_customer(tool_context)
    if not customer_id:
        return {"status": "error", "message": "Please sign in first."}
    try:
        return banking.transfer(customer_id, recipient_customer_id, amount)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}


async def get_transaction_history(
    tool_context: ToolContext, limit: int = 10
) -> dict[str, Any]:
    """Show up to 20 recent transactions from the signed-in demo account."""
    customer_id = _signed_in_customer(tool_context)
    return banking.history(customer_id, limit) if customer_id else {
        "status": "error", "message": "Please sign in first."
    }


async def update_pin(
    current_pin: str, new_pin: str, tool_context: ToolContext
) -> dict[str, str]:
    """Change the signed-in demo customer's PIN after verifying the current PIN."""
    customer_id = _signed_in_customer(tool_context)
    return banking.change_pin(customer_id, current_pin, new_pin) if customer_id else {
        "status": "error", "message": "Please sign in first."
    }


async def logout_customer(tool_context: ToolContext) -> dict[str, str]:
    """Sign out the current demo customer and clear their ADK session state."""
    tool_context.state.pop("customer_id", None)
    tool_context.state.pop("customer_name", None)
    return {"status": "success", "message": "You have been signed out."}


def _validate_rate_query(amount: str, base_currency: str, quote_currency: str) -> Decimal:
    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid amount.") from None
    if not decimal_amount.is_finite() or decimal_amount <= 0 or decimal_amount.as_tuple().exponent < -6:
        raise ValueError("Amount must be positive and have at most six decimal places.")
    if decimal_amount > MAX_REFERENCE_AMOUNT:
        raise ValueError("Amount is above the supported conversion limit.")
    for currency in (base_currency, quote_currency):
        if not _CURRENCY_CODE.fullmatch(currency):
            raise ValueError("Use three-letter ISO currency codes, such as INR and EUR.")
    if base_currency.upper() == quote_currency.upper():
        raise ValueError("Choose two different currencies.")
    return decimal_amount


def _normalize_rate_payload(
    payload: object, amount: Decimal, quote_currency: str
) -> dict[str, str]:
    """Whitelist numeric and date fields; never forward arbitrary MCP text to the LLM."""
    if not isinstance(payload, dict) or str(payload.get("currency", "")).upper() != quote_currency:
        raise RuntimeError("The reference-rate service returned an unexpected currency.")
    try:
        converted_amount = Decimal(str(payload["amount"]))
    except (KeyError, InvalidOperation, ValueError):
        raise RuntimeError("The reference-rate service returned an invalid amount.") from None
    if not converted_amount.is_finite() or converted_amount < 0:
        raise RuntimeError("The reference-rate service returned an invalid amount.")
    normalized = {
        "converted_amount": str(converted_amount),
        "quote_currency": quote_currency,
        "rate_for_one_base_unit": str(converted_amount / amount),
    }
    rate_date = payload.get("date")
    if isinstance(rate_date, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", rate_date):
        normalized["rate_date"] = rate_date
    return normalized


async def _call_frankfurter(
    amount: Decimal, base_currency: str, quote_currency: str
) -> dict[str, str]:
    """Call Frankfurter's read-only conversion tool and keep only validated rate fields."""
    async with streamable_http_client(FRANKFURTER_MCP_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "convert",
                arguments={
                    "amount": float(amount),
                    "from": base_currency.upper(),
                    "to": quote_currency.upper(),
                },
            )
    if getattr(result, "isError", False):
        raise RuntimeError("The reference-rate service returned an error.")
    payload = getattr(result, "structuredContent", None)
    if payload is None:
        text_blocks = [
            block.text for block in getattr(result, "content", [])
            if getattr(block, "type", None) == "text" and getattr(block, "text", None)
        ]
        if not text_blocks:
            raise RuntimeError("The reference-rate service returned no rate data.")
        try:
            payload = json.loads("\n".join(text_blocks))
        except json.JSONDecodeError:
            raise RuntimeError("The reference-rate service returned an unexpected response.") from None
    return _normalize_rate_payload(payload, amount, quote_currency)


async def get_reference_exchange_rate(
    amount: str, base_currency: str, quote_currency: str
) -> dict[str, str | float]:
    """Look up an informational currency conversion from the public Frankfurter MCP service.

    This uses published reference rates only. It does not exchange or transfer money,
    and the displayed rate may differ from a bank's actual rate or fees.
    """
    try:
        decimal_amount = _validate_rate_query(amount, base_currency, quote_currency)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    base_currency = base_currency.upper()
    quote_currency = quote_currency.upper()
    try:
        rate_result = await asyncio.wait_for(
            _call_frankfurter(decimal_amount, base_currency, quote_currency), timeout=15
        )
    except (TimeoutError, OSError, RuntimeError) as exc:
        return {
            "status": "error",
            "message": f"Reference rates are temporarily unavailable ({type(exc).__name__}).",
        }
    except Exception:
        # Keep transport/library details out of the conversation and logs.
        return {"status": "error", "message": "Reference rates are temporarily unavailable."}
    return {
        "status": "success",
        "source": "Frankfurter public MCP (reference rates)",
        "amount": str(decimal_amount),
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "reference_result": rate_result,
        "disclaimer": "Indicative reference rate only; this is not a bank quote or a money movement.",
    }
