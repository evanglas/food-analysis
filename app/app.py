import panel as pn
from pyfoodopt import *
from config import *
from components.food_box import FoodBox
from components.food_boxes_container import FoodBoxesContainer
from components.nutrient_constraint_widget import NutrientConstraintWidget
from components.nutrient_constraints import NutrientConstraints
from components.optimize_button import OptimizeButton
from components.restriction_checkbox import RestrictionCheckBox

from results import *
from instructions import instructions
from config_tabs import ConfigTabs
from navbar import navbar

pn.extension("tabulator")

nb = NutrientBank()
nb.build_nutrient_bank_from_csv("data/nutrients_no_duplicate_nbrs.csv")
constraints = Constraints()
constraints.add_nutrient_constraints_from_json("data/nutrient_constraints_2.json")
pantry = Pantry()
pantry.build_pantry_from_json("data/food_data.json")
FOOD_RESTRICTIONS = [r for r in FoodRestrictions.param.objects() if r != "name"]


FOOD_RESTRICTION_NAME_MAPPINGS = {
    "vegan": "Vegan",
    "vegetarian": "Vegetarian",
    "pescatarian": "Pescatarian",
    "keto": "Keto",
    "halal": "Halal",
    "kosher": "Kosher",
    "dairy_free": "Dairy-Free",
    "gluten_free": "Gluten-Free",
    "soy_free": "Soy-Free",
    "wheat_free": "Wheat-Free",
    "egg_free": "Egg-Free",
    "fish_shellfish_free": "Fish/Shellfish-Free",
    "nut_free": "Nut-Free",
}

instructions_wrapper = pn.FlexBox(
    instructions,
    flex_direction="column",
    justify_content="center",
    align_items="center",
    sizing_mode="stretch_width",
    flex_wrap="nowrap",
    # align_content="center",
)


food_config_search_box = pn.widgets.TextInput(placeholder="Search Foods")

food_config_category_dropdown = pn.widgets.Select(
    options=["Fruits", "Vegetables", "Meats", "Dairy", "Grains", "Legumes"],
)

food_boxes = [FoodBox(food=food) for fdc_id, food in pantry.foods.items()]


food_boxes_wrapper = FoodBoxesContainer(food_boxes=food_boxes)

common_diet_checks = pn.GridBox(
    *[
        RestrictionCheckBox(
            name=FOOD_RESTRICTION_NAME_MAPPINGS[rd],
            on_click=lambda event, rd=rd: food_boxes_wrapper.handle_restriction_checkbox_clicked(
                event, rd
            ),
        )
        for rd in FOOD_RESTRICTIONS
    ],
    ncols=6,
)

general_food_config_widgets = pn.FlexBox(common_diet_checks)

active_button = pn.widgets.Button(
    name="Active",
    button_type="primary",
    on_click=food_boxes_wrapper.get_active_foods_fdc_ids,
)

food_config_foods = pn.FlexBox(
    food_config_search_box,
    food_config_category_dropdown,
    food_boxes_wrapper,
    flex_direction="column",
    sizing_mode="stretch_width",
)

food_config_tab = pn.FlexBox(
    general_food_config_widgets,
    food_config_foods,
    name="Foods",
)


nutrient_constraints_widgets = NutrientConstraints(constraints=constraints)

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

    results = Results(food_optimizer=fo)

    results_tabs.add_result(results)


optimize_button = OptimizeButton(on_click=optimize)

config_tabs = ConfigTabs(food_config_tab, nutrient_config_tab)

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
