from src.coffee_machine.coffee_recipe import (CoffeeRecipe,
                                              CoffeeRecipeGrindLevel)
from src.errors import InvalidRecipeError
import pytest
from dataclasses import FrozenInstanceError


@pytest.fixture
def coffee() -> CoffeeRecipe:
    return CoffeeRecipe('espresso', 30, 8)


class TestCoffeeRecipe:
    def test_coffee_recipe_initialization(self, coffee):
        assert coffee.name == 'espresso'
        assert coffee.water_ml == 30
        assert coffee.beans_g == 8
        assert coffee.grind is None

    @pytest.mark.parametrize("name",
                             ["", " ", None],
                             ids=["empty", "space", "None"])
    def test_coffee_recipe_name_empty(self, name):
        with pytest.raises(InvalidRecipeError):
            CoffeeRecipe(name, 30, 8)

    @pytest.mark.parametrize("kwargs", [
        {"water_ml": -1, "beans_g": 8},
        {"water_ml": 30, "beans_g": -1},
        {"water_ml": 2001, "beans_g": 8},    # over max
        {"water_ml": 30, "beans_g": 501},    # over max
    ])
    def test_coffee_recipe_invalid_numeric(self, kwargs):
        from src.errors import InvalidRecipeError
        with pytest.raises(InvalidRecipeError):
            CoffeeRecipe("x", kwargs["water_ml"], kwargs["beans_g"])

    def test_coffee_recipe_grind_validation(self):
        from src.errors import InvalidRecipeError

        with pytest.raises(InvalidRecipeError):
            CoffeeRecipe("x", 30, 8, grind="COARSE")

        coffee = CoffeeRecipe("x", 30, 8, grind=CoffeeRecipeGrindLevel.COARSE)
        assert coffee.grind is CoffeeRecipeGrindLevel.COARSE

    def test_requires_water_true_false(self):
        coffee1 = CoffeeRecipe("with_water", 30, 0)
        coffee2 = CoffeeRecipe("no_water", 0, 8)

        assert coffee1.requires_water() is True
        assert coffee2.requires_water() is False

    def test_requires_beans_true_false(self):
        coffee1 = CoffeeRecipe("with_beans", 0, 8)
        coffee2 = CoffeeRecipe("no_beans", 30, 0)

        assert coffee1.requires_beans() is True
        assert coffee2.requires_beans() is False

    def test_as_dict_serializes_enum(self):
        coffee = CoffeeRecipe("esp", 30, 8, grind=CoffeeRecipeGrindLevel.FINE)
        coffee_dict = coffee.as_dict()

        assert isinstance(coffee_dict, dict)
        assert coffee_dict["name"] == "esp"
        assert coffee_dict["water_ml"] == 30
        assert coffee_dict["beans_g"] == 8
        assert coffee_dict["grind"] == "FINE"

    def test_immutable_recipe(self):
        coffee = CoffeeRecipe("immutable", 30, 8)
        with pytest.raises((FrozenInstanceError, AttributeError)):
            coffee.water_ml = 40

    def test_repr_contains_key_fields(self):
        coffee = CoffeeRecipe("reprtest", 45, 7,
                              grind=CoffeeRecipeGrindLevel.MEDIUM)
        rep = repr(coffee)
        assert "CoffeeRecipe" in rep
        assert "reprtest" in rep
        assert "45" in rep
        assert "7" in rep
        # grind name should appear as well (or its string representation)
        assert "MEDIUM" in rep or "CoffeeRecipeGrindLevel.MEDIUM" in rep

    def test_equality_and_hash(self):
        coffee1 = CoffeeRecipe("espresso", 30, 8,
                               grind=CoffeeRecipeGrindLevel.FINE)

        coffee2 = CoffeeRecipe("espresso", 30, 8,
                               grind=CoffeeRecipeGrindLevel.FINE)

        coffee3 = CoffeeRecipe("espresso", 40, 8,
                               grind=CoffeeRecipeGrindLevel.FINE)

        # equality for identical fields
        assert coffee1 == coffee2
        assert hash(coffee1) == hash(coffee2)

        # different when a field differs
        assert coffee1 != coffee3
