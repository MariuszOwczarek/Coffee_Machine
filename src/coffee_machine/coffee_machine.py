from datetime import datetime
from src.coffee_machine.coffee_recipe import CoffeeRecipe
from src.coffee_machine.policies.brew_policy import BrewDecision
from src.coffee_machine.policies.cleaning_policy import CleaningAction


class SimpleCoffeeMachine:
    def __init__(self, water_tank, bean_container,
                 brew_policy, cleaning_policy, refill_policy):
        self.water_tank = water_tank
        self.bean_container = bean_container
        self.brew_policy = brew_policy
        self.cleaning_policy = cleaning_policy
        self.refill_policy = refill_policy

        self.state = "IDLE"
        self.active_recipe = None
        self.dirty_count = 0
        self.last_cleaned_ts = None
        self.cleaning_scheduled = False  # flag set when cleaning is scheduled (SCHEDULE)

    def select_recipe(self, recipe: CoffeeRecipe):
        self.active_recipe = recipe

    def brew(self):
        if self.active_recipe is None:
            raise RuntimeError("No recipe selected")

        recipe = self.active_recipe

        decision = self.brew_policy.can_brew(
            recipe,
            self.water_tank.current_level,
            self.bean_container.current_level,
            maintenance_state={"dirty_count": self.dirty_count}
        )

        if decision is not BrewDecision.OK:
            self.state = decision.name
            return decision

        if recipe.requires_water():
            self.water_tank.consume_water(recipe.water_ml)

        if recipe.requires_beans():
            self.bean_container.consume_beans(recipe.beans_g)

        # update maintenance
        self.dirty_count += 1

        cleaning_action = self.cleaning_policy.evaluate(
            self.dirty_count, self.last_cleaned_ts
        )

        if cleaning_action is CleaningAction.IMMEDIATE:
            self.state = "NEEDS_CLEANING"
        elif cleaning_action is CleaningAction.SCHEDULE:
            # set scheduled flag but remain IDLE
            self.cleaning_scheduled = True
            self.state = "IDLE"
        else:
            self.state = "IDLE"

        return BrewDecision.OK

    def clean(self):
        """
        Perform cleaning now: reset dirty_count and record timestamp.
        After cleaning, machine is IDLE and scheduled flag is cleared.
        """
        self.dirty_count = 0
        self.last_cleaned_ts = datetime.utcnow()
        self.cleaning_scheduled = False
        self.state = "IDLE"

    def schedule_cleaning(self):
        """Mark cleaning as scheduled (non-blocking)."""
        self.cleaning_scheduled = True

    def refill_water(self, amount):
        return self.water_tank.refill(amount)

    def refill_beans(self, amount):
        return self.bean_container.refill(amount)
