from enum import Enum, auto
from src.errors import (
    InvalidWaterTankConfigError,
    InvalidWaterOperationError,
    NotEnoughWaterError,
)


class WaterTankRefillStatus(Enum):
    """
    Result status returned by the WaterTank.refill operation.
    """

    NOW_FULL = auto()
    """Tank has reached its maximum capacity after refill."""

    STILL_NOT_FULL = auto()
    """Tank is still not full after refill."""


class WaterTank:
    """
    Domain model representing a water reservoir for a coffee machine.

    The WaterTank is responsible only for:
    - storing the current and maximum water level,
    - validating configuration and operations,
    - providing domain-level queries about its fill state.

    All water volumes are expressed in milliliters (ml).

    Invariants guaranteed by this class:
    - 0 <= current_level <= maximum_level
    - maximum_level > 0
    """

    def __init__(self, maximum_level: int, initial_level: int) -> None:
        """
        Create a new WaterTank instance.

        Args:
            maximum_level (int): Maximum capacity of the tank in milliliters.
                                 Must be greater than zero.
            initial_level (int): Initial water level in milliliters.
                                 Must satisfy:
                                 0 <= initial_level <= maximum_level.

        Raises:
            InvalidWaterTankConfigError:
                - If maximum_level is not greater than zero.
                - If initial_level is negative.
                - If initial_level exceeds maximum_level.
        """
        if maximum_level <= 0:
            raise InvalidWaterTankConfigError(
                "maximum_level should be greater than zero"
            )

        if initial_level < 0:
            raise InvalidWaterTankConfigError(
                "Initial level cannot be less than zero"
            )

        if initial_level > maximum_level:
            raise InvalidWaterTankConfigError(
                "Initial level should not be greater than maximum level"
            )

        self._maximum_level = maximum_level
        self._current_level = initial_level

    @property
    def missing_capacity(self) -> int:
        """
        Return the amount of water (in ml) missing to reach full capacity.

        Returns:
            int: Difference between maximum level and current level.
        """
        return self._maximum_level - self._current_level

    @property
    def fulfillment_ratio(self) -> float:
        """
        Return the current fill ratio of the tank.

        The value is expressed as a float in the range [0.0, 1.0].

        Returns:
            float: Current_level divided by maximum_level.
        """
        return self._current_level / self._maximum_level

    @property
    def current_level(self) -> int:
        """
        Return the current water level in milliliters.

        Returns:
            int: Current water level.
        """
        return self._current_level

    @property
    def maximum_level(self) -> int:
        """
        Return the maximum water capacity of the tank in milliliters.

        Returns:
            int: Maximum tank capacity.
        """
        return self._maximum_level

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the tank.

        Returns:
            str: Representation containing class name, maximum level
                 and current level.
        """
        return (
            f"{self.__class__.__name__}(max={self._maximum_level},"
            f"current={self._current_level})"
        )

    def consume_water(self, use_level: int) -> None:
        """
        Consume a specified amount of water from the tank.

        This operation reduces the current water level by the given amount.
        The operation is atomic: if there is not enough water available,
        the state of the tank is not modified.

        Args:
            use_level (int): Amount of water to consume in milliliters.
                             Must be greater than zero.

        Raises:
            InvalidWaterOperationError:
                If use_level is less than or equal to zero.
            NotEnoughWaterError:
                If the tank does not contain enough water to fulfill
                the requested consumption.
        """
        if use_level <= 0:
            raise InvalidWaterOperationError(
                "Water usage must be greater than zero"
            )

        if self._current_level - use_level >= 0:
            self._current_level -= use_level
            return

        raise NotEnoughWaterError

    def refill(self, refill_level: int) -> WaterTankRefillStatus:
        """
        Refill the tank with a specified amount of water.

        If the refill would exceed the maximum capacity, the water level
        is capped at maximum_level and the tank becomes full.

        Args:
            refill_level (int): Amount of water to add in milliliters.
                                Must be greater than zero.

        Returns:
            WaterTankRefillStatus:
                - NOW_FULL if the tank becomes full as a result of refill,
                - STILL_NOT_FULL if the tank is still not full after refill.

        Raises:
            InvalidWaterOperationError:
                If refill_level is less than or equal to zero.
        """
        if refill_level <= 0:
            raise InvalidWaterOperationError(
                "Refill level must be greater than zero"
            )

        new_level = self._current_level + refill_level

        if new_level >= self._maximum_level:
            self._current_level = self._maximum_level
            return WaterTankRefillStatus.NOW_FULL

        self._current_level += refill_level
        return WaterTankRefillStatus.STILL_NOT_FULL

    def is_empty(self) -> bool:
        """
        Check whether the tank is empty.

        Returns:
            bool: True if the current water level is zero, False otherwise.
        """
        return self._current_level == 0

    def is_full(self) -> bool:
        """
        Check whether the tank is full.

        Returns:
            bool: True if the current water level equals the maximum level,
                  False otherwise.
        """
        return self._current_level == self._maximum_level
