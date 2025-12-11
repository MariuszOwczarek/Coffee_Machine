from enum import Enum, auto
from src.errors import (
    InvalidBeanContainerConfigError,
    InvalidBeanOperationError,
    NotEnoughBeansError,
)


class BeanContainerRefillStatus(Enum):
    """
    Result status returned by BeanContainer.refill().
    """

    NOW_FULL = auto()
    """Container reached maximum capacity after refill."""

    STILL_NOT_FULL = auto()
    """Container is still not full after refill."""


class BeanContainer:
    """
    Domain model representing a bean/container of coffee (measured in grams).

    Responsibilities:
    - hold current and maximum bean quantity (int grams),
    - validate constructor and operations,
    - provide domain queries (is_empty, is_full, missing_capacity,
        fulfillment_ratio).

    Invariants:
    - 0 <= current_level <= maximum_level
    - maximum_level > 0
    """

    def __init__(self, maximum_grams: int, initial_grams: int) -> None:
        """
        Initialize a BeanContainer.

        Args:
            maximum_grams: maximum capacity in grams (must be > 0).
            initial_grams: initial amount in grams (must satisfy 0 <=
                                    initial_grams <= maximum_grams).

        Raises:
            InvalidBeanContainerConfigError: on invalid constructor arguments.
        """
        if maximum_grams <= 0:
            raise InvalidBeanContainerConfigError(
                "maximum_grams should be greater than zero"
            )

        if initial_grams < 0:
            raise InvalidBeanContainerConfigError(
                "initial_grams cannot be less than zero"
            )

        if initial_grams > maximum_grams:
            raise InvalidBeanContainerConfigError(
                "initial_grams should not be greater than maximum_grams"
            )

        self._maximum_grams = maximum_grams
        self._current_grams = initial_grams

    @property
    def missing_capacity(self) -> int:
        """
        Amount of grams missing to reach maximum capacity.

        Returns:
            int: maximum_grams - current_grams
        """
        return self._maximum_grams - self._current_grams

    @property
    def fulfillment_ratio(self) -> float:
        """
        Current fill ratio in range [0.0, 1.0].

        Returns:
            float: current_grams / maximum_grams
        """
        return self._current_grams / self._maximum_grams

    @property
    def current_level(self) -> int:
        """
        Current amount of beans in grams.

        Returns:
            int
        """
        return self._current_grams

    @property
    def maximum_level(self) -> int:
        """
        Maximum capacity in grams.

        Returns:
            int
        """
        return self._maximum_grams

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(max={self._maximum_grams}g,"
            f" current={self._current_grams}g)"
        )

    def consume_beans(self, amount_grams: int) -> None:
        """
        Consume a specified amount of beans (grams).

        Operation is atomic: if there is not enough beans, the state
        is not modified.

        Args:
            amount_grams: grams to consume (must be > 0).

        Raises:
            InvalidBeanOperationError: if amount_grams <= 0.
            NotEnoughBeansError: if there is not enough beans to
            consume the requested amount.
        """
        if amount_grams <= 0:
            raise InvalidBeanOperationError("Consumption amount must be "
                                            "greater than zero")

        if self._current_grams - amount_grams >= 0:
            self._current_grams -= amount_grams
            return

        raise NotEnoughBeansError("Not enough beans to consume  "
                                  "the requested amount")

    def refill(self, refill_grams: int) -> BeanContainerRefillStatus:
        """
        Refill the container by a specified amount (grams).

        If the refill would exceed the maximum capacity,
        the level is capped at maximum.

        Args:
            refill_grams: grams to add (must be > 0).

        Returns:
            BeanContainerRefillStatus:
                    NOW_FULL if container is full after refill,
                    STILL_NOT_FULL otherwise.

        Raises:
            InvalidBeanOperationError: if refill_grams <= 0.
        """
        if refill_grams <= 0:
            raise InvalidBeanOperationError("Refill amount must be "
                                            "greater than zero")

        new_level = self._current_grams + refill_grams

        if new_level >= self._maximum_grams:
            self._current_grams = self._maximum_grams
            return BeanContainerRefillStatus.NOW_FULL

        self._current_grams = new_level
        return BeanContainerRefillStatus.STILL_NOT_FULL

    def is_empty(self) -> bool:
        """Return True if the container is empty (0 grams)."""
        return self._current_grams == 0

    def is_full(self) -> bool:
        """Return True if the container is full (current == maximum)."""
        return self._current_grams == self._maximum_grams
