from app.llm_client import generate_response, stream_response


class DummyResponse:
    def __init__(self, output_text):
        self.output_text = output_text


def test_generate_response_success(monkeypatch):
    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key

        class responses:
            @staticmethod
            def create(model, input):
                assert model == "gpt-4o-mini"
                assert input == "Explain AI in one sentence."
                return DummyResponse("AI is a system that learns patterns from data.")

    monkeypatch.setattr("app.llm_client.OpenAI", DummyClient)

    result = generate_response("Explain AI in one sentence.", "test-key", "gpt-4o-mini")

    assert result == "AI is a system that learns patterns from data."


def test_generate_response_error_raises_runtime_error(monkeypatch):
    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key

        class responses:
            @staticmethod
            def create(model, input):
                raise RuntimeError("API failure")

    monkeypatch.setattr("app.llm_client.OpenAI", DummyClient)

    try:
        generate_response("Hello", "test-key", "gpt-4o-mini")
        assert False, "Expected RuntimeError to be raised"
    except RuntimeError as exc:
        assert "OpenAI request failed" in str(exc)


def test_stream_response_yields_text_deltas(monkeypatch):
    class DummyDeltaEvent:
        def __init__(self, delta):
            self.type = "response.output_text.delta"
            self.delta = delta

    class DummyCompletedEvent:
        def __init__(self):
            self.type = "response.completed"
            self.response = DummyResponse("Hello there")

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key

        class responses:
            @staticmethod
            def create(model, input, stream=False, store=False):
                assert stream is True
                assert store is False
                assert model == "gpt-4o-mini"
                assert input == [{"role": "user", "content": "Hello"}]
                return [DummyDeltaEvent("Hello "), DummyDeltaEvent("there"), DummyCompletedEvent()]

    monkeypatch.setattr("app.llm_client.OpenAI", DummyClient)

    result = "".join(
        stream_response(
            "Hello",
            "test-key",
            "gpt-4o-mini",
            conversation_history=[{"role": "user", "content": "Hello"}],
        )
    )
    assert result == "Hello there"
