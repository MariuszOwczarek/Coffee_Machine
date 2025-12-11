# src/coffee_machine/policies/refill_policy.py
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Tuple


class RefillResult(Enum):
    NOW_FULL = auto()
    STILL_NOT_FULL = auto()
    OVERFLOW_ERROR = auto()  # used by strict policy to indicate error


class RefillPolicy(ABC):
    """
    Abstract interface for refill policies.

    on_refill returns (new_level:int, RefillResult).
    """

    @abstractmethod
    def on_refill(self, current_level: int, refill_amount: int, maximum: int) -> Tuple[int, RefillResult]:
        raise NotImplementedError


class CapRefillPolicy(RefillPolicy):
    """
    Default, forgiving policy: cap to maximum when refill would overflow.
    """

    def on_refill(self, current_level: int, refill_amount: int, maximum: int):
        if refill_amount <= 0:
            raise ValueError("refill_amount must be > 0")

        new_level = current_level + refill_amount
        if new_level >= maximum:
            return maximum, RefillResult.NOW_FULL
        return new_level, RefillResult.STILL_NOT_FULL


class StrictRefillPolicy(RefillPolicy):
    """
    Strict policy: raising/returning overflow error instead of capping.
    """

    def on_refill(self, current_level: int, refill_amount: int, maximum: int):
        if refill_amount <= 0:
            raise ValueError("refill_amount must be > 0")

        new_level = current_level + refill_amount
        if new_level > maximum:
            return current_level, RefillResult.OVERFLOW_ERROR
        if new_level == maximum:
            return maximum, RefillResult.NOW_FULL
        return new_level, RefillResult.STILL_NOT_FULL
