import panel as pn
from panel.viewable import Viewer
import pandas as pd
import param

from param import rx

pn.extension("tabulator")


class NutritionFacts(param.Parameterized):

    calories: int = param.Integer()
    protein: int = param.Integer()
    fat: int = param.Integer()
    carbs: int = param.Integer()
    fiber: int = param.Integer()
    sugar: int = param.Integer()
    sodium: int = param.Integer()
    cholesterol: int = param.Integer()
    saturated_fat: int = param.Integer()


class FoodName(param.Parameterized):

    food_name: str = param.String(nested_refs=True)


class FoodPrice(param.Parameterized):

    price: float = param.Number()


class Food(param.Parameterized):

    # food_name: FoodName = param.ClassSelector(
    #     class_=FoodName, allow_refs=True, nested_refs=True
    # )
    food_name: str = param.String()
    nutrition_facts: NutritionFacts = param.ClassSelector(
        class_=NutritionFacts, allow_refs=True, nested_refs=True
    )
    price: FoodPrice = param.ClassSelector(
        class_=FoodPrice, allow_refs=True, nested_refs=True
    )


beef = Food(
    food_name="beef",
    nutrition_facts=NutritionFacts(),
    price=FoodPrice(price=3),
)


class FoodEditBox(Viewer):

    food = param.ClassSelector(class_=Food, allow_refs=True, nested_refs=True)

    selected = param.Boolean(default=True)
    diet_proportion_limit = param.Number(default=1, bounds=(0, 1))

    def __init__(self, **params):
        super().__init__(**params)

    # @param.depends("food.food_name.food_name")
    # def update_food_name(self):
    #     return pn.pane.Markdown(f"Food Name: {self.food.food_name.food_name}")

    def __panel__(self):
        return pn.FlexBox(
            pn.widgets.Checkbox.from_param(
                self.param.selected,
                name="",
                styles={
                    "margin-left": "20px",
                    "margin-right": "20px",
                    "margin-top": "0px",
                    "margin-bottom": "0px",
                },
            ),
            pn.pane.Str(
                f"{self.param.food.rx.value.param.food_name.rx().capitalize().rx.value}",
                styles={
                    "font-size": "20px",
                    "font-weight": "bold",
                    "font-family": "Helvetica",
                    "margin-left": "20px",
                    "margin-right": "20px",
                    "margin-top": "0px",
                    "margin-bottom": "3px",
                },
            ),
            pn.widgets.FloatInput.from_param(
                self.param.diet_proportion_limit,
                width=100,
                name="",
                styles={"height": "30px"},
            ),
            flex_direction="row",
            align_items="center",
            align_content="center",
            sizing_mode="fixed",
            width=300,
            height=40,
            styles={
                "background-color": "pink",
                "color": "black",
                "border-radius": "10px",
            },
        )
        # return pn.Column(
        #     pn.Row(
        #         self.param.food.rx().param.food_name,
        #         self.param.food.rx.value.param.food_name.rx(),
        #         self.param.a.rx(),
        #     ),
        #     pn.Row(
        #         # Accessor
        #         self.param.food.rx.value.param.price.rx().param.price,
        #         # Reactive display
        #         self.param.food.rx.value.param.price.rx.value.param.price.rx(),
        #     ),
        # )
        # return pn.Row(self.param.food.rx().param.food_name, self.param.food.rx()._depth)
        # return pn.Row(self.param.a, self.param.a.rx())


food_df = pd.DataFrame(
    {
        "food_name": ["beef", "chicken", "pork", "lamb", "fish"],
        "calories": [250, 200, 300, 400, 150],
        "protein": [20, 15, 25, 30, 10],
        "fat": [15, 10, 20, 25, 5],
    }
)

tabulator = pn.widgets.Tabulator(food_df, pagination="remote", page_size=5)

beef_box = FoodEditBox(food=beef)

# pn.Feed(*[beef_box] * 10).servable()

# beef_box.servable()


tabulator.servable()
