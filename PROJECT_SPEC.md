# Project Specification: AI Chatbot with Conversation Memory

## Goal

Learn AI engineering fundamentals by constructing an understandable Python application that calls a pre-trained LLM, eventually gaining a web UI, conversation context, streaming, token tracking, cost estimates, and reliability tests.

## Technology

- Python >=3.11
- OpenAI official Python SDK, current Responses API
- python-dotenv for local secrets
- pytest with mocked SDK responses
- Streamlit starting in M2 (NOT needed for M1)
- No database, LangChain, vector database, or agent framework.

## Architecture (target)

User -> Streamlit UI -> Conversation manager -> LLM service -> OpenAI API -> Response -> UI + usage statistics.

For M1: User -> Python CLI -> LLM service -> OpenAI API -> terminal output.

## Functional requirements (eventual project)

1. Ask a question and see an AI response.
2. Conversational session history with follow-up question handling.
3. Clear session history.
4. Display generated output while it streams.
5. Select among specifically configured model identifiers.
6. Report actual usage where returned, and estimate costs from configurable current prices. Never invent missing usage data.
7. Show response time.
8. Validate empty inputs and handle API errors without exposing secrets.
9. Unit tests using fake or mocked API interactions; optional live smoke test only with explicit user intent.
10. Provide README, architecture explanation, and learning notes.

## Milestones

### M1: Terminal chatbot (START HERE)

Build only:
- Python terminal entry point that prompts for text until the user enters `exit`.
- OpenAI SDK integration with `client.responses.create` and `response.output_text`.
- `OPENAI_API_KEY` and `OPENAI_MODEL` from environment / `.env`.
- A helpful message when a key/model is missing; no secret leakage.
- Ignore blank input; handle API/network errors cleanly; Ctrl+C/EOF graceful shutdown.
- A small testable function or class for calling the model.
- At least 3 automated tests that mock the SDK (successful response, blank input behavior, API error handling).
- Setup instructions for macOS/Linux and Windows.

Explicitly out of M1: session memory, Streamlit, streaming, model switcher, price dashboard.

**M1 acceptance**: User can start the script, enter one question, read a model reply, ask another question, and exit; tests run offline without a real API key. A live smoke test remains a user action and may incur API charges.

### M2: Streamlit interface

Chat area, input form, working reply, clear status/error messages, minimal polished UI.

### M3: Conversation memory

Store session messages, send appropriate history to the model; verify follow-up question behavior; clear history; avoid unbounded context growth.

### M4: Streaming and model selection

Streaming UI and an explicit list of supported user-configured model IDs. Handle streaming interruption.

### M5: Observability

Token usage if reported, latency measurement, configurable price table, explicit 'unavailable' if missing, estimated (not exact) costs.

### M6: Reliability and documentation

Mock tests, edge cases, modularization, README, architecture, explanation of training vs inference and prompt/context limitations, deployment notes if appropriate.

## Learning questions to answer after M1

1. What is the difference between training a model and running inference?
2. What information is sent in an API request?
3. Why doesn't a stateless chatbot automatically remember a previous question?
4. What is an API key, and why must it stay secret?
5. How can tests run without making paid API calls?
6. what is LLM and how does it work and where is it used?
