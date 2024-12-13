import panel as pn
from pyfoodopt import *
from config import *
from components.food_box import FoodBox
from components.food_boxes_container import *
from components.nutrient_constraint_widget import NutrientConstraintWidget
from components.nutrient_constraints import NutrientConstraints
from components.optimize_button import OptimizeButton
from components.restriction_checkbox import RestrictionCheckBox

from results import *
from instructions import instructions
from config_tabs import ConfigTabs
from navbar import navbar
from config import *

pn.extension("tabulator")
# pn.extension(design="bootstrap")

nb = NutrientBank()
nb.build_nutrient_bank_from_csv("data/nutrients_no_duplicate_nbrs.csv")
constraints = Constraints()
constraints.add_nutrient_constraints_from_json("data/nutrient_constraints_2.json")
pantry = Pantry()
pantry.build_pantry_from_json("data/food_data.json")

instructions_wrapper = pn.FlexBox(
    instructions,
    flex_direction="column",
    justify_content="center",
    align_items="center",
    sizing_mode="stretch_width",
    flex_wrap="nowrap",
)


nutrient_constraints_widgets = NutrientConstraints(
    constraints=constraints, nutrient_bank=nb
)

nutrient_config_tab = pn.FlexBox(
    nutrient_constraints_widgets,
    name="Constraints",
)

food_config = FoodConfig(
    food_restriction_name_mappings=FOOD_RESTRICTION_NAME_MAPPINGS, pantry=pantry
)

config_tabs = pn.Tabs(("Foods", food_config), nutrient_config_tab)

results_container = ResultsContainer()


def optimize(event):
    nutrient_constraints = nutrient_constraints_widgets.get_constraints()
    nutrient_constraints = Constraints(nutrient_constraints=nutrient_constraints)
    active_food_fdc_ids = food_config.get_active_foods_fdc_ids()
    pantry.set_active_foods(active_food_fdc_ids)

    fo = FoodOptimizer(pantry=pantry, constraints=nutrient_constraints)

    # Foods don't seem to have foods with ids in the combined constraints (omega-3, omega-6)
    status = fo.optimize()

    ov = fo.get_optimal_values()

    results = Results(food_optimizer=fo, nutrient_bank=nb)

    results_container.add_result(results)


optimize_button = OptimizeButton(on_click=optimize)

config = pn.Column(
    instructions,
    optimize_button,
    config_tabs,
    width=CONFIG_RESULTS_WIDTH,
    margin=(25, 0),
    styles={
        # "background-color": "lightgrey",
        "border": "1px solid black",
        "border-radius": "25px",
        "padding": "10px 25px",
    },
)

config_wrapper = config

app_content = pn.FlexBox(
    config_wrapper,
    results_container,
    flex_direction="row",
    justify_content="space-evenly",
)

app = pn.FlexBox(
    navbar,
    app_content,
    flex_direction="column",
    align_items="center",
    align_content="center",
    sizing_mode="stretch_width",
)

app.servable()
