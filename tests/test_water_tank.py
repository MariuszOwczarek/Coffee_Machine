from src.errors import (InvalidWaterTankConfigError,
                        NotEnoughWaterError,
                        InvalidWaterOperationError)
from src.coffee_machine.water_tank import WaterTank, WaterTankRefillStatus
import pytest


class TestWaterTank:
    def test_water_tank_initialization(self):
        watertank = WaterTank(500, 200)
        assert watertank.current_level == 200
        assert watertank.maximum_level == 500

    def test_invalid_maximum_level(self):
        with pytest.raises(InvalidWaterTankConfigError):
            WaterTank(0, 200)

    def test_invalid_initial_level(self):
        with pytest.raises(InvalidWaterTankConfigError):
            WaterTank(100, -1)

    def test_initial_level_gt_maximum_level(self):
        with pytest.raises(InvalidWaterTankConfigError):
            WaterTank(100, 150)

    # tutaj przyklad parametryzacji 1 testu zamiast pisania 3 testow jak wyzej
    @pytest.mark.parametrize(
        "maximum, initial",
        [
            (0, 200),
            (100, -1),
            (100, 150),
        ],
        ids=[
            "maximum_level_zero",
            "initial_level_negative",
            "initial_gt_maximum",
        ]
    )
    def test_constructor_invalid_values(self, maximum, initial):
        with pytest.raises(InvalidWaterTankConfigError):
            WaterTank(maximum, initial)

    def test_consume_water(self):
        tank = WaterTank(500, 200)
        before = tank.current_level
        tank.consume_water(100)

        assert tank.current_level == before - 100
        assert tank.current_level >= 0
        assert tank.current_level <= tank.maximum_level

    def test_consume_to_zero(self):
        tank = WaterTank(200, 100)
        tank.consume_water(100)

        assert tank.is_empty() is True
        assert tank.current_level == 0

    def test_consume_more_than_available_raises_and_state_unchanged(self):
        tank = WaterTank(500, 50)
        before = tank.current_level
        with pytest.raises(NotEnoughWaterError):
            tank.consume_water(100)
        assert tank.current_level == before

    @pytest.mark.parametrize("invalid_amount", [0, -10])
    def test_consume_invalid_amount_raises(self, invalid_amount):
        tank = WaterTank(500, 200)
        with pytest.raises(InvalidWaterOperationError):
            tank.consume_water(invalid_amount)

    # parametryzacja testu Refill, jeden test zamiast 3
    @pytest.mark.parametrize(
        "maximum_level, "
        "initial_level, "
        "refill_amount, "
        "expected_level, "
        "expected_status",
        [
            (500, 200, 100, 300, WaterTankRefillStatus.STILL_NOT_FULL),
            (500, 300, 200, 500, WaterTankRefillStatus.NOW_FULL),
            (500, 450, 200, 500, WaterTankRefillStatus.NOW_FULL),
            (500, 500, 100, 500, WaterTankRefillStatus.NOW_FULL)
        ],
        ids=[
            "partial_refill",
            "full_refill",
            "overflow_refill",
            "already_full"
        ]
    )
    def test_refill_behavior(self, maximum_level,
                             initial_level,
                             refill_amount,
                             expected_level,
                             expected_status):

        tank = WaterTank(maximum_level, initial_level)
        status = tank.refill(refill_amount)

        assert tank.current_level == expected_level
        assert status is expected_status

    def test_refill_wrong_argument(self):
        tank = WaterTank(500, 200)

        with pytest.raises(InvalidWaterOperationError):
            tank.refill(0)

    def test_is_empty(self):
        tank = WaterTank(500, 0)

        assert tank.is_empty() is True

    def test_is_full(self):
        tank = WaterTank(500, 500)

        assert tank.is_full() is True

    def test_fulfillment_ratio(self):
        tank = WaterTank(500, 200)
        assert tank.fulfillment_ratio == pytest.approx(0.4)
        assert 0 <= tank.current_level <= tank.maximum_level

    def test_missing_capacity(self):
        tank = WaterTank(500, 200)
        assert tank.missing_capacity == 300
        assert 0 <= tank.current_level <= tank.maximum_level

    def test_few_small_refills(self):
        tank = WaterTank(500, 200)
        status = tank.refill(50)

        assert tank.current_level == 250
        assert status is WaterTankRefillStatus.STILL_NOT_FULL
        assert 0 <= tank.current_level <= tank.maximum_level

        status = tank.refill(50)
        assert tank.current_level == 300
        assert status is WaterTankRefillStatus.STILL_NOT_FULL
        assert 0 <= tank.current_level <= tank.maximum_level

        status = tank.refill(100)
        assert tank.current_level == 400
        assert status is WaterTankRefillStatus.STILL_NOT_FULL
        assert 0 <= tank.current_level <= tank.maximum_level

        status = tank.refill(100)
        assert tank.current_level == 500
        assert status is WaterTankRefillStatus.NOW_FULL
        assert 0 <= tank.current_level <= tank.maximum_level

    def test_refill_when_already_full(self):
        tank = WaterTank(500, 500)
        status = tank.refill(100)
        assert tank.current_level == 500
        assert status is WaterTankRefillStatus.NOW_FULL

    def test_fulfillment_ratio_edges(self):
        assert WaterTank(100, 0).fulfillment_ratio == pytest.approx(0.0)
        assert WaterTank(100, 100).fulfillment_ratio == pytest.approx(1.0)
