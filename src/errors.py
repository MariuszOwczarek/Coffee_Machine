class CoffeeMachineError(Exception):
    ...


class InvalidWaterTankConfigError(CoffeeMachineError):
    ...


class InvalidWaterOperationError(CoffeeMachineError):
    ...


class NotEnoughWaterError(CoffeeMachineError):
    ...


class InvalidBeanContainerConfigError(CoffeeMachineError):
    ...


class InvalidBeanOperationError(CoffeeMachineError):
    ...


class NotEnoughBeansError(CoffeeMachineError):
    ...
