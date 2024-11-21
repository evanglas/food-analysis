import panel as pn
from panel.viewable import Viewer
from pyfoodopt import *
import pandas as pd
import param
import random

css = """
.tabulator .tabulator-header .tabulator-col .tabulator-col-content .tabulator-col-title
{
white-space: normal;
text-overflow: clip;
}
"""

pn.extension("tabulator")

title_styles = {"font-size": "20px", "font-weight": "bold"}
sidebar_title = pn.pane.Str("Requirements", styles=title_styles)
age_input = pn.widgets.IntInput(name="Age", value=30)
weight_input = pn.widgets.IntInput(name="Weight", value=70)
height_input = pn.widgets.IntInput(name="Height", value=170)
number_demographic_inputs = pn.Column(age_input, weight_input, height_input)

# food_df = pd.read_csv("panel_food_prices_nutrients.csv", index_col=0)
# constraints_df = pd.read_csv("panel_nutrient_constraints.csv", index_col=0)

# constraints = Constraints()
# constraints.add_nutrient_constraints_from_csv("../data/nutrient_constraints.csv")
pantry = Pantry()
pantry.build_pantry_from_csv("data/food_nutrient_amounts.csv")
# fo = FoodOptimizer(pantry=p, constraints=constraints)
# fo.optimize()


class LabeledRBGroup(pn.Column):
    def __init__(self, options: list[str], label: str, **kwargs):
        self.label = pn.pane.Str(label)
        self.radio_buttons = pn.widgets.RadioButtonGroup(
            options=options, name=label, **kwargs
        )
        super().__init__(self.label, self.radio_buttons)


sex_radio_buttons = LabeledRBGroup(options=["Male", "Female"], label="Sex")

activity_radio_buttons = LabeledRBGroup(
    options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
    label="Activity",
)


weight_goal_radio_buttons = LabeledRBGroup(
    options=["Lose", "Maintain", "Gain"], label="Weight Goal"
)

select_demographic_widgets = pn.Column(
    sex_radio_buttons, activity_radio_buttons, weight_goal_radio_buttons
)

demographic_widgets = pn.Column(number_demographic_inputs, select_demographic_widgets)

vegan_check = pn.widgets.Checkbox(name="Vegan")

vegetarian_check = pn.widgets.Checkbox(name="Vegetarian")

pescatarian_check = pn.widgets.Checkbox(name="Pescatarian")

keto_check = pn.widgets.Checkbox(name="Keto")

halal_check = pn.widgets.Checkbox(name="Halal")

kosher_check = pn.widgets.Checkbox(name="Kosher")

label_common_diet_checks = pn.pane.Str("Common Diets")

common_diet_checks = pn.GridBox(
    vegan_check,
    vegetarian_check,
    pescatarian_check,
    keto_check,
    halal_check,
    kosher_check,
    ncols=3,
)

label_common_restrictions = pn.pane.Str("Common Restrictions")

low_sodium_check = pn.widgets.Checkbox(name="Low Sodium")

nut_allergy_check = pn.widgets.Checkbox(name="Nut Allergy")

lactose_intolerant_check = pn.widgets.Checkbox(name="Lactose Intolerant")

gluten_free_check = pn.widgets.Checkbox(name="Gluten Free")

label_common_restrictions_checks = pn.pane.Str("Common Restrictions")

common_restrictions_checks = pn.GridBox(
    low_sodium_check,
    nut_allergy_check,
    lactose_intolerant_check,
    gluten_free_check,
    ncols=2,
)


goals_tab = pn.FlexBox(
    demographic_widgets,
    label_common_diet_checks,
    common_diet_checks,
    label_common_restrictions,
    common_restrictions_checks,
    name="Goals",
    flex_direction="column",
    height=300,
)


class food_box(pn.FlexBox):
    def __init__(
        self,
        name: str,
    ):
        super().__init__()


# tabulator = pn.widgets.Tabulator(
#     food_df.T,
#     pagination="local",
#     page_size=10,
#     stylesheets=[":host .tabulator {font-size: 10px;}"],
# )
# styler = tabulator.style

foods_tab = pn.FlexBox(
    "hi",
    name="Foods",
)

contraints_tab = pn.FlexBox("Constraints", name="Constraints")

sidebar_content = pn.layout.Tabs(goals_tab, foods_tab, contraints_tab)

sidebar = pn.FlexBox(
    sidebar_title,
    sidebar_content,
    flex_direction="column",
    height=800,
    styles={"background-color": "grey"},
    sizing_mode="stretch_width",
    flex_wrap="nowrap",
)

results_title = pn.pane.Str("Results", styles=title_styles)

results_diet = pn.FlexBox("Beef", "Potato", "Pepper", flex_direction="column")

results_nutrition = pn.FlexBox("Calories", "Protein", "Fat", flex_direction="column")

results_content = pn.FlexBox(results_diet, results_nutrition)

results = pn.FlexBox(
    results_title,
    results_content,
    flex_direction="column",
    align_items="center",
    sizing_mode="stretch_width",
)

content = pn.GridBox(sidebar, results, ncols=2, sizing_mode="stretch_width")

navbar_title = pn.pane.Str("TOD", styles=title_styles)

navbar = pn.FlexBox(navbar_title, flex_direction="row", justify_content="center")

instructions_markdown = pn.pane.Markdown(
    """
    # TOD: The Optimal Diet
    ---

    ### Use this app to find the unique cost-optimal diet that satisfies all of your core nutritional needs.
    ___

    <br>

    ## Instructions
    1. Select the foods you'd be willing to include in your diet.
    2. Set your nutritional constraints.
    3. Click **Optimize**!

    <br>

    ## How it works?
    - The app uses the [PyFoodOpt](https://coin-or.github.io/pulp/) library to solve a linear programming problem.
    - The problem is to minimize the cost of the diet while satisfying all of the nutritional constraints.
    - Nutritional data is sourced from the [USDA Food Database](https://usda.gov).
    - Pricing data has been set manually to reflect real-world wholesale prices. Pricing assumptions may be changed below.
    - See [about](/about) for more information.

    """
)

instructions = pn.FlexBox(
    instructions_markdown,
    flex_direction="column",
    justify_content="center",
    align_items="center",
    align_content="center",
    margin=(100, 0, 50, 0),
    width=500,
    height=500,
    styles={
        "background-color": "lightgrey",
        "border-radius": "25px",
        "padding": "25px",
    },
)

optimize_button = pn.widgets.Button(name="Optimize", button_type="primary")

results_wrapper = pn.FlexBox(
    instructions,
    flex_direction="column",
    justify_content="center",
    align_items="center",
    sizing_mode="stretch_width",
    flex_wrap="nowrap",
    # align_content="center",
)

general_food_config_widgets = pn.FlexBox(common_diet_checks)

food_config_search_box = pn.widgets.TextInput(placeholder="Search Foods")

food_config_category_dropdown = pn.widgets.Select(
    options=["Fruits", "Vegetables", "Meats", "Dairy", "Grains", "Legumes"],
)


class FoodBox(Viewer):

    food = param.ClassSelector(class_=BaseFood)

    rcolor = lambda: "#%06x" % random.randint(0, 0xFFFFFF)

    enabled_stylesheets = [
        """
    button { background-color: green !important;}
    """
    ]

    disabled_stylesheets = [
        """
        button { background-color: red !important;}
        """
    ]

    def __init__(self, **params):
        super().__init__(**params)
        self.toggle = pn.widgets.Button(
            name="Enabled",
            on_click=self._on_click,
            stylesheets=FoodBox.enabled_stylesheets,
        )
        self._layout = pn.FlexBox(
            pn.pane.Str(self.food.food_name),
            self.toggle,
            flex_direction="column",
            justify_content="center",
            align_items="center",
            align_content="center",
            sizing_mode="fixed",
            width=150,
            height=100,
            margin=10,
            styles={
                "background-color": f"{FoodBox.rcolor()}",
                "border-radius": "10px",
            },
        )

    def _on_click(self, event):
        if self.toggle.name == "Enabled":
            self.toggle.name = "Disabled"
            self.toggle.stylesheets = FoodBox.disabled_stylesheets
        else:
            self.toggle.name = "Enabled"
            self.toggle.stylesheets = FoodBox.enabled_stylesheets

    def __panel__(self):
        return self._layout


food_boxes = [FoodBox(food=food) for fdc_id, food in pantry.foods.items()]

food_boxes_wrapper = pn.FlexBox(
    *food_boxes,
    flex_direction="row",
    justify_content="flex-start",
    sizing_mode="stretch_width",
    # flex_wrap="nowrap",
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

nutrient_config_tab = pn.FlexBox(
    "hi",
    name="Constraints",
)

config_tabs = pn.Tabs(
    food_config_tab,
    nutrient_config_tab,
    # tabs_location="left",
    # width=500,
    # height=500,
    # margin=(50, 0),
    # styles={
    #     "background-color": "lightgrey",
    #     "border-radius": "25px",
    #     "padding": "25px",
    # },
)

config = pn.FlexBox(
    config_tabs,
    flex_direction="column",
    # align_items="center",
    # align_content="center",
    # sizing_mode="fixed",
    width=800,
    height=800,
    margin=(50, 0),
    styles={
        "background-color": "lightgrey",
        "border-radius": "25px",
        "padding": "25px",
    },
)

config_wrapper = pn.FlexBox(
    config,
    flex_direction="row",
    justify_content="center",
)

app = pn.FlexBox(
    navbar,
    results_wrapper,
    optimize_button,
    config_wrapper,
    flex_direction="column",
    align_items="center",
    align_content="center",
    sizing_mode="stretch_width",
)

app.servable()
