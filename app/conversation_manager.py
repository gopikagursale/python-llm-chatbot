class ConversationManager:
    def __init__(self, history=None):
        self._history = list(history) if history is not None else []

    def initialize(self):
        self._history = []
        return self._history

    def get_history(self):
        return list(self._history)

    def build_request(self, user_message: str):
        text = (user_message or "").strip()
        if not text:
            raise ValueError("Message cannot be empty.")

        request = [dict(item) for item in self._history]
        request.append({"role": "user", "content": text})
        return request

    def add_exchange(self, user_message: str, assistant_message: str):
        text_user = (user_message or "").strip()
        text_assistant = (assistant_message or "").strip()
        if not text_user or not text_assistant:
            raise ValueError("User and assistant messages must be non-empty.")

        self._history.append({"role": "user", "content": text_user})
        self._history.append({"role": "assistant", "content": text_assistant})
        return self.get_history()

    def clear(self):
        self._history = []
        return self._history

    def __len__(self):
        return len(self._history)
