# Support Ticket Intelligence

An end-to-end support triage demo that combines a transparent classical ML classifier with an optional LLM-generated analyst note.

The local model uses word and character TF-IDF features with logistic regression to rank six ticket categories. An OpenAI Responses API call can then turn the ticket and predicted category into a concise summary, evidence, and a suggested next step. The model prediction stays visible alongside the LLM output, and the LLM call is always a separate, explicit action.

## What it demonstrates

- Data preparation and a stratified train / validation split
- A scikit-learn text classification pipeline with class probabilities
- Reproducible evaluation metrics and a saved model artifact
- A Streamlit interface for trying examples or entering a demo ticket
- Optional server-side OpenAI Responses API integration
- Clear boundaries: the LLM note is a draft for human review, not an automated decision

## Requirements

- Python 3.10 or newer
- An OpenAI API key to use the optional LLM analysis button

The classifier and UI work without an API key. The sample dataset is synthetic and ships with the project.

## Run on Windows PowerShell

Open PowerShell in this project directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m ticket_triage.train
Copy-Item .env.example .env
```

To use the LLM feature, add your key to `.env`:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-6-astra
```

Keep `.env` private; it is excluded by `.gitignore`. The model name can be changed to another model available to your API project.

Start the application:

```powershell
python -m streamlit run src/ticket_triage/app.py
```

Choose a synthetic ticket or write a short example, click **Classify ticket**, then optionally click **Generate LLM triage note**. Without a key, category classification still works.

## Run on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m ticket_triage.train
cp .env.example .env
```

Add `OPENAI_API_KEY` and optionally `OPENAI_MODEL` to `.env`, then run:

```bash
python -m streamlit run src/ticket_triage/app.py
```

## Project structure

```text
Support_Ticket_Intelligence/
  data/sample_tickets.csv       # Synthetic labeled examples
  src/ticket_triage/
    app.py                      # Streamlit user interface
    llm.py                      # Optional OpenAI Responses API integration
    model.py                    # Prediction wrapper
    settings.py                 # Project paths and environment loading
    train.py                    # Training and held-out evaluation
  artifacts/                    # Generated model and metrics (gitignored)
```

## Model and evaluation notes

Run `python -m ticket_triage.train` to print accuracy, macro F1, and a per-category report, then save the trained pipeline and metrics under `artifacts/`. The included data is intentionally small and synthetic so the demo is self-contained; evaluation scores are not evidence of production performance. Replace it with a suitably licensed, representative, de-identified dataset before drawing conclusions.

## LLM and data handling

The LLM call sends the entered ticket text, predicted label, and model confidence to the OpenAI API. Use synthetic or non-sensitive text in this demo; do not paste real customer details. Ticket text is treated as untrusted input, and the generated note must not make policy, refund, or eligibility decisions. A human should review any draft before using it.

The integration uses the OpenAI Python SDK and the Responses API, following the [official text-generation guide](https://developers.openai.com/api/docs/guides/text?lang=python).
