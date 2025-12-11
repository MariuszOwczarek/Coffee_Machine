from src.errors import (InvalidBeanContainerConfigError,
                        NotEnoughBeansError,
                        InvalidBeanOperationError)
from src.coffee_machine.bean_container import (BeanContainer,
                                               BeanContainerRefillStatus)
import pytest


class TestBeanContainer:
    def test_bean_container_initialization(self):
        bean_container = BeanContainer(500, 200)
        assert bean_container.current_level == 200
        assert bean_container.maximum_level == 500

    def test_invalid_maximum_level(self):
        with pytest.raises(InvalidBeanContainerConfigError):
            BeanContainer(0, 200)

    def test_invalid_initial_level(self):
        with pytest.raises(InvalidBeanContainerConfigError):
            BeanContainer(100, -1)

    def test_initial_level_gt_maximum_level(self):
        with pytest.raises(InvalidBeanContainerConfigError):
            BeanContainer(100, 150)

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
        with pytest.raises(InvalidBeanContainerConfigError):
            BeanContainer(maximum, initial)

    def test_consume_beans(self):
        container = BeanContainer(500, 200)
        before = container.current_level
        container.consume_beans(100)

        assert container.current_level == before - 100
        assert container.current_level >= 0
        assert container.current_level <= container.maximum_level

    def test_consume_to_zero(self):
        container = BeanContainer(200, 100)
        container.consume_beans(100)

        assert container.is_empty() is True
        assert container.current_level == 0

    def test_consume_more_than_available_raises_and_state_unchanged(self):
        container = BeanContainer(500, 50)
        before = container.current_level
        with pytest.raises(NotEnoughBeansError):
            container.consume_beans(100)
        assert container.current_level == before

    @pytest.mark.parametrize("invalid_amount", [0, -10])
    def test_consume_invalid_amount_raises(self, invalid_amount):
        container = BeanContainer(500, 200)
        with pytest.raises(InvalidBeanOperationError):
            container.consume_beans(invalid_amount)

    # parametryzacja testu Refill, jeden test zamiast 3
    @pytest.mark.parametrize(
        "maximum_level, "
        "initial_level, "
        "refill_amount, "
        "expected_level, "
        "expected_status",
        [
            (500, 200, 100, 300, BeanContainerRefillStatus.STILL_NOT_FULL),
            (500, 300, 200, 500, BeanContainerRefillStatus.NOW_FULL),
            (500, 450, 200, 500, BeanContainerRefillStatus.NOW_FULL),
            (500, 500, 100, 500, BeanContainerRefillStatus.NOW_FULL)
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

        container = BeanContainer(maximum_level, initial_level)
        status = container.refill(refill_amount)

        assert container.current_level == expected_level
        assert status is expected_status

    def test_refill_wrong_argument(self):
        container = BeanContainer(500, 200)

        with pytest.raises(InvalidBeanOperationError):
            container.refill(0)

    def test_is_empty(self):
        container = BeanContainer(500, 0)

        assert container.is_empty() is True

    def test_is_full(self):
        container = BeanContainer(500, 500)

        assert container.is_full() is True

    def test_fulfillment_ratio(self):
        container = BeanContainer(500, 200)
        assert container.fulfillment_ratio == pytest.approx(0.4)
        assert 0 <= container.current_level <= container.maximum_level

    def test_missing_capacity(self):
        container = BeanContainer(500, 200)
        assert container.missing_capacity == 300
        assert 0 <= container.current_level <= container.maximum_level

    def test_few_small_refills(self):
        container = BeanContainer(500, 200)
        status = container.refill(50)

        assert container.current_level == 250
        assert status is BeanContainerRefillStatus.STILL_NOT_FULL
        assert 0 <= container.current_level <= container.maximum_level

        status = container.refill(50)
        assert container.current_level == 300
        assert status is BeanContainerRefillStatus.STILL_NOT_FULL
        assert 0 <= container.current_level <= container.maximum_level

        status = container.refill(100)
        assert container.current_level == 400
        assert status is BeanContainerRefillStatus.STILL_NOT_FULL
        assert 0 <= container.current_level <= container.maximum_level

        status = container.refill(100)
        assert container.current_level == 500
        assert status is BeanContainerRefillStatus.NOW_FULL
        assert 0 <= container.current_level <= container.maximum_level

    def test_refill_when_already_full(self):
        container = BeanContainer(500, 500)
        status = container.refill(100)
        assert container.current_level == 500
        assert status is BeanContainerRefillStatus.NOW_FULL

    def test_fulfillment_ratio_edges(self):
        assert BeanContainer(100, 0).fulfillment_ratio == pytest.approx(0.0)
        assert BeanContainer(100, 100).fulfillment_ratio == pytest.approx(1.0)
