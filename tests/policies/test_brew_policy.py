from src.coffee_machine.coffee_recipe import CoffeeRecipe
from src.coffee_machine.policies.brew_policy import (DefaultBrewPolicy,
                                                     BrewDecision)


def test_brew_policy_ok_when_resources_sufficient():
    policy = DefaultBrewPolicy(clean_threshold=10)
    recipe = CoffeeRecipe("espresso", 30, 8)
    decision = policy.can_brew(recipe,
                               water_available_ml=100,
                               beans_available_g=100,
                               maintenance_state={"dirty_count": 0})

    assert decision is BrewDecision.OK


def test_brew_policy_out_of_water():
    policy = DefaultBrewPolicy(clean_threshold=10)
    recipe = CoffeeRecipe("espresso", 50, 8)
    decision = policy.can_brew(recipe,
                               water_available_ml=40,
                               beans_available_g=100,
                               maintenance_state={})

    assert decision is BrewDecision.OUT_OF_WATER


def test_brew_policy_out_of_beans():
    policy = DefaultBrewPolicy(clean_threshold=10)
    recipe = CoffeeRecipe("espresso", 30, 10)
    decision = policy.can_brew(recipe,
                               water_available_ml=100,
                               beans_available_g=9,
                               maintenance_state={})

    assert decision is BrewDecision.OUT_OF_BEANS


def test_brew_policy_needs_cleaning_when_dirty_count_exceeded():
    policy = DefaultBrewPolicy(clean_threshold=2)
    recipe = CoffeeRecipe("espresso", 10, 1)
    decision = policy.can_brew(recipe, water_available_ml=100,
                               beans_available_g=100,
                               maintenance_state={"dirty_count": 2})

    assert decision is BrewDecision.NEEDS_CLEANING
