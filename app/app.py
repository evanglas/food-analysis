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
    # align_content="center",
)


nutrient_constraints_widgets = NutrientConstraints(
    constraints=constraints, nutrient_bank=nb
)

nutrient_config_tab = pn.FlexBox(
    nutrient_constraints_widgets,
    name="Constraints",
)

results_tabs = ResultsTabs()


def optimize(event):
    nutrient_constraints = nutrient_constraints_widgets.get_constraints()
    nutrient_constraints = Constraints(nutrient_constraints=nutrient_constraints)
    active_food_fdc_ids = food_boxes_wrapper.get_active_foods_fdc_ids()
    pantry.set_active_foods(active_food_fdc_ids)

    # print(pantry.get_food_by_fdc_id(168409).food_nutrition)

    fo = FoodOptimizer(pantry=pantry, constraints=nutrient_constraints)

    # Foods don't seem to have foods with ids in the combined constraints (omega-3, omega-6)
    status = fo.optimize()

    ov = fo.get_optimal_values()

    results = Results(food_optimizer=fo, nutrient_bank=nb)

    results_tabs.add_result(results)


optimize_button = OptimizeButton(on_click=optimize)

food_config_tab = FoodConfig(
    food_restriction_name_mappings=FOOD_RESTRICTION_NAME_MAPPINGS, pantry=pantry
)

config_tabs = pn.Tabs(("Foods", food_config_tab), nutrient_config_tab)

config = pn.Column(
    instructions,
    optimize_button,
    config_tabs,
    # flex_direction="column",
    # align_items="center",
    # align_content="center",
    # sizing_mode="fixed",
    width=CONFIG_RESULTS_WIDTH,
    margin=(50, 50),
    # sizing_mode="stretch_height",
    styles={
        "background-color": "lightgrey",
        "border-radius": "25px",
        "padding": "25px",
    },
)

# config_wrapper = pn.Column(
#     config,
#     flex_direction="row",
#     margin=(0,50),
#     width=750,
# )

config_wrapper = config

results_wrapper = pn.FlexBox(
    results_tabs,
    flex_direction="column",
    align_items="center",
    align_content="center",
    # sizing_mode="fixed",
    width=CONFIG_RESULTS_WIDTH,
    margin=(50, 0),
    # sizing_mode="stretch_height",
    styles={
        "background-color": "lightgrey",
        "border-radius": "25px",
        "padding": "25px",
    },
)

app_content = pn.FlexBox(
    # instructions_wrapper,
    config_wrapper,
    results_wrapper,
    flex_direction="row",
    # flex_wrap="nowrap",
    justify_content="left",
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
