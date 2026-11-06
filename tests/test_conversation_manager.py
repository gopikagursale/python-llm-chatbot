from app.conversation_manager import ConversationManager


def test_first_message_build_request():
    manager = ConversationManager()
    request = manager.build_request("My name is Sarah.")

    assert request == [{"role": "user", "content": "My name is Sarah."}]


def test_second_message_build_request_includes_history():
    manager = ConversationManager([
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
    ])

    request = manager.build_request("What is my name?")

    assert request == [
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
        {"role": "user", "content": "What is my name?"},
    ]


def test_third_message_build_request_keeps_all_turns():
    manager = ConversationManager([
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
        {"role": "user", "content": "What is my name?"},
        {"role": "assistant", "content": "Your name is Sarah."},
    ])

    request = manager.build_request("What color is the sky?")

    assert request == [
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
        {"role": "user", "content": "What is my name?"},
        {"role": "assistant", "content": "Your name is Sarah."},
        {"role": "user", "content": "What color is the sky?"},
    ]


def test_new_chat_clears_history():
    manager = ConversationManager([
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
    ])

    manager.clear()
    request = manager.build_request("Hi there")

    assert request == [{"role": "user", "content": "Hi there"}]


def test_conversation_manager_failure_does_not_corrupt_history():
    manager = ConversationManager([
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
    ])
    original = manager.get_history()

    try:
        raise RuntimeError("API unavailable")
    except RuntimeError:
        pass

    assert manager.get_history() == original


def test_session_isolation_between_managers():
    manager_one = ConversationManager()
    manager_two = ConversationManager()

    manager_one.add_exchange("My name is Sarah.", "Hello Sarah!")

    assert manager_one.get_history() == [
        {"role": "user", "content": "My name is Sarah."},
        {"role": "assistant", "content": "Hello Sarah!"},
    ]
    assert manager_two.get_history() == []
