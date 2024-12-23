import param
import panel as pn
from panel.viewable import Viewer
from components.food_box import FoodBox
from pyfoodopt import BaseFood, Pantry
import pandas as pd
from bokeh.models.widgets.tables import (
    NumberFormatter,
    BooleanFormatter,
    HTMLTemplateFormatter,
)

# from nutrition_facts import NutritionFactsView
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

    food_link_formatter = HTMLTemplateFormatter(template="<%= value %>")

    def get_food_link_url(self, row):
        link = f'<a href="https://fdc.nal.usda.gov/food-details/{row['fdc_id']}/nutrients" target="_blank">{row['food_name']}</a>'
        return link

    def __init__(self, **params):
        super().__init__(**params)
        self.active_restrictions = {fdc_id: set() for fdc_id in self.pantry.foods}
        self.food_tabulator = self.get_food_tabulator()

    def get_food_tabulator(self):
        foods = {
            fdc_id: {"food_name": food.food_name, "price": food.price.price_per_100_g}
            for fdc_id, food in self.pantry.foods.items()
        }
        foods_df = pd.DataFrame(foods).T
        foods_df.index.name = "fdc_id"
        foods_df = foods_df.reset_index(drop=False)
        foods_df["food_link"] = foods_df.apply(self.get_food_link_url, axis=1)

        tabulator = pn.widgets.Tabulator(
            foods_df,
            selectable="checkbox",
            hidden_columns=[
                c for c in foods_df.columns if c not in ["food_link", "price"]
            ],
            # row_content=self.row_content,
            show_index=False,
            formatters={
                "price": NumberFormatter(format="0.00"),
                # "active": BooleanFormatter(),
                "food_link": FoodTabulatorContainer.food_link_formatter,
            },
            titles={
                "food_link": "Food",
                "price": "Price ($/100g)",
                # "active": "Active",
            },
            stylesheets=[TABULATOR_STYLESHEET],
        )
        tabulator.selection = list(tabulator.value.index)
        return tabulator

    def get_active_foods_fdc_ids(self, *args):
        return self.food_tabulator.value.loc[
            self.food_tabulator.selection
        ].fdc_id.tolist()

    def handle_restriction_for_fdc_id(self, event, restriction_name, fdc_id):
        food = self.pantry.get_food_by_fdc_id(fdc_id)
        if event:
            if not food.food_meta.restrictions.__getattribute__(restriction_name):
                self.active_restrictions[fdc_id].add(restriction_name)
        else:
            if not food.food_meta.restrictions.__getattribute__(restriction_name):
                self.active_restrictions[fdc_id].remove(restriction_name)
        if len(self.active_restrictions[fdc_id]) == 0:
            return True
        else:
            return False

    def handle_restriction_checkbox_clicked(self, event, restriction_name):
        is_selected = self.food_tabulator.value.fdc_id.apply(
            lambda x: self.handle_restriction_for_fdc_id(event, restriction_name, x)
        )
        new_selection = self.food_tabulator.value[is_selected].index.tolist()
        self.food_tabulator.selection = new_selection

    def __panel__(self):
        return self.food_tabulator


class ChecksAndFoodsContainer(Viewer):

    food_tabulator_container = param.ClassSelector(class_=FoodTabulatorContainer)

    def __init__(self, **params):
        super().__init__(**params)
        self.restriction_checks = RestrictionChecks(
            on_click=self.food_tabulator_container.handle_restriction_checkbox_clicked,
            food_restriction_name_mappings=FOOD_RESTRICTION_NAME_MAPPINGS,
        )

    def _layout(self):
        return pn.Column(
            self.restriction_checks,
            self.food_tabulator_container,
        )

    def get_active_foods_fdc_ids(self, *args):
        return self.food_tabulator_container.get_active_foods_fdc_ids()

    def __panel__(self):
        return self._layout


class FoodBoxesContainer(FoodsContainer):

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
    show_tabulator = param.Boolean(default=True)

    def __init__(self, **params):
        super().__init__(**params)

        if self.show_tabulator:
            self.foods_container = FoodTabulatorContainer(pantry=self.pantry)
        else:
            self.foods_container = FoodBoxesContainer(
                food_boxes_list=FoodBoxesList(
                    food_boxes=[
                        FoodBox(food=food) for food in list(self.pantry.foods.values())
                    ]
                )
            )

        self.restriction_checks = RestrictionChecks(
            on_click=self.foods_container.handle_restriction_checkbox_clicked,
            food_restriction_name_mappings=self.food_restriction_name_mappings,
        )

    def _layout(self):

        food_config_foods = pn.FlexBox(
            self.foods_container,
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
        return self.foods_container.get_active_foods_fdc_ids()

    def __panel__(self):
        return self._layout
