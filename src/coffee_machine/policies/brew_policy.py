# src/coffee_machine/policies/brew_policy.py
from __future__ import annotations
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Optional, Dict
from src.coffee_machine.coffee_recipe import CoffeeRecipe


class BrewDecision(Enum):
    OK = auto()
    OUT_OF_WATER = auto()
    OUT_OF_BEANS = auto()
    RECIPE_FORBIDDEN = auto()
    NEEDS_CLEANING = auto()
    ERROR = auto()


class BrewPolicy(ABC):
    """
    Abstract interface for brew decision policies.

    Implementations must not mutate resources; they only evaluate and return
    a BrewDecision.
    """

    @abstractmethod
    def can_brew(
        self,
        recipe: CoffeeRecipe,
        water_available_ml: int,
        beans_available_g: int,
        maintenance_state: Optional[Dict] = None,
    ) -> BrewDecision:
        raise NotImplementedError


class DefaultBrewPolicy(BrewPolicy):
    """
    Default, simple brew policy.

    Configurable parameters:
      - clean_threshold: number of brews after which machine needs cleaning
      - allow_recipe_with_no_requirements: whether recipes that require neither
        water nor beans are allowed (default: False -> RECIPE_FORBIDDEN).
    """

    def __init__(self, clean_threshold: int = 100, allow_recipe_with_no_requirements: bool = False):
        if clean_threshold < 0:
            raise ValueError("clean_threshold must be >= 0")
        self.clean_threshold = clean_threshold
        self.allow_recipe_with_no_requirements = allow_recipe_with_no_requirements

    def can_brew(
        self,
        recipe: CoffeeRecipe,
        water_available_ml: int,
        beans_available_g: int,
        maintenance_state: Optional[Dict] = None,
    ) -> BrewDecision:
        # safety: normalize maintenance_state
        maintenance_state = maintenance_state or {}
        dirty_count = int(maintenance_state.get("dirty_count", 0))

        # 1. sanity on recipe methods
        requires_water = recipe.requires_water()
        requires_beans = recipe.requires_beans()

        # 2. recipe that requires nothing -> either allow or treat as forbidden
        if not requires_water and not requires_beans:
            return BrewDecision.OK if self.allow_recipe_with_no_requirements else BrewDecision.RECIPE_FORBIDDEN

        # 3. resource checks (water first)
        if requires_water and water_available_ml < recipe.water_ml:
            return BrewDecision.OUT_OF_WATER

        if requires_beans and beans_available_g < recipe.beans_g:
            return BrewDecision.OUT_OF_BEANS

        # 4. cleaning check
        if dirty_count >= self.clean_threshold:
            return BrewDecision.NEEDS_CLEANING

        # 5. default: OK
        return BrewDecision.OK
