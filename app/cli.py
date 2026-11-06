from app.config import load_settings
from app.llm_client import generate_response


def chat_loop(
    input_func=input,
    output_func=print,
    generate_response_fn=None,
    api_key=None,
    model=None,
):
    if generate_response_fn is None:
        generate_response_fn = generate_response

    while True:
        try:
            user_input = input_func("You: ").strip()
        except KeyboardInterrupt:
            output_func("\nGoodbye!")
            break

        if not user_input:
            output_func("Please enter a message or type 'exit' to quit.")
            continue

        if user_input.lower() == "exit":
            output_func("Goodbye!")
            break

        try:
            reply = generate_response_fn(user_input, api_key, model)
        except Exception:
            output_func(
                "Sorry, I couldn't get a response right now. Please check your "
                "API configuration and try again."
            )
            continue

        output_func(f"Assistant: {reply}")


def main():
    api_key, model = load_settings()

    if not api_key or not model:
        print("Missing OpenAI configuration. Set OPENAI_API_KEY and OPENAI_MODEL in your environment or .env file.")
        return 1

    chat_loop(input_func=input, output_func=print, generate_response_fn=generate_response, api_key=api_key, model=model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
