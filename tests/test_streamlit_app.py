import app.llm_client as llm_client
import streamlit_app


class FakeChatMessage:
    def __init__(self, role):
        self.role = role

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSpinner:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSessionState(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_instantiated = False

    def __setitem__(self, key, value):
        if key == "selected_model" and self.widget_instantiated:
            raise RuntimeError(
                "st.session_state['selected_model'] cannot be modified after the "
                "widget with that key is instantiated."
            )
        super().__setitem__(key, value)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __setattr__(self, key, value):
        if key == "widget_instantiated":
            object.__setattr__(self, key, value)
        else:
            self[key] = value


class FakeExpander:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSidebar:
    def __init__(self, session_state=None):
        self.session_state = session_state

    def checkbox(self, label, value=True, key=None):
        return value

    def selectbox(self, label, options, index=0, key=None):
        if self.session_state is not None:
            self.session_state.widget_instantiated = True
        return options[index]

    def button(self, label, on_click=None):
        return False

    def expander(self, label, expanded=False):
        return FakeExpander()

    def caption(self, value):
        return value

    def json(self, value):
        return value

    def write(self, value):
        return value


class FakeStreamlit:
    def __init__(self):
        self.session_state = FakeSessionState(messages=[])
        self.sidebar = FakeSidebar(self.session_state)
        self.rendered_messages = []
        self.errors = []
        self.warnings = []

    def chat_message(self, role):
        return FakeChatMessage(role)

    def markdown(self, value):
        self.rendered_messages.append(value)

    def warning(self, message):
        self.warnings.append(message)

    def error(self, message):
        self.errors.append(message)

    def spinner(self, message):
        return FakeSpinner()

    def write_stream(self, stream):
        for item in stream:
            self.rendered_messages.append(item)

    def checkbox(self, label, value=True, key=None):
        return value

    def selectbox(self, label, options, index=0, key=None):
        self.session_state.widget_instantiated = True
        return options[index]

    def button(self, label, on_click=None):
        return False

    def expander(self, label, expanded=False):
        return FakeExpander()

    def json(self, value):
        self.rendered_messages.append(str(value))

    def write(self, value):
        self.rendered_messages.append(str(value))

    def caption(self, value):
        self.rendered_messages.append(value)


def test_streamlit_app_renders_chat_history(monkeypatch):
    fake_st = FakeStreamlit()
    fake_st.session_state["messages"] = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]
    monkeypatch.setattr(streamlit_app, "st", fake_st)

    streamlit_app.render_chat_history()

    assert fake_st.rendered_messages == ["hello", "hi there"]


def test_streamlit_app_successful_message_flow(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(streamlit_app, "st", fake_st)
    monkeypatch.setenv("OPENAI_API_KEY", "demo-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    class DummyResponse:
        def __init__(self, output_text):
            self.output_text = output_text

    class DummyClient:
        def __init__(self, api_key):
            assert api_key == "demo-key"

        class responses:
            @staticmethod
            def create(model, input, store=False):
                assert model == "gpt-4o-mini"
                assert input == [{"role": "user", "content": "Hello from the browser"}]
                return DummyResponse("Hello from the assistant")

    monkeypatch.setattr(llm_client, "OpenAI", DummyClient)

    streamlit_app.handle_user_message("Hello from the browser")

    assert fake_st.session_state["messages"] == [
        {"role": "user", "content": "Hello from the browser"},
        {"role": "assistant", "content": "Hello from the assistant"},
    ]
    assert fake_st.errors == []


def test_streamlit_app_missing_config_shows_error(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(streamlit_app, "st", fake_st)
    monkeypatch.setattr(streamlit_app, "load_settings", lambda: ("", ""))

    streamlit_app.handle_user_message("Missing config test")

    assert fake_st.errors == [
        "Missing OpenAI configuration. Set OPENAI_API_KEY and OPENAI_MODEL in your environment or .env file."
    ]
    assert fake_st.session_state["messages"] == []


def test_streamlit_app_failed_api_does_not_add_assistant_message(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(streamlit_app, "st", fake_st)
    monkeypatch.setenv("OPENAI_API_KEY", "demo-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    class DummyClient:
        def __init__(self, api_key):
            assert api_key == "demo-key"

        class responses:
            @staticmethod
            def create(model, input, store=False):
                raise RuntimeError("API unavailable")

    monkeypatch.setattr(llm_client, "OpenAI", DummyClient)

    streamlit_app.handle_user_message("Trigger a failure")

    assert fake_st.session_state["messages"] == [{"role": "user", "content": "Trigger a failure"}]
    assert fake_st.errors == [
        "Sorry, I couldn't get a response right now. Please check your API configuration and try again."
    ]


def test_streamlit_app_model_switch_uses_selected_model(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(streamlit_app, "st", fake_st)
    monkeypatch.setenv("OPENAI_API_KEY", "demo-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("OPENAI_MODELS", "gpt-4o-mini,gpt-4.1-mini")
    fake_st.session_state["selected_model"] = "gpt-4.1-mini"

    class DummyResponse:
        def __init__(self, output_text):
            self.output_text = output_text

    class DummyClient:
        def __init__(self, api_key):
            assert api_key == "demo-key"

        class responses:
            @staticmethod
            def create(model, input, store=False):
                assert model == "gpt-4.1-mini"
                return DummyResponse("Switched model answer")

    monkeypatch.setattr(llm_client, "OpenAI", DummyClient)

    streamlit_app.handle_user_message("Switch model")

    assert fake_st.session_state["messages"][-1] == {"role": "assistant", "content": "Switched model answer"}
    assert fake_st.session_state["selected_model"] == "gpt-4.1-mini"


def test_render_sidebar_keeps_selected_model_after_widget_instantiation(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(streamlit_app, "st", fake_st)
    monkeypatch.setenv("OPENAI_API_KEY", "demo-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("OPENAI_MODELS", "gpt-4o-mini,gpt-4.1-mini")
    fake_st.session_state["selected_model"] = "gpt-4.1-mini"

    streamlit_app.render_sidebar()

    assert fake_st.session_state["selected_model"] == "gpt-4.1-mini"
    assert fake_st.session_state["messages"] == []
