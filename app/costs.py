from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.usage_tracking import UsageMetrics

MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": Decimal("0.15"),
        "output": Decimal("0.60"),
        "cached_input": Decimal("0.03"),
        "cache_write": Decimal("0.15"),
    },
    "gpt-4.1-mini": {
        "input": Decimal("0.40"),
        "output": Decimal("1.60"),
        "cached_input": Decimal("0.08"),
        "cache_write": Decimal("0.40"),
    },
}


def estimate_cost(model_id: Optional[str], usage: Optional[UsageMetrics]) -> Optional[Decimal]:
    if usage is None:
        return None

    if model_id is None:
        return None

    pricing = MODEL_PRICING.get(model_id)
    if pricing is None:
        return None

    input_tokens = max(0, usage.input_tokens)
    output_tokens = max(0, usage.output_tokens)
    cached_input_tokens = max(0, usage.cached_input_tokens)
    cache_write_tokens = max(0, usage.cache_write_tokens)

    base_input_tokens = max(0, input_tokens - cached_input_tokens)
    input_cost = (Decimal(base_input_tokens) * pricing["input"]) / Decimal("1000000")
    output_cost = (Decimal(output_tokens) * pricing["output"]) / Decimal("1000000")
    cached_cost = (Decimal(cached_input_tokens) * pricing["cached_input"]) / Decimal("1000000")
    cache_write_cost = (Decimal(cache_write_tokens) * pricing["cache_write"]) / Decimal("1000000")

    total = input_cost + output_cost + cached_cost + cache_write_cost
    return total.quantize(Decimal("0.000001"))
