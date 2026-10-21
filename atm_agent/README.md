# Google ADK Demo ATM Agent

A small conversational ATM agent built with Python and Google's Agent Development Kit (ADK). It demonstrates tool calling, per-session sign-in state, parameter validation, SQLite persistence, and transaction recording.

> **Demo only.** This project simulates fictional INR accounts in a local SQLite database. It is not connected to a bank, does not accept real cash, and is not suitable for real financial use. The demo PIN is entered into the agent conversation; never use real banking credentials or personal financial data with it.

## Features

- Demo customer sign-in with a four-digit PIN, PBKDF2-HMAC-SHA256 PIN hashes, and lockout after five incorrect attempts
- Balance inquiry
- Simulated cash deposits and withdrawals, with non-negative balance enforcement
- Transfers between demo accounts, with atomic balance updates and ledger entries
- Recent transaction history
- PIN change and sign-out
- SQLite persistence; balances are stored as integer paise to avoid floating-point accounting errors
- Agent instructions require explicit confirmation before withdrawals and transfers

## Requirements

- Python 3.10+
- Google AI Studio API key for Gemini
- `pip` (or `uv`)

## Run locally

From this project directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your Google AI Studio key to `.env` as `GOOGLE_API_KEY=...`, then start the ADK web interface:

```powershell
adk web
```

Choose `atm_agent` in the interface. On first start it creates `atm_agent/atm_demo.db` with two demo accounts:

| Customer ID | PIN | Starting balance |
| --- | --- | ---: |
| `100001` | `1234` | ₹2,500.00 |
| `100002` | `2345` | ₹1,000.00 |

You can reset local demo data by stopping the server and deleting `atm_agent/atm_demo.db`.

## Example prompts

- “Sign in with customer ID 100001 and PIN 1234.”
- “What is my balance?”
- “Deposit ₹250.”
- “Withdraw ₹100.” (The agent should ask you to confirm first.)
- “Transfer ₹100 to customer 100002.”
- “Show my recent transactions.”
- “Change my PIN from 1234 to 5678.”
- “Sign me out.”

## Configuration

`ATM_DB_PATH` optionally overrides the SQLite database path. Do not commit `.env` files or `atm_demo.db`; both are ignored by Git.

## Project layout

```text
atm_agent/
  __init__.py
  __main__.py       # Initialize demo data: python -m atm_agent
  agent.py          # ADK root_agent and tool functions
  banking.py        # SQLite operations and validation
```

## Notes

This is an educational sample, not a production ATM design. A production service needs a trusted authentication surface outside the LLM conversation, strong identity and authorization controls, audit and fraud monitoring, secure secret handling, operational safeguards, and integration with regulated banking infrastructure.
