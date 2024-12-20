import param
import panel as pn
from panel.viewable import Viewer
from components.food_box import FoodBox
from pyfoodopt import BaseFood, Pantry
import pandas as pd
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
from config import *


class RestrictionCheckBox(pn.widgets.Checkbox):
    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click
        self.rx.watch(self._on_click, "value")


class RestrictionChecks(Viewer):

    food_restriction_name_mappings = param.Dict(default={})

    def __init__(self, on_click, **params):
        super().__init__(**params)
        self._on_click = on_click

    def _layout(self):
        return pn.GridBox(
            *[
                RestrictionCheckBox(
                    name=self.food_restriction_name_mappings[rd],
                    on_click=lambda event, rd=rd: self._on_click(event, rd),
                )
                for rd in self.food_restriction_name_mappings
            ],
            ncols=6,
        )

    def __panel__(self):
        return self._layout


class FoodBoxesList(param.Parameterized):

    food_boxes = param.List(item_type=FoodBox)
    visible_food_boxes = param.List(item_type=FoodBox, default=[])

    def __init__(self, **params):
        super().__init__(**params)
        self.visible_food_boxes = self.food_boxes

    def update_visible_food_boxes(
        self, search_term: str = "", dropdown_category: str = None
    ):
        if search_term == "":
            self.visible_food_boxes = self.food_boxes
        else:
            self.visible_food_boxes = [
                fb for fb in self.food_boxes if search_term in fb.food.food_name
            ]


class FoodsContainer(Viewer):

    pantry = param.ClassSelector(class_=Pantry)

    def handle_restriction_checkbox_clicked(self, event, restriction_name):
        pass

    def get_active_foods_fdc_ids(self, *args):
        pass

    def __panel__(self):
        pass


class FoodTabulatorContainer(FoodsContainer):

    def __init__(self, **params):
        super().__init__(**params)
        self.food_tabulator = self.get_food_tabulator()

    def row_content(row):
        link = f"https://fdc.nal.usda.gov/food-details/{row['fdc_id']}/nutrients?printable=true"
        return pn.pane.HTML(
            f'<iframe src="{link}" width="100%" height="200px"></iframe>',
            sizing_mode="stretch_width",
        )
        # with open("nutrition_facts.html", "r") as file:
        #     nutrition_facts = pn.pane.HTML(file.read())
        # return nutrition_facts

        # return pn.pane.Markdown(f"# {row['food_name']}")

    def get_food_tabulator(self):
        foods = {
            fdc_id: {"food_name": food.food_name, "price": food.price.price_per_100_g}
            for fdc_id, food in self.pantry.foods.items()
        }
        foods_df = pd.DataFrame(foods).T
        foods_df["active"] = True
        foods_df.index.name = "fdc_id"

        tabulator = pn.widgets.Tabulator(
            foods_df.reset_index(),
            selectable="checkbox",
            row_content=FoodTabulatorContainer.row_content,
            show_index=False,
            formatters={
                "price": NumberFormatter(format="0.00"),
                "active": BooleanFormatter(),
                "fdc_id": NumberFormatter(format="0"),
            },
            stylesheets=[TABULATOR_STYLESHEET],
        )
        return tabulator

    def __panel__(self):
        return self.food_tabulator


class FoodBoxesContainer(Viewer):

    food_boxes_list = param.ClassSelector(class_=FoodBoxesList)

    def __init__(self, **params):
        super().__init__(**params)
        self.food_config_search_box = pn.widgets.AutocompleteInput(
            placeholder="Search Foods",
            options=[fb.food.food_name for fb in self.food_boxes_list.food_boxes],
            case_sensitive=False,
            search_strategy="includes",
            restrict=False,
        )

        def clear_search_box(event):
            self.food_config_search_box.value = ""

        self.search_box_clear_button = pn.widgets.Button(
            name="Clear", button_type="primary", on_click=clear_search_box
        )
        self.food_config_category_dropdown = pn.widgets.Select(
            options=["Fruits", "Vegetables", "Meats", "Dairy", "Grains", "Legumes"],
        )
        pn.bind(
            self.food_boxes_list.update_visible_food_boxes,
            self.food_config_search_box.param.value,
            watch=True,
        )

    @param.depends("food_boxes_list.visible_food_boxes")
    def _layout(self):
        return pn.Column(
            pn.Row(self.food_config_search_box, self.search_box_clear_button),
            self.food_config_category_dropdown,
            pn.FlexBox(
                *self.food_boxes_list.visible_food_boxes,
                flex_direction="row",
                justify_content="flex-start",
                sizing_mode="stretch_width",
            ),
            height=800,
            scroll=True,
        )

    def handle_restriction_checkbox_clicked(self, event, restriction_name):
        for food_box in self.food_boxes_list.food_boxes:
            food_box.handle_checkbox_click(event, restriction_name)

    def get_active_foods_fdc_ids(self, *args):
        return [
            fb.food.fdc_id
            for fb in self.food_boxes_list.food_boxes
            if fb.toggle.name == "Enabled"
        ]

    def __panel__(self):
        return self._layout


class FoodConfig(Viewer):

    food_restriction_name_mappings = param.Dict(default={})
    pantry = param.ClassSelector(class_=Pantry)

    def __init__(self, **params):
        super().__init__(**params)
        self.food_boxes_container = FoodBoxesContainer(
            food_boxes_list=FoodBoxesList(
                food_boxes=[
                    FoodBox(food=food) for food in list(self.pantry.foods.values())
                ]
            )
        )

        self.restriction_checks = RestrictionChecks(
            on_click=self.food_boxes_container.handle_restriction_checkbox_clicked,
            food_restriction_name_mappings=self.food_restriction_name_mappings,
        )

    def _layout(self):

        food_config_foods = pn.FlexBox(
            self.food_boxes_container,
            flex_direction="column",
            sizing_mode="stretch_width",
        )

        food_config_tab = pn.FlexBox(
            self.restriction_checks,
            food_config_foods,
            name="Foods",
        )

        return food_config_tab

    def get_active_foods_fdc_ids(self, *args):
        return self.food_boxes_container.get_active_foods_fdc_ids()

    def __panel__(self):
        return self._layout
