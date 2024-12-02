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


nb = NutrientBank()
nb.build_nutrient_bank_from_csv("data/nutrients_no_duplicate_nbrs.csv")
constraints = Constraints()
constraints.add_nutrient_constraints_from_json("data/nutrient_constraints_2.json")
# constraints.add_nutrient_constraints_from_csv("../data/nutrient_constraints.csv")
pantry = Pantry()
pantry.build_pantry_from_json("data/food_data.json")
FOOD_RESTRICTIONS = [r for r in FoodRestrictions.param.objects() if r != "name"]
# fo = FoodOptimizer(pantry=p, constraints=constraints)
# fo.optimize()

vegan_check = pn.widgets.Checkbox(name="Vegan")

vegetarian_check = pn.widgets.Checkbox(name="Vegetarian")

pescatarian_check = pn.widgets.Checkbox(name="Pescatarian")

keto_check = pn.widgets.Checkbox(name="Keto")

halal_check = pn.widgets.Checkbox(name="Halal")

kosher_check = pn.widgets.Checkbox(name="Kosher")

label_common_diet_checks = pn.pane.Str("Common Diets")

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
    sizing_mode="fixed",
    styles={
        "background-color": "lightgrey",
        "border-radius": "25px",
        "padding": "25px",
    },
)

results_wrapper = pn.FlexBox(
    instructions,
    flex_direction="column",
    justify_content="center",
    align_items="center",
    sizing_mode="stretch_width",
    flex_wrap="nowrap",
    # align_content="center",
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
        self.restrictions = set()

    def handle_checkbox_click(self, event, restriction_name):
        if event:
            if not self.food.food_meta.restrictions.__getattribute__(restriction_name):
                self.disable_toggle()
                self.restrictions.add(restriction_name)
        else:
            if not self.food.food_meta.restrictions.__getattribute__(restriction_name):
                self.restrictions.remove(restriction_name)
                if len(self.restrictions) == 0:
                    self.enable_toggle()

    def enable_toggle(self):
        self.toggle.name = "Enabled"
        self.toggle.stylesheets = FoodBox.enabled_stylesheets

    def disable_toggle(self):
        self.toggle.name = "Disabled"
        self.toggle.stylesheets = FoodBox.disabled_stylesheets

    def _on_click(self, event):
        if self.toggle.name == "Enabled":
            self.enable_toggle()
        else:
            self.disable_toggle()

    def __panel__(self):
        return self._layout


class RestrictionCheckBox(pn.widgets.Checkbox):
    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click
        self.rx.watch(self._on_click, "value")


food_config_search_box = pn.widgets.TextInput(placeholder="Search Foods")

food_config_category_dropdown = pn.widgets.Select(
    options=["Fruits", "Vegetables", "Meats", "Dairy", "Grains", "Legumes"],
)

food_boxes = [FoodBox(food=food) for fdc_id, food in pantry.foods.items()]


class FoodBoxesContainer(Viewer):

    food_boxes = param.List(class_=FoodBox)

    def __init__(self, **params):
        super().__init__(**params)
        self.food_boxes = food_boxes
        self._layout = pn.FlexBox(
            *self.food_boxes,
            flex_direction="row",
            justify_content="flex-start",
            sizing_mode="stretch_width",
        )

    def handle_restriction_checkbox_clicked(self, event, restriction_name):
        for food_box in food_boxes:
            food_box.handle_checkbox_click(event, restriction_name)

    def get_active_foods_fdc_ids(self, *args):
        return [fb.food.fdc_id for fb in self.food_boxes if fb.toggle.name == "Enabled"]

    def __panel__(self):
        return self._layout


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
    active_button,
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


class NutrientConstraintWidget(Viewer):

    label = param.String()
    lower_bound = param.Number(default=0)
    upper_bound = param.Number(default=None)
    equality = param.Number(default=None)

    def __init__(self, nutrient_nbrs: tuple, **params):
        super().__init__(**params)
        if self.lower_bound is not None:
            self.lower_bound = round(self.lower_bound, 1)
        if self.upper_bound is not None:
            self.upper_bound = round(self.upper_bound, 1)
        if self.equality is not None:
            self.equality = round(self.equality, 1)
        self.nutrient_nbrs = nutrient_nbrs
        self.layout = self._create_layout()

    def _create_layout(self):
        label_widget = pn.pane.Markdown(f"**{self.label}**", width=200)
        lower_input = pn.widgets.FloatInput.from_param(
            self.param.lower_bound, width=100
        )
        equality_input = pn.widgets.FloatInput.from_param(
            self.param.equality, width=100
        )
        upper_input = pn.widgets.FloatInput.from_param(
            self.param.upper_bound, width=100
        )

        input_row = pn.Row(label_widget, lower_input, equality_input, upper_input)
        return input_row

    def get_constraints(self):
        nbr_to_coefficient = {nbr: 1 for nbr in self.nutrient_nbrs}
        constraints = {self.nutrient_nbrs: {}}
        if self.lower_bound is not None:
            constraints[self.nutrient_nbrs]["lower_bound"] = NutrientConstraint(
                    constraint_type="lower_bound",
                    constraint_value=self.lower_bound,
                    nbr_to_coefficient=nbr_to_coefficient,
                )
        if self.upper_bound is not None:
            constraints[self.nutrient_nbrs]["upper_bound"] = NutrientConstraint(
                    constraint_type="upper_bound",
                    constraint_value=self.upper_bound,
                    nbr_to_coefficient=nbr_to_coefficient,
                )
        if self.equality is not None:
            constraints[self.nutrient_nbrs]["equality"] = NutrientConstraint(
                    constraint_type="equality",
                    constraint_value=self.equality,
                    nbr_to_coefficient=nbr_to_coefficient,
                )
        return constraints

    def __panel__(self):
        return self.layout


class NutrientConstraints(Viewer):

    constraints = param.ClassSelector(class_=Constraints)

    def __init__(self, **params):
        super().__init__(**params)
        self.constraint_widgets = []
        for (
            nutrient_nbrs,
            nbr_constraints,
        ) in self.constraints.nutrient_constraints.items():
            label = " + ".join(
                [nb.get_nutrient_by_id(nbr).nutrient_name for nbr in nutrient_nbrs]
            )
            label += f" ({nb.get_nutrient_by_id(nutrient_nbrs[0]).unit_name})"
            lower_bound = nbr_constraints.get("lower_bound")
            upper_bound = nbr_constraints.get("upper_bound")
            equality = nbr_constraints.get("equality")

            if lower_bound is not None:
                lower_bound = lower_bound.constraint_value
            else:
                lower_bound = 0
            if upper_bound is not None:
                upper_bound = upper_bound.constraint_value
            if equality is not None:
                equality = equality.constraint_value
            self.constraint_widgets.append(
                NutrientConstraintWidget(
                    nutrient_nbrs=nutrient_nbrs,
                    label=label,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    equality=equality,
                )
            )
        self._layout = pn.FlexBox(
            *self.constraint_widgets,
            flex_direction="column",
            sizing_mode="stretch_width",
        )

    def get_constraints(self):
        constraints = {}
        for nutrient_constraint_widget in self.constraint_widgets:
            constraints.update(nutrient_constraint_widget.get_constraints())
        return constraints

    def __panel__(self):
        return self._layout


nutrient_constraints_widgets = NutrientConstraints(constraints=constraints)

nutrient_config_tab = pn.FlexBox(
    nutrient_constraints_widgets,
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
    margin=(50, 0),
    sizing_mode="stretch_height",
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

    ov.to_csv('ov.csv')

    # print(fo.get_optimal_values())


optimize_button = pn.widgets.Button(
    name="Optimize", button_type="primary", on_click=optimize
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
