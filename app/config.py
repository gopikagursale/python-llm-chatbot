import os

from dotenv import load_dotenv


def load_settings():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    return api_key, model


def load_model_options(default_model=None):
    load_dotenv()
    default_model = default_model or os.getenv("OPENAI_MODEL")
    configured = os.getenv("OPENAI_MODELS", "")
    model_ids = [item.strip() for item in configured.split(",") if item.strip()]

    if default_model:
        model_ids = [default_model] + [item for item in model_ids if item != default_model]

    unique_models = []
    for model_id in model_ids:
        if model_id not in unique_models:
            unique_models.append(model_id)

    if not unique_models and default_model:
        return [default_model]

    return unique_models
