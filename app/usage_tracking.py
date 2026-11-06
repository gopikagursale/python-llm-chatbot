from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class UsageMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_input_tokens: int = 0
    reasoning_tokens: int = 0
    cache_write_tokens: int = 0
    raw_usage: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def _safe_int(value: Any) -> int:
        if value is None:
            return 0
        try:
            value = int(value)
        except (TypeError, ValueError):
            return 0
        return value if value >= 0 else 0

    @classmethod
    def from_response(cls, response: Any) -> "UsageMetrics":
        usage = getattr(response, "usage", None)
        if usage is None:
            return cls(raw_usage={})

        raw_usage = usage if isinstance(usage, dict) else {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }

        input_details = getattr(usage, "input_tokens_details", None)
        output_details = getattr(usage, "output_tokens_details", None)

        if isinstance(usage, dict):
            input_details = usage.get("input_tokens_details")
            output_details = usage.get("output_tokens_details")

        cached_tokens = 0
        cache_write_tokens = 0
        if input_details is not None:
            if isinstance(input_details, dict):
                cached_tokens = input_details.get("cached_tokens", 0)
                cache_write_tokens = input_details.get(
                    "cache_creation_input_tokens",
                    input_details.get("cache_write_input_tokens", 0),
                )
            else:
                cached_tokens = getattr(input_details, "cached_tokens", 0)
                cache_write_tokens = getattr(
                    input_details,
                    "cache_creation_input_tokens",
                    getattr(input_details, "cache_write_input_tokens", 0),
                )

        reasoning_tokens = 0
        if output_details is not None:
            if isinstance(output_details, dict):
                reasoning_tokens = output_details.get("reasoning_tokens", 0)
            else:
                reasoning_tokens = getattr(output_details, "reasoning_tokens", 0)

        input_tokens = cls._safe_int(
            getattr(usage, "input_tokens", 0)
            if not isinstance(usage, dict)
            else usage.get("input_tokens", 0)
        )
        output_tokens = cls._safe_int(
            getattr(usage, "output_tokens", 0)
            if not isinstance(usage, dict)
            else usage.get("output_tokens", 0)
        )
        total_tokens = cls._safe_int(
            getattr(usage, "total_tokens", 0)
            if not isinstance(usage, dict)
            else usage.get("total_tokens", 0)
        )

        if total_tokens == 0 and (input_tokens or output_tokens):
            total_tokens = input_tokens + output_tokens

        return cls(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cached_input_tokens=cls._safe_int(cached_tokens),
            reasoning_tokens=cls._safe_int(reasoning_tokens),
            cache_write_tokens=cls._safe_int(cache_write_tokens),
            raw_usage=raw_usage,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cache_write_tokens": self.cache_write_tokens,
        }
