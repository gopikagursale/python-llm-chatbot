import csv
import io
import time

import streamlit as st

from app.config import load_model_options, load_settings
from app.conversation_manager import ConversationManager
from app.costs import estimate_cost
from app.llm_client import generate_response, generate_response_with_metadata, stream_response_with_metadata
from app.usage_tracking import UsageMetrics


def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_context" not in st.session_state:
        st.session_state.llm_context = []
    if "enable_streaming" not in st.session_state:
        st.session_state.enable_streaming = True
    if "usage_history" not in st.session_state:
        st.session_state.usage_history = []
    if "last_usage" not in st.session_state:
        st.session_state.last_usage = None

    api_key, model = load_settings()
    available_models = load_model_options(model)
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = model or (available_models[0] if available_models else "")
    elif st.session_state.selected_model not in available_models:
        st.session_state.selected_model = model or (available_models[0] if available_models else "")


def render_chat_history():
    initialize_chat_history()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def clear_conversation():
    initialize_chat_history()
    st.session_state.messages = []
    st.session_state.llm_context = []
    st.session_state.usage_history = []
    st.session_state.last_usage = None


def _build_usage_record(
    model_id,
    response=None,
    usage=None,
    latency_seconds=0.0,
    ttft_seconds=None,
    status="completed",
    error_category=None,
    streaming_enabled=False,
):
    metrics = (
        UsageMetrics.from_response(response)
        if response is not None
        else (usage or UsageMetrics())
    )
    cost = estimate_cost(model_id, metrics)
    return {
        "model": model_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "status": status,
        "streaming": streaming_enabled,
        "input_tokens": metrics.input_tokens,
        "output_tokens": metrics.output_tokens,
        "total_tokens": metrics.total_tokens,
        "cached_input_tokens": metrics.cached_input_tokens,
        "reasoning_tokens": metrics.reasoning_tokens,
        "latency_seconds": round(float(latency_seconds), 3) if latency_seconds is not None else None,
        "time_to_first_text_delta_seconds": round(float(ttft_seconds), 3) if ttft_seconds is not None else None,
        "estimated_cost": str(cost) if cost is not None else "Unavailable",
        "error_category": error_category,
    }


def render_usage_analytics():
    initialize_chat_history()
    if hasattr(st, "subheader"):
        st.subheader("Usage & Analytics")
    records = st.session_state.get("usage_history", [])
    if not records:
        if hasattr(st, "caption"):
            st.caption("No usage data yet.")
        else:
            st.write("No usage data yet.")
        return

    latest = records[-1]
    total_requests = len(records)
    completed = sum(1 for record in records if record["status"] == "completed")
    failed = total_requests - completed

    totals = {
        "input_tokens": sum(record["input_tokens"] for record in records),
        "output_tokens": sum(record["output_tokens"] for record in records),
        "total_tokens": sum(record["total_tokens"] for record in records),
    }

    if hasattr(st, "columns"):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Input tokens", totals["input_tokens"])
        col2.metric("Output tokens", totals["output_tokens"])
        col3.metric("Total tokens", totals["total_tokens"])
        col4.metric("Completed", completed)
    else:
        st.write({
            "input_tokens": totals["input_tokens"],
            "output_tokens": totals["output_tokens"],
            "total_tokens": totals["total_tokens"],
            "completed": completed,
            "failed": failed,
        })

    st.write("Last response:")
    st.json({
        "input_tokens": latest["input_tokens"],
        "output_tokens": latest["output_tokens"],
        "total_tokens": latest["total_tokens"],
        "cached_input_tokens": latest["cached_input_tokens"],
        "reasoning_tokens": latest["reasoning_tokens"],
        "latency_seconds": latest["latency_seconds"],
        "time_to_first_text_delta_seconds": latest["time_to_first_text_delta_seconds"],
        "estimated_cost": latest["estimated_cost"],
    })

    csv_buffer = io.StringIO()
    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=[
            "timestamp",
            "model",
            "status",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "latency_seconds",
            "estimated_cost",
        ],
    )
    writer.writeheader()
    for record in records:
        writer.writerow({
            "timestamp": record["timestamp"],
            "model": record["model"],
            "status": record["status"],
            "input_tokens": record["input_tokens"],
            "output_tokens": record["output_tokens"],
            "total_tokens": record["total_tokens"],
            "latency_seconds": record["latency_seconds"],
            "estimated_cost": record["estimated_cost"],
        })
    if hasattr(st, "download_button"):
        st.download_button("Export usage CSV", csv_buffer.getvalue(), file_name="usage_history.csv", mime="text/csv")

    if hasattr(st, "dataframe"):
        st.dataframe(
            [{
                "timestamp": record["timestamp"],
                "model": record["model"],
                "status": record["status"],
                "input_tokens": record["input_tokens"],
                "output_tokens": record["output_tokens"],
                "total_tokens": record["total_tokens"],
                "latency_seconds": record["latency_seconds"],
                "estimated_cost": record["estimated_cost"],
            } for record in records],
            use_container_width=True,
        )


def render_sidebar():
    initialize_chat_history()
    st.session_state.enable_streaming = st.sidebar.checkbox("Enable Streaming", value=st.session_state.enable_streaming)

    _, default_model = load_settings()
    available_models = load_model_options(default_model)
    if available_models:
        current_index = 0
        if st.session_state.selected_model in available_models:
            current_index = available_models.index(st.session_state.selected_model)

        selected_model = st.sidebar.selectbox(
            "Select AI Model",
            options=available_models,
            index=current_index,
            key="selected_model",
        )
        st.sidebar.caption(f"Selected model: {selected_model}")
    else:
        st.sidebar.caption("No available AI models configured.")

    st.sidebar.button("New Chat", on_click=clear_conversation)

    with st.sidebar.expander("View LLM Context", expanded=False):
        if st.session_state.llm_context:
            st.json(st.session_state.llm_context)
        else:
            st.write("No recent model context.")

    render_usage_analytics()


def handle_user_message(user_input: str, generate_response_fn=None, stream_response_fn=None):
    if generate_response_fn is None:
        generate_response_fn = generate_response
    if stream_response_fn is None:
        stream_response_fn = stream_response_with_metadata

    initialize_chat_history()
    text = (user_input or "").strip()

    if not text:
        st.warning("Please enter a message before sending.")
        return

    api_key, model = load_settings()
    if not api_key or not model:
        st.error("Missing OpenAI configuration. Set OPENAI_API_KEY and OPENAI_MODEL in your environment or .env file.")
        return

    available_models = load_model_options(model)
    selected_model = st.session_state.get("selected_model") or model
    if selected_model not in available_models:
        st.error(f"Selected model '{selected_model}' is unavailable. Choose one of: {', '.join(available_models)}")
        return

    manager = ConversationManager(st.session_state.messages)
    request_history = manager.build_request(text)
    st.session_state.llm_context = request_history

    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.markdown(text)

    start_time = time.perf_counter()
    usage_record = None
    try:
        if st.session_state.get("enable_streaming", True):
            with st.spinner("AI is thinking..."):
                result = stream_response_fn(text, api_key, selected_model, conversation_history=request_history)
                reply = result["text"]
                if not reply:
                    raise ValueError("Streaming response was empty.")

            with st.chat_message("assistant"):
                if hasattr(st, "write_stream"):
                    st.write_stream(result["chunks"])
                else:
                    for chunk in result["chunks"]:
                        st.markdown(chunk)

            usage_record = _build_usage_record(
                selected_model,
                response=result.get("response"),
                latency_seconds=time.perf_counter() - start_time,
                ttft_seconds=result.get("time_to_first_text_delta"),
                status="completed",
                streaming_enabled=True,
            )
        else:
            with st.spinner("AI is thinking..."):
                result = generate_response_with_metadata(
                    text,
                    api_key,
                    selected_model,
                    conversation_history=request_history,
                )
                reply = result["text"]

            with st.chat_message("assistant"):
                st.markdown(reply)

            usage_record = _build_usage_record(
                selected_model,
                response=result.get("response"),
                latency_seconds=result.get("latency_seconds", time.perf_counter() - start_time),
                status="completed",
                streaming_enabled=False,
            )
    except Exception as exc:
        if st.session_state.get("enable_streaming", True):
            st.warning("The response was interrupted before completion. The partial output was not saved.")
        st.error("Sorry, I couldn't get a response right now. Please check your API configuration and try again.")
        usage_record = _build_usage_record(
            selected_model,
            usage=UsageMetrics(),
            latency_seconds=time.perf_counter() - start_time,
            status="failed",
            error_category=type(exc).__name__,
            streaming_enabled=st.session_state.get("enable_streaming", True),
        )
        st.session_state.usage_history.append(usage_record)
        st.session_state.last_usage = usage_record
        return

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.last_usage = usage_record
    st.session_state.usage_history.append(usage_record)


def main():
    st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
    st.title("AI Chatbot")
    st.caption("Powered by OpenAI")

    render_sidebar()
    render_chat_history()

    user_input = st.chat_input("Type your message here...")
    if user_input is not None:
        handle_user_message(user_input)


if __name__ == "__main__":
    main()
