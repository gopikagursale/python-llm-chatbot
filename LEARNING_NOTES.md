# Learning Notes — M1 to M5

## 1. What is LLM response streaming?

Streaming means the model starts returning text before it has finished the entire answer. Instead of waiting for one large response, the app receives incremental chunks and displays them in near real time.

Example pattern:

```python
stream = client.responses.create(
    model="gpt-4o-mini",
    input="Explain recursion simply.",
    stream=True,
    store=False,
)
```

The app then reads events from the stream and updates the UI progressively.

## 2. What are Server-Sent Events?

Server-Sent Events (SSE) are a simple HTTP streaming format where the server pushes updates to the client over one connection. The OpenAI Responses API uses chunks of event data to communicate progress and text output. In a Python app, we usually consume those events as an iterable stream.

## 3. What is a text delta?

A text delta is a small piece of output text delivered in a chunk. For example, a model might emit:

```python
"The"
" model"
" predicts"
" the next token."
```

Each fragment is a delta. The app concatenates these deltas to form the final answer.

## 4. How does streaming differ from a normal API response?

A normal response waits for the entire model output to finish, then returns one final object. Streaming shows incremental progress while generation is still happening.

Normal flow:

```python
response = client.responses.create(...)
answer = response.output_text
```

Streaming flow:

```python
for event in client.responses.create(..., stream=True):
    if event.type == "response.output_text.delta":
        print(event.delta)
```

This is useful for chat UIs because it feels faster and more natural to the user.

## 5. How does `st.write_stream()` work?

`st.write_stream()` accepts an iterable of strings or message chunks and writes them in order as they arrive. It is designed for streaming chat responses in Streamlit apps.

Example:

```python
for delta in stream_response(...):
    yield delta

st.write_stream(stream_chunks())
```

The function displays the text progressively without waiting for the full answer to complete.

## 6. How are selected models passed to the API?

The UI stores the selected model in Streamlit session state, then passes that value to the shared LLM service. The service calls:

```python
client.responses.create(model=selected_model, input=request_payload)
```

The model is not hardcoded in the UI. It comes from the environment and the optional `OPENAI_MODELS` list, which keeps the app flexible and easy to configure.

## 7. How are streaming responses saved into conversation history?

The app builds a request payload from the current conversation messages, sends it to the model, and only appends the final assistant message to the saved history after success. This keeps the conversation timeline accurate.

Example payload:

```python
[
    {"role": "user", "content": "My name is Sarah."},
    {"role": "assistant", "content": "Hi Sarah!"},
    {"role": "user", "content": "What is my name?"},
]
```

## 8. Why should partial responses not be treated as complete?

If the stream fails halfway through, the user may see some text already displayed, but that text is not reliable as a finished answer. If we save it as a complete assistant message, the history becomes inaccurate and confusing.

This is why the app keeps temporary displayed text separate from persisted conversation history until the stream finishes successfully.

## 9. How do model capabilities differ?

Different models may have different strengths:
- some are optimized for general chat
- some are better for reasoning or larger context windows
- some may not accept the same parameters or may have different rate limits

The app lets the user choose a configured model but does not assume all models are interchangeable. It validates the selected model and surfaces a useful error when a model is unavailable.

## 10. What is usage tracking in the Responses API?

The OpenAI Responses API includes `response.usage`, which gives you token counts for the request. In practice, we usually inspect fields such as:

```python
response.usage.input_tokens
response.usage.output_tokens
response.usage.total_tokens
response.usage.input_tokens_details.cached_tokens
response.usage.output_tokens_details.reasoning_tokens
```

This lets the app estimate how much work the model did and how much each call likely cost.

## 11. Why do we measure latency and time-to-first-token?

Response latency tells us how long the app took to receive the final answer. Time-to-first-token (TTFT) is more specific for streaming: it measures how quickly the user sees the first visible text from the model.

That is a useful metric because it captures the perceived responsiveness of the app, even if the total answer takes longer to finish.

## 12. How do we estimate API cost?

We can assign a pricing table to each model, such as dollars per 1M tokens for input and output. Then the app multiplies the token counts by those unit prices and adds cached-token pricing when relevant.

Example idea:

```python
cost = (input_tokens * input_price_per_million) / 1_000_000
```

This is a simple but useful estimate for monitoring usage during experimentation and deployment.

## 13. How do we test streaming vs non-streaming behavior?

We use mocked OpenAI responses. The tests verify that:
- streaming mode yields text deltas in order
- non-streaming mode still returns a final output string
- conversation history is included in the request
- switching models does not erase user history
- interruption errors do not save partial results

## Example: single-turn vs multi-turn requests

Single-turn:

```python
[
    {"role": "user", "content": "Tell me a joke."}
]
```

Multi-turn:

```python
[
    {"role": "user", "content": "My name is Sarah."},
    {"role": "assistant", "content": "Nice to meet you, Sarah!"},
    {"role": "user", "content": "What is my name?"},
]
```

The second request gives the model enough context to answer correctly without requiring a separate memory system.

## Example: usage analytics record

```python
{
    "model": "gpt-4o-mini",
    "input_tokens": 1200,
    "output_tokens": 300,
    "total_tokens": 1500,
    "latency_seconds": 1.42,
    "estimated_cost": "0.000725",
}
```

These records are collected in session state and can be exported to CSV from the sidebar panel.

## Architecture summary

```text
Streamlit UI
    ↓
Conversation Manager
    ↓
Shared LLM Service
    ↓
OpenAI Responses API
    ↓
Streaming events / final output
    ↓
UI state + conversation history
```

This separation keeps the UI focused on display and interaction, while the service stays responsible for LLM requests and the manager stays responsible for message ordering.

## Beginner-friendly takeaway

Think of the chatbot as a layered system:
- the UI is the front desk,
- the conversation manager keeps notes,
- the model service sends the request,
- the API returns text that gets displayed.

Streaming simply means the notes arrive while the answer is still being generated, rather than only at the very end.
