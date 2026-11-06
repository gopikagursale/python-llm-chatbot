import time

from openai import OpenAI

from app.usage_tracking import UsageMetrics


def _build_request_payload(prompt, conversation_history=None):
    if conversation_history is not None:
        payload = [dict(item) for item in conversation_history]
        if not payload:
            raise ValueError("Prompt cannot be empty.")
        return payload

    if prompt is None or not str(prompt).strip():
        raise ValueError("Prompt cannot be empty.")
    return prompt


def generate_response(
    prompt: str,
    api_key: str,
    model: str,
    conversation_history=None,
    return_details: bool = False,
):
    payload = _build_request_payload(prompt, conversation_history)

    if not api_key or not model:
        raise RuntimeError("Missing OPENAI_API_KEY or OPENAI_MODEL configuration.")

    try:
        client = OpenAI(api_key=api_key)
        if conversation_history is None:
            response = client.responses.create(model=model, input=prompt)
        else:
            try:
                response = client.responses.create(model=model, input=payload, store=False)
            except TypeError as exc:
                if "store" not in str(exc):
                    raise
                response = client.responses.create(model=model, input=payload)
        output_text = response.output_text
        if return_details:
            return output_text, response
        return output_text
    except Exception as exc:
        raise RuntimeError(
            "OpenAI request failed. Check your API key, model, and network connection."
        ) from exc


def generate_response_with_metadata(prompt: str, api_key: str, model: str, conversation_history=None):
    start = time.perf_counter()
    output_text, response = generate_response(
        prompt,
        api_key,
        model,
        conversation_history=conversation_history,
        return_details=True,
    )
    latency = time.perf_counter() - start
    usage = UsageMetrics.from_response(response)
    return {
        "text": output_text,
        "response": response,
        "usage": usage,
        "latency_seconds": latency,
        "completed": True,
    }


def stream_response(prompt: str, api_key: str, model: str, conversation_history=None):
    result = stream_response_with_metadata(prompt, api_key, model, conversation_history=conversation_history)
    for chunk in result["chunks"]:
        yield chunk


def stream_response_with_metadata(prompt: str, api_key: str, model: str, conversation_history=None):
    payload = _build_request_payload(prompt, conversation_history)

    if not api_key or not model:
        raise RuntimeError("Missing OPENAI_API_KEY or OPENAI_MODEL configuration.")

    client = OpenAI(api_key=api_key)
    start = time.perf_counter()
    first_delta_time = None
    collected_chunks = []
    completed_response = None

    try:
        if conversation_history is None:
            stream = client.responses.create(model=model, input=prompt, stream=True, store=False)
        else:
            try:
                stream = client.responses.create(model=model, input=payload, stream=True, store=False)
            except TypeError as exc:
                if "store" not in str(exc):
                    raise
                stream = client.responses.create(model=model, input=payload, stream=True)
    except TypeError as exc:
        if "stream" not in str(exc):
            raise RuntimeError(
                "OpenAI request failed. Check your API key, model, and network connection."
            ) from exc
        try:
            response = client.responses.create(
                model=model,
                input=payload if conversation_history is not None else prompt,
                store=False,
            )
        except TypeError:
            response = client.responses.create(
                model=model,
                input=payload if conversation_history is not None else prompt,
            )
        text = response.output_text
        return {
            "text": text,
            "chunks": [text],
            "response": response,
            "usage": UsageMetrics.from_response(response),
            "latency_seconds": time.perf_counter() - start,
            "time_to_first_text_delta": None,
            "completed": True,
        }
    except Exception as exc:
        raise RuntimeError(
            "OpenAI request failed. Check your API key, model, and network connection."
        ) from exc

    completed = False
    for event in stream:
        event_type = getattr(event, "type", None) or (event.get("type") if isinstance(event, dict) else None)
        if event_type == "response.output_text.delta":
            delta = getattr(event, "delta", None)
            if delta is None and isinstance(event, dict):
                delta = event.get("delta")
            if delta is not None:
                text = str(delta)
                if first_delta_time is None:
                    first_delta_time = time.perf_counter() - start
                collected_chunks.append(text)
        elif event_type in {"response.failed", "response.incomplete"}:
            raise RuntimeError("OpenAI streaming response failed before completion.")
        elif event_type == "error":
            message = (
                getattr(event, "message", None)
                or (event.get("message") if isinstance(event, dict) else None)
                or "OpenAI streaming error."
            )
            raise RuntimeError(f"OpenAI streaming error: {message}")
        elif event_type == "response.completed":
            completed_response = event.response
            completed = True

    if not completed:
        raise RuntimeError("OpenAI streaming response did not complete successfully.")

    return {
        "text": "".join(collected_chunks),
        "chunks": list(collected_chunks),
        "response": completed_response,
        "usage": UsageMetrics.from_response(completed_response),
        "latency_seconds": time.perf_counter() - start,
        "time_to_first_text_delta": first_delta_time,
        "completed": True,
    }
