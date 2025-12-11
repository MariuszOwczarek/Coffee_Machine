# run_coffee_cli.py
"""
Prosty interaktywny CLI do eksperymentowania z SimpleCoffeeMachine.
Uruchom: python run_coffee_cli.py
"""

from datetime import timedelta
from src.coffee_machine.coffee_machine import SimpleCoffeeMachine
from src.coffee_machine.coffee_recipe import CoffeeRecipe, CoffeeRecipeGrindLevel
from src.coffee_machine.water_tank import WaterTank
from src.coffee_machine.bean_container import BeanContainer
from src.coffee_machine.policies.brew_policy import DefaultBrewPolicy, BrewDecision
from src.coffee_machine.policies.cleaning_policy import DefaultCleaningPolicy
from src.coffee_machine.policies.refill_policy import CapRefillPolicy

# --- przykładowe receptury ---
RECIPES = {
    "espresso": CoffeeRecipe("espresso", water_ml=30, beans_g=8, grind=CoffeeRecipeGrindLevel.FINE),
    "lungo": CoffeeRecipe("lungo", water_ml=60, beans_g=8, grind=CoffeeRecipeGrindLevel.FINE),
    "americano": CoffeeRecipe("americano", water_ml=120, beans_g=8, grind=CoffeeRecipeGrindLevel.MEDIUM),
    "ristretto": CoffeeRecipe("ristretto", water_ml=20, beans_g=8, grind=CoffeeRecipeGrindLevel.FINE),
}

def print_help():
    print("""
Komendy:
  list                       - pokaż dostępne przepisy
  select <name>              - wybierz przepis (np. select espresso)
  brew                       - spróbuj zaparzyć wybrany przepis
  refill_water <ml>          - dolej wodę (np. refill_water 200)
  refill_beans <g>           - dodaj ziarna (np. refill_beans 50)
  clean                      - wykonaj czyszczenie (reset dirty_count)
  status                     - pokaż stan maszyny i zasobów
  help                       - pokaż tę pomoc
  quit | q                   - wyjście
""")

def print_status(machine):
    print("STATE:", machine.state)
    print("Active recipe:", machine.active_recipe.name if machine.active_recipe else None)
    print("Dirty count:", machine.dirty_count)
    print("Last cleaned:", machine.last_cleaned_ts)
    print("Water: {}/{}".format(machine.water_tank.current_level, machine.water_tank.maximum_level))
    print("Beans: {}/{}".format(machine.bean_container.current_level, machine.bean_container.maximum_level))
    print("Cleaning scheduled:", getattr(machine, "cleaning_scheduled", False))

def main():
    # inicjalizacja maszynki z domyślnymi politykami
    water = WaterTank(maximum_level=500, initial_level=150)
    beans = BeanContainer(maximum_grams=500, initial_grams=50)

    brew_policy = DefaultBrewPolicy(clean_threshold=5)
    cleaning_policy = DefaultCleaningPolicy(schedule_threshold=3, immediate_threshold=6, max_time_between_cleans=timedelta(days=7))
    refill_policy = CapRefillPolicy()

    machine = SimpleCoffeeMachine(water, beans, brew_policy, cleaning_policy, refill_policy)

    print("Simple Coffee CLI. Wpisz 'help' aby zobaczyć dostępne komendy.")
    print_status(machine)

    while True:
        try:
            raw = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nKoniec (CTRL-C/EOF).")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        try:
            if cmd in ("quit", "q"):
                print("Koniec.")
                break

            elif cmd == "help":
                print_help()

            elif cmd == "list":
                print("Dostępne przepisy:")
                for k, r in RECIPES.items():
                    print(f"  {k} — water={r.water_ml}ml beans={r.beans_g}g grind={r.grind.name if r.grind else None}")

            elif cmd == "select":
                if len(parts) < 2:
                    print("Użycie: select <name>")
                    continue
                name = parts[1]
                if name not in RECIPES:
                    print(f"Brak przepisu: {name}")
                    continue
                machine.select_recipe(RECIPES[name])
                print("Wybrano przepis:", name)

            elif cmd == "brew":
                try:
                    result = machine.brew()
                except Exception as exc:
                    # pokaż informację o błędzie, ale nie przerywaj CLI
                    print("Błąd podczas parzenia:", type(exc).__name__, exc)
                    continue

                # result to BrewDecision albo enum name w SimpleCoffeeMachine
                if isinstance(result, BrewDecision):
                    print("Result:", result.name)
                else:
                    # fallback — SimpleCoffeeMachine zwraca pewne stringi w minimalnej wersji
                    print("Result:", result)
                print_status(machine)

            elif cmd == "refill_water":
                if len(parts) < 2:
                    print("Użycie: refill_water <ml>")
                    continue
                try:
                    amount = int(parts[1])
                except ValueError:
                    print("Nieprawidłowa liczba")
                    continue
                try:
                    res = machine.refill_water(amount)
                    # refill_policy może zwracać enum lub zasób również
                    print("Refill result:", res)
                except Exception as exc:
                    print("Błąd refill:", type(exc).__name__, exc)
                print_status(machine)

            elif cmd == "refill_beans":
                if len(parts) < 2:
                    print("Użycie: refill_beans <g>")
                    continue
                try:
                    amount = int(parts[1])
                except ValueError:
                    print("Nieprawidłowa liczba")
                    continue
                try:
                    res = machine.refill_beans(amount)
                    print("Refill result:", res)
                except Exception as exc:
                    print("Błąd refill:", type(exc).__name__, exc)
                print_status(machine)

            elif cmd == "clean":
                machine.clean()
                print("Wykonano czyszczenie.")
                print_status(machine)

            elif cmd == "status":
                print_status(machine)

            else:
                print("Nieznana komenda. Wpisz 'help'.")
        except Exception as exc:
            # bezpieczeństwo: łapiemy wszystko, żeby CLI nie padł
            print("Nieoczekiwany błąd:", type(exc).__name__, exc)

if __name__ == "__main__":
    main()
