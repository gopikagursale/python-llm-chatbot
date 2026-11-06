from app.cli import chat_loop


def test_chat_loop_ignores_blank_input_and_exits():
    prompts = ["", "Hi there", "exit"]
    outputs = []

    def fake_input(prompt_text=""):
        return prompts.pop(0)

    def fake_output(text):
        outputs.append(text)

    def fake_generate_response(prompt, api_key, model):
        assert prompt == "Hi there"
        assert api_key == "demo-key"
        assert model == "gpt-4o-mini"
        return "Hello from the model"

    chat_loop(
        input_func=fake_input,
        output_func=fake_output,
        generate_response_fn=fake_generate_response,
        api_key="demo-key",
        model="gpt-4o-mini",
    )

    assert any("Please enter a message" in item for item in outputs)
    assert any("Assistant: Hello from the model" in item for item in outputs)
    assert any("Goodbye!" in item for item in outputs)


def test_chat_loop_handles_keyboard_interrupt():
    outputs = []

    def fake_input(prompt_text=""):
        raise KeyboardInterrupt

    def fake_output(text):
        outputs.append(text)

    chat_loop(input_func=fake_input, output_func=fake_output, api_key="demo-key", model="gpt-4o-mini")

    assert any("Goodbye!" in item for item in outputs)
