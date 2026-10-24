# Engineering Review Agent

A Google Agent Development Kit (ADK) assistant for reviewing a pasted unified Git diff. It combines a deterministic Python pre-scan with Gemini's contextual review to surface concrete correctness, security, data-integrity, and reliability concerns. It offers recommendations only: it never edits a checkout, runs reviewed code, approves a PR, or merges changes.

## Capabilities

- Uses a Google ADK `Agent` and a local Python function tool.
- Reports changed paths, inserted line count, sensitive-area paths, and heuristic signals for secret-like additions or destructive operations.
- Redacts secret-like values in the deterministic scan output.
- Instructs the model to treat diff content as untrusted, cite exact changed lines, avoid invented findings, and distinguish observations from uncertainty.
- Keeps a human responsible for deciding whether findings are valid and what to change.

## Run locally

Prerequisites: Python 3.11+ and a Google AI Studio API key.

From a terminal at the repository root:

```powershell
cd Engineering_Review_Agent
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

Edit `.env` and set `GOOGLE_API_KEY` to your own key. Then launch the ADK development UI:

```powershell
adk web
```

Open the local URL shown in the terminal and select `review_agent`. Paste a focused unified diff and, when useful, describe the expected behavior, relevant constraints, and language/framework. Avoid including live credentials, customer data, or confidential source code in prompts.

On macOS or Linux, use `python3 -m venv .venv`, `source .venv/bin/activate`, and `cp .env.example .env`; the remaining commands are the same.

## How the tool scans a diff

The local `inspect_diff` tool does not call a model and has no filesystem or network access. It scans added lines in the supplied unified diff and returns a JSON summary. Secret detection is heuristic and omits the matched value. Destructive-operation checks are also heuristic; they can miss risks or flag harmless text. The tool output is a starting point for review, not proof that a change is safe or unsafe.

## Configuration

- `GOOGLE_API_KEY`: required for Gemini-backed reviews.
- `REVIEW_AGENT_MODEL`: optional model override; defaults to `gemini-3.8-flash`.

## Source

[Project folder in this repository](https://github.com/pavan9753/AI-agent-work-and-coding-profiles/tree/main/Engineering_Review_Agent)
