# tests/unit/policies/test_cleaning_policy.py
from datetime import datetime, timedelta
import pytest

from src.coffee_machine.policies.cleaning_policy import (
    DefaultCleaningPolicy,
    CleaningAction,
)


def test_no_action_when_below_schedule_threshold():
    policy = DefaultCleaningPolicy(schedule_threshold=5, immediate_threshold=10)
    action = policy.evaluate(dirty_count=0, last_cleaned_ts=None)
    assert action is CleaningAction.NO_ACTION


def test_schedule_when_between_thresholds():
    policy = DefaultCleaningPolicy(schedule_threshold=5, immediate_threshold=10)
    action = policy.evaluate(dirty_count=5, last_cleaned_ts=None)
    assert action is CleaningAction.SCHEDULE


def test_immediate_when_equal_or_above_immediate_threshold():
    policy = DefaultCleaningPolicy(schedule_threshold=5, immediate_threshold=10)
    assert policy.evaluate(dirty_count=10, last_cleaned_ts=None) is CleaningAction.IMMEDIATE
    assert policy.evaluate(dirty_count=15, last_cleaned_ts=None) is CleaningAction.IMMEDIATE


def test_time_based_immediate():
    policy = DefaultCleaningPolicy(schedule_threshold=5, immediate_threshold=10, max_time_between_cleans=timedelta(days=7))
    old_ts = datetime.utcnow() - timedelta(days=8)
    assert policy.evaluate(dirty_count=0, last_cleaned_ts=old_ts) is CleaningAction.IMMEDIATE


def test_invalid_thresholds_raise():
    with pytest.raises(ValueError):
        DefaultCleaningPolicy(schedule_threshold=10, immediate_threshold=5)
