# src/coffee_machine/coffee_recipe.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from src.errors import InvalidRecipeError


class CoffeeRecipeGrindLevel(Enum):
    FINE = auto()
    MEDIUM = auto()
    COARSE = auto()


MAX_WATER_ML = 2000
MAX_BEANS_G = 500


@dataclass(frozen=True)
class CoffeeRecipe:
    """
    Immutable domain model describing a coffee recipe.

    Units:
      - water_ml: milliliters (int)
      - beans_g: grams (int)
      - grind: optional CoffeeRecipeGrindLevel enum
    """
    name: str
    water_ml: int
    beans_g: int
    grind: Optional[CoffeeRecipeGrindLevel] = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidRecipeError("name must be a non-empty string")

        if not isinstance(self.water_ml, int):
            raise InvalidRecipeError("water_ml must be an integer")
        if self.water_ml < 0 or self.water_ml > MAX_WATER_ML:
            raise InvalidRecipeError(
                f"water_ml must be in range [0, {MAX_WATER_ML}]"
            )

        if not isinstance(self.beans_g, int):
            raise InvalidRecipeError("beans_g must be an integer")
        if self.beans_g < 0 or self.beans_g > MAX_BEANS_G:
            raise InvalidRecipeError(
                f"beans_g must be in range [0, {MAX_BEANS_G}]"
            )

        if self.grind is not None and not isinstance(self.grind,
                                                     CoffeeRecipeGrindLevel):
            raise InvalidRecipeError(
                "grind must be a CoffeeRecipeGrindLevel or None"
            )

    def requires_water(self) -> bool:
        """Return True if recipe requires water (water_ml > 0)."""
        return self.water_ml > 0

    def requires_beans(self) -> bool:
        """Return True if recipe requires beans (beans_g > 0)."""
        return self.beans_g > 0

    def as_dict(self) -> dict:
        """Return a serializable mapping of the recipe."""
        return {
            "name": self.name,
            "water_ml": self.water_ml,
            "beans_g": self.beans_g,
            "grind": self.grind.name if self.grind is not None else None,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, water_ml={self.water_ml}, "
            f"beans_g={self.beans_g}, "
            f"grind={self.grind.name if self.grind is not None else None})"
        )
