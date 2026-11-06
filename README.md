# AI Chatbot Project

This project is a milestone-based Python AI engineering learning app. It starts with a CLI chatbot, adds a Streamlit web UI, then adds conversation memory and model-selection/streaming features.

## Milestone status

- M1: Terminal chatbot complete.
- M2: Streamlit web chatbot complete.
- M3: Conversation memory complete.
- M4: Response streaming and model selection complete.
- M5: Token usage, response timing, and API cost tracking complete.

## Architecture

```text
User
  ↓
Streamlit UI
  ↓
Conversation Manager
  ↓
Shared LLM Service
  ↓
OpenAI Responses API
  ↓
Streaming events / final response
  ↓
Streamlit UI
```

## Project structure

```text
.
├── .env.example
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── PROJECT_SPEC.md
├── PROMPTS.md
├── README.md
├── LEARNING_NOTES.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── conversation_manager.py
│   ├── costs.py
│   ├── llm_client.py
│   └── usage_tracking.py
├── streamlit_app.py
├── tests/
│   ├── test_cli.py
│   ├── test_llm_client.py
│   ├── test_streamlit_app.py
│   ├── test_conversation_manager.py
│   └── test_usage_tracking.py
└── .venv/
```

## Setup

### 1) Create a virtual environment

macOS/Linux:

```bash
cd /path/to/ai-chatbot-project-1
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
cd C:\path\to\ai-chatbot-project-1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a local `.env` file or copy the example file:

```bash
cp .env.example .env
```

Example content:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MODELS=gpt-4o-mini,gpt-4.1-mini
```

## Run the terminal chatbot

```bash
python -m app.cli
```

## Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

Use the sidebar to:
- enable or disable streaming
- choose the active model from the configured list
- inspect the latest LLM request payload
- review usage and cost analytics
- export the request history as a CSV
- start a new conversation

## Streaming behavior

When streaming is enabled, the app sends the conversation history to the OpenAI Responses API with `stream=True` and reads text deltas as they arrive. The UI displays them progressively using `st.write_stream()`. The final assistant message is only appended after successful completion.

When streaming is disabled, the app uses the standard non-streaming `responses.create(...)` call and captures the final `response.output_text` once the API has finished.

## Model selection

The app reads the default model from `OPENAI_MODEL` and supports an optional `OPENAI_MODELS` comma-separated list. The sidebar dropdown uses that list while preserving the default model as the fallback choice.

## Usage and cost analytics

The app captures token usage from the OpenAI Responses API, including input, output, cached input, and reasoning tokens when available. The streamlit UI records response latency, time-to-first-token for streaming responses, and a simple estimated cost per model using model pricing metadata.

The analytics panel displays the latest totals and lets you export a CSV of the request history for review.

## Testing

Run offline tests without paid API calls:

```bash
source .venv/bin/activate
pytest -q
```

The test suite uses mocked OpenAI responses and validates:
- streaming delta handling
- non-streaming behavior
- conversation history context
- model switching
- New Chat reset behavior
- partial-stream failure handling
- usage metrics and cost estimation

## Security notes

- Never commit `.env`.
- Never print secrets in logs or UI messages.
- Keep live API usage deliberate and approved.

## Learning goals

This project helps you understand:
- prompt and response structure
- how inference differs from training
- how session state works in Streamlit
- how conversation history is passed to an LLM
- how streaming is useful for latency and progressive feedback
- why partial responses should not be treated as successful output

For deeper explanations, read [LEARNING_NOTES.md](LEARNING_NOTES.md).
