# Instructions for Codex (and other agents that read AGENTS.md)

Read `PROJECT_SPEC.md` and `PROMPTS.md` before changing code.

You are building a Python AI engineering learning project. Prefer simple architecture and incremental milestones.

- Follow **only** the milestone the user requests. The current milestone is **M1**.
- Use Python >=3.11, the official OpenAI Python SDK, and the current Responses API (`client.responses.create`).
- Avoid obsolete Assistants API, LangChain, agent frameworks, and unnecessary complexity.
- Do not fabricate working API connectivity or test results.
- Treat `.env` as secret and keep it out of version control; provide `.env.example` with placeholders only.
- Do not expose API keys in code, logs, screenshots, or error messages.
- Tests must use mocks, not live paid API requests.
- Run tests if possible and report exactly what passed or was blocked.
- Ask before installing large dependencies, incurring API costs, or taking destructive actions.
- Explain significant design decisions and provide run commands.
- Maintain README and LEARNING_NOTES.md after implementing milestones.
- For M1, build a terminal chatbot only; conversation memory is reserved for M3.
