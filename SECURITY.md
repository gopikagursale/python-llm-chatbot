# Security Review

## Overview

This project is a learning-focused Python chatbot that calls the OpenAI Responses API. It is intentionally lightweight and does not include user accounts, databases, or long-term persistence.

This repository is not production-secure by default. It is suitable for local development and educational use, but it still needs clear operational safeguards before broader or public deployment.

## API key handling

- API keys must be stored in environment variables or a local `.env` file.
- The project uses `OPENAI_API_KEY` and `OPENAI_MODEL` as configuration values.
- Keys must never be checked into source control.
- The repository excludes `.env` files and `.streamlit/secrets.toml` in `.gitignore`.
- Error messages must not print the raw key or include secret values.

## Environment configuration

Use a local `.env` file that looks like:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MODELS=gpt-4o-mini,gpt-4.1-mini
```

Only include placeholder values in `.env.example`.

## Data handling

- Chat history stays in Streamlit session state only.
- No database or permanent storage is used in this project.
- Analytics records do not include API keys or raw conversation bodies.
- Usage records intentionally store only token counts, timestamps, model IDs, and status metadata.

## Session memory limitations

- Conversation memory is in-memory only.
- Each browser session has its own Streamlit session state.
- New Chat resets the current session state intentionally.
- This is not durable memory and should not be treated as a production user profile system.

## API usage and cost considerations

- Model calls can create real billable usage.
- The project includes estimated cost metadata based on token counts.
- The cost calculations are estimates only and should never be treated as final billing records.
- Users should review model choice and avoid accidental expensive model selection in shared or paid environments.

## Known security limitations

- No authentication or authorization layer is implemented.
- No rate-limit enforcement beyond the upstream API provider.
- No auditing trail for user actions beyond the in-memory session.
- No secrets rotation process is automated.
- No deployment configuration is included for public hosting.

## Recommendations before public deployment

1. Add environment-variable enforcement in CI and local linting.
2. Keep `.env` and secret files outside version control.
3. Consider a secured deployment environment with secret management.
4. Add explicit rate limits and abuse protections.
5. Review which conversation data is safe to retain, if any.
6. Add clear data-retention and privacy notices before exposing the app externally.
