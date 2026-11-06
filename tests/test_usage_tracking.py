from decimal import Decimal

from app.costs import estimate_cost
from app.usage_tracking import UsageMetrics


class DummyUsage:
    def __init__(self, input_tokens=0, output_tokens=0, total_tokens=0, cached_tokens=0, reasoning_tokens=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.input_tokens_details = type("Details", (), {"cached_tokens": cached_tokens})()
        self.output_tokens_details = type("Details", (), {"reasoning_tokens": reasoning_tokens})()


class DummyResponse:
    def __init__(self, usage=None, model="gpt-4o-mini"):
        self.usage = usage
        self.model = model


def test_extract_usage_metrics_from_response():
    usage = DummyUsage(input_tokens=101, output_tokens=52, total_tokens=153, cached_tokens=11, reasoning_tokens=5)
    metrics = UsageMetrics.from_response(DummyResponse(usage=usage))
    assert metrics.input_tokens == 101
    assert metrics.output_tokens == 52
    assert metrics.total_tokens == 153
    assert metrics.cached_input_tokens == 11
    assert metrics.reasoning_tokens == 5


def test_cost_estimate_for_standard_usage():
    usage = UsageMetrics(input_tokens=1000, output_tokens=2000, total_tokens=3000)
    cost = estimate_cost("gpt-4o-mini", usage)
    assert cost is not None
    assert cost > 0
    assert isinstance(cost, Decimal)


def test_cost_estimate_handles_cached_tokens_without_double_counting():
    usage = UsageMetrics(input_tokens=1000, output_tokens=200, total_tokens=1200, cached_input_tokens=400)
    cost = estimate_cost("gpt-4o-mini", usage)
    assert cost is not None
    assert cost > 0


def test_unknown_model_cost_is_unavailable():
    usage = UsageMetrics(input_tokens=100, output_tokens=50, total_tokens=150)
    cost = estimate_cost("unknown-model", usage)
    assert cost is None
