# Google ADK Demo ATM Agent

A small conversational ATM simulator built with Python and Google's Agent Development Kit (ADK). It demonstrates ADK function tools, per-session sign-in state, SQLite persistence, validation, transaction limits, and a read-only public MCP integration.

## Features

- Four-digit demo PIN authentication, PBKDF2-HMAC-SHA256 PIN hashes, and lockout after five failed attempts
- Balance inquiry, simulated cash deposits and withdrawals, and transfers between demo accounts
- Withdrawal safety limits: ₹25,000 per withdrawal and ₹50,000 per India calendar day (IST), enforced in the SQLite service layer
- Atomic balance changes and ledger entries with transaction IDs
- Recent transaction history, PIN changes, and sign-out
- Reference currency conversions via the public, read-only [Frankfurter MCP](https://mcp.frankfurter.dev/) service
- Strict tool input validation, ADK confirmation dialogs on every money-moving function, and agent guidance for privacy, untrusted MCP output, and demo-only actions
- Unit tests for account operations, validation, limits, session gating, and the MCP function-tool wrapper

## Requirements and setup

- Python 3.10+
- A Google AI Studio API key for Gemini
- `pip`

Open a terminal in this `ATM_AI_AGENT` directory and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GOOGLE_API_KEY` in `.env`, then start the ADK interface:

```powershell
adk web
```

Select `atm_agent` in the UI. First startup seeds two fictional accounts:

| Customer ID | Demo PIN | Starting balance |
| --- | --- | ---: |
| `100001` | `1234` | ₹2,500.00 |
| `100002` | `2345` | ₹1,000.00 |

Example prompts:

- “Sign in with customer ID 100001 and PIN 1234.”
- “What is my balance?”
- “Show my withdrawal limits.”
- “Withdraw ₹100.” The agent summarizes the simulated transaction, then ADK requires approval in a confirmation dialog before the function runs.
- “Transfer ₹100 to customer 100002.” The agent confirms the exact amount and recipient, then ADK requires approval before the function runs.
- “Convert 100 USD to INR using a reference rate.”
- “Show my recent transactions.”
- “Sign me out.”

The Frankfurter call is a read-only reference-rate lookup. The service requires no API key, but it depends on internet access and can be unavailable or rate limited. Its rate is not a bank quote, and the agent must not use it to perform or approve a transfer.

## Tests

Install test dependencies and run the suite from this directory:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

The unit tests use temporary SQLite databases and mock the MCP service; they do not need a Gemini key or live MCP access.

## Configuration and layout

`ATM_DB_PATH` optionally overrides the local SQLite database path. `.env`, SQLite databases, and Python caches are ignored by Git. Delete `atm_agent/atm_demo.db` while the app is stopped to reset the local demo accounts and transaction history.

```text
atm_agent/
  agent.py            # ADK root_agent, instruction guardrails, and tool registration
  function_tools.py   # ADK-callable ATM and Frankfurter MCP adapter functions
  banking.py          # SQLite storage, authentication, limits, validation, ledger
tests/
  test_banking.py
  test_function_tools.py
```

