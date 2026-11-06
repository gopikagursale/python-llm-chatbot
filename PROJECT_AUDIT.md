# Project Audit — M1 to M5

## 1. Current application architecture

The project is a small Python AI chatbot built in layers:

1. User interaction layer
   - Terminal CLI in `app/cli.py`
   - Streamlit interface in `streamlit_app.py`
2. Conversation layer
   - `app/conversation_manager.py` builds and preserves message history
3. LLM integration layer
   - `app/llm_client.py` sends requests to the OpenAI Responses API
4. Configuration layer
   - `app/config.py` loads environment variables and available model IDs
5. Observability layer
   - `app/usage_tracking.py` extracts token usage
   - `app/costs.py` estimates model-specific spend
6. UI analytics layer
   - `streamlit_app.py` renders chat, sidebar controls, usage data, and CSV export

The design is intentionally simple and educational: separate service logic from UI logic while keeping the app easy to trace.

## 2. Existing functionality

### Implemented milestones
- M1: terminal chatbot with OpenAI Responses API call
- M2: Streamlit interface with chat messages and display logic
- M3: per-session conversation history and context inspection
- M4: streaming mode and model selection
- M5: token usage, response timing, and estimated API costs

### Functional checks currently supported
- Chat request to OpenAI model via official SDK
- Empty input validation
- Fancy but lightweight Streamlit sidebar controls
- Model selection via `OPENAI_MODEL` and optional `OPENAI_MODELS`
- New Chat reset behavior
- Streamed answer rendering
- Error handling for missing config and failed model requests
- Request-level usage statistics and CSV export

## 3. Current test results

Baseline verification run:

- Command: `source .venv/bin/activate && python -m pytest -q`
- Result: 21 passed in 0.43s

The current test suite is green, but it is still largely mock-based and does not represent a live API smoke test.

## 4. Identified bugs and issues

### Confirmed strengths
- The session-state widget bug has been addressed.
- The project remains stable under the mock test suite.
- The app clearly separates conversation logic from UI logic.

### Remaining concerns
1. There is no formal GitHub Actions workflow yet.
2. There is no security review file or architecture/design review file yet.
3. The project does not yet include a coverage gate or Ruff configuration.
4. The repository still contains a prompt file that should be excluded from GitHub publication.
5. There is no explicit final acceptance report for M6 tasks.
6. The app assumes model pricing metadata is present and reasonably consistent but does not enforce a pricing source record in code.
7. Some late-stage code still keeps logic tightly grouped in the Streamlit file, which could be split further for maintainability.

## 5. Security risks

### Low-risk but real concerns
- Secret handling depends on `.env` and environment variables, which is acceptable when `.env` is excluded.
- The project should explicitly document that `.env` and `.streamlit/secrets.toml` must never be checked into Git.
- The UI is not storing raw prompts or API keys in analytics records, which is good.
- Logs should continue to avoid printing secrets or full user conversations.

### Security actions still needed
- Add a dedicated security review document.
- Confirm `.gitignore` excludes secrets and generated artifacts.
- Add CI checks so secret-bearing paths are not accidentally committed.
- Document the fact that this is not production-secure by default.

## 6. Missing tests

The project already covers the main happy path and selected model-state bug, but the real M6 audit still calls for a more thorough set:

- CLI path: empty input, exit command, API failure, keyboard interrupts
- LLM client: authentication, rate limit, network errors, missing response data
- Conversation manager: per-session isolation, failed-request preservation, chronological order
- Streaming: interrupted stream handling and duplicate-message prevention
- Analytics: CSV export, session totals, model pricing edge cases
- UI: AppTest coverage for sidebar interactions where supported

## 7. Documentation gaps

The project includes a useful README and learning notes, but it still lacks the formal final-review artifacts required for a polished portfolio handoff:

- `SECURITY.md`
- `ARCHITECTURE.md`
- `PROJECT_REVIEW.md`
- `FINAL_TEST_REPORT.md`
- `PROJECT_AUDIT.md`
- GitHub CI workflow

## 8. Proposed improvements

1. Add repository-level automation with Ruff and coverage checks.
2. Finalize the security policy and environment-secrets documentation.
3. Add a more explicit M6 final review report rather than relying only on the current test suite.
4. Formalize the architecture documentation with a Mermaid diagram.
5. Keep the app as a learning project: simple, readable, and testable, without introducing unnecessary frameworks.

## 9. Overall assessment

The application is in a good state for a learning-focused milestone project: it works under mocked tests, the architecture is understandable, and the key AI-engineering concepts are implemented. The next step is to finish the final engineering review artifacts and prepare the repository for GitHub with correct security and CI guardrails.
