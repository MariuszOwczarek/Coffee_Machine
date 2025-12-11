# tests/unit/policies/test_refill_policy.py
import pytest

from src.coffee_machine.policies.refill_policy import (
    CapRefillPolicy,
    StrictRefillPolicy,
    RefillResult,
)


def test_cap_refill_partial():
    p = CapRefillPolicy()
    new_level, result = p.on_refill(current_level=100, refill_amount=50, maximum=200)
    assert new_level == 150
    assert result is RefillResult.STILL_NOT_FULL


def test_cap_refill_to_full_on_overflow():
    p = CapRefillPolicy()
    new_level, result = p.on_refill(current_level=180, refill_amount=50, maximum=200)
    assert new_level == 200
    assert result is RefillResult.NOW_FULL


def test_strict_refill_partial_and_full():
    p = StrictRefillPolicy()
    new_level, result = p.on_refill(current_level=100, refill_amount=50, maximum=200)
    assert new_level == 150
    assert result is RefillResult.STILL_NOT_FULL

    new_level, result = p.on_refill(current_level=150, refill_amount=50, maximum=200)
    assert new_level == 200
    assert result is RefillResult.NOW_FULL


def test_strict_refill_overflow_error():
    p = StrictRefillPolicy()
    new_level, result = p.on_refill(current_level=180, refill_amount=50, maximum=200)
    assert new_level == 180  # unchanged
    assert result is RefillResult.OVERFLOW_ERROR


def test_refill_invalid_amount_raises():
    p = CapRefillPolicy()
    with pytest.raises(ValueError):
        p.on_refill(current_level=100, refill_amount=0, maximum=200)
