# src/coffee_machine/policies/cleaning_policy.py
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional
from datetime import datetime, timedelta


class CleaningAction(Enum):
    NO_ACTION = auto()
    SCHEDULE = auto()   # schedule cleaning after current brew cycle
    IMMEDIATE = auto()  # require immediate cleaning before next brew


class CleaningPolicy(ABC):
    """
    Abstract interface for cleaning policies.

    Implementations must be pure functions: evaluate state and return CleaningAction.
    """

    @abstractmethod
    def evaluate(self, dirty_count: int, last_cleaned_ts: Optional[datetime]) -> CleaningAction:
        raise NotImplementedError


class DefaultCleaningPolicy(CleaningPolicy):
    """
    Default cleaning policy:

    - If dirty_count < schedule_threshold -> NO_ACTION
    - If schedule_threshold <= dirty_count < immediate_threshold -> SCHEDULE
    - If dirty_count >= immediate_threshold -> IMMEDIATE

    Optional time-based rule:
    - If max_time_between_cleans is set and last_cleaned_ts is older -> IMMEDIATE
    """

    def __init__(
        self,
        schedule_threshold: int = 80,
        immediate_threshold: int = 120,
        max_time_between_cleans: Optional[timedelta] = None,
    ):
        if not (0 <= schedule_threshold <= immediate_threshold):
            raise ValueError("0 <= schedule_threshold <= immediate_threshold required")
        self.schedule_threshold = int(schedule_threshold)
        self.immediate_threshold = int(immediate_threshold)
        self.max_time_between_cleans = max_time_between_cleans

    def evaluate(self, dirty_count: int, last_cleaned_ts: Optional[datetime]) -> CleaningAction:
        # normalize inputs
        dirty_count = int(dirty_count or 0)

        # time-based immediate check
        if self.max_time_between_cleans is not None and last_cleaned_ts is not None:
            if datetime.utcnow() - last_cleaned_ts >= self.max_time_between_cleans:
                return CleaningAction.IMMEDIATE

        # count-based logic
        if dirty_count < self.schedule_threshold:
            return CleaningAction.NO_ACTION

        if dirty_count < self.immediate_threshold:
            return CleaningAction.SCHEDULE

        return CleaningAction.IMMEDIATE
