import param
import panel as pn
from panel.viewable import Viewer
from pyfoodopt import FoodOptimizer, NutrientBank
import pandas as pd
from bokeh.models.widgets.tables import NumberFormatter
from config import *

SHADOW_PRICES_DISPLAY_COLUMNS = ["nutrient_names", "constraint_type", "pi"]


class AggregateResultInfo(Viewer):

    cost = param.Number()
    n_foods = param.Integer()

    def __init__(self, **params):
        super().__init__(**params)
        self._layout = pn.Row(
            pn.FlexBox(
                self.get_cost_indicator(),
                self.get_n_foods_indicator(),
                flex_direction="row",
                justify_content="space-evenly",
            )
        )

    def get_cost_indicator(self):
        return pn.indicators.Number(
            name="Total Cost",
            value=self.cost,
            format="${value:,.2f}",
            default_color="green",
        )

    def get_n_foods_indicator(self):
        return pn.indicators.Number(name="# of Foods", value=self.n_foods)

    def __panel__(self):
        return self._layout


class AggregateResultNutritionFacts(Viewer):

    food_optimizer = param.ClassSelector(class_=FoodOptimizer)
    optimal_foods = param.DataFrame(default=None)
    nutrient_bank = param.ClassSelector(class_=NutrientBank)

    tabulator_formatters = {
        "Amount": NumberFormatter(format="0.00"),
    }

    def __init__(self, **params):
        super().__init__(**params)
        if self.optimal_foods is None:
            self.optimal_foods = self.food_optimizer.get_optimal_foods()
        self.tabulator = self.get_aggregate_nutrition_facts_tabulator()
        self._layout = pn.Column(self.tabulator)

    def get_aggregate_nutrition_facts_tabulator(self):
        df = self.get_aggregate_nutrition_facts_df()
        tabulator = pn.widgets.Tabulator(
            df,
            show_index=False,
            formatters=AggregateResultNutritionFacts.tabulator_formatters,
            stylesheets=[TABULATOR_STYLESHEET],
        )
        return tabulator

    def get_aggregate_nutrition_facts_df(self):
        nutrition_dict = {}
        for i, row in self.optimal_foods.iterrows():
            food = self.food_optimizer.pantry.get_food_by_fdc_id(row["fdc_id"])
            nutrition_dict[str(row["fdc_id"])] = {
                nutrient_nbr: amount * row["amount"] / 100
                for nutrient_nbr, amount in food.food_nutrition.items()
            }
        nutrition_df = pd.DataFrame(nutrition_dict)
        nutrient_units = [
            self.nutrient_bank.get_nutrient_by_id(nbr).unit_name
            for nbr in nutrition_df.index
        ]
        nutrient_names = [
            self.nutrient_bank.get_nutrient_by_id(nbr).nutrient_name
            for nbr in nutrition_df.index
        ]
        # nutrition_df.columns = pd.MultiIndex.from_tuples(
        #     list(zip(nutrition_df.columns.astype(str), nutrient_names)),
        #     names=["nutrient_nbr", "nutrient_name"]
        # )
        nutrition_df.index = nutrient_names
        nutrition_df = (
            nutrition_df.T.sum()
            .reset_index()
            .rename(columns={"index": "Nutrient", 0: "Amount"})
        )
        nutrition_df["Units"] = nutrient_units
        return nutrition_df

    def __panel__(self):
        return self._layout


class ShadowPrices(Viewer):
    food_optimizer = param.ClassSelector(class_=FoodOptimizer)
    nutrient_bank = param.ClassSelector(class_=NutrientBank)

    def translate_nutrient_nbrs(self, nutrient_nbrs: str):
        nutrient_nbrs = nutrient_nbrs.split("_")
        nutrient_names = []
        for nbr in nutrient_nbrs:
            nutrient = self.nutrient_bank.get_nutrient_by_id(int(nbr))
            if nutrient is not None:
                nutrient_names.append(nutrient.nutrient_name)
        return " + ".join(nutrient_names)

    def __init__(self, **params):
        super().__init__(**params)
        self.shadow_prices = self.food_optimizer.get_shadow_prices()
        self.shadow_prices[["nutrient_nbrs", "constraint_type"]] = (
            self.shadow_prices.constraint_name.str.split(":", expand=True)
        )
        self.shadow_prices["nutrient_names"] = self.shadow_prices[
            "nutrient_nbrs"
        ].apply(self.translate_nutrient_nbrs)

    def _layout(self, show_all=False):
        return pn.widgets.Tabulator(
            self.shadow_prices.loc[(self.shadow_prices.pi != 0) | show_all][
                SHADOW_PRICES_DISPLAY_COLUMNS
            ]
        )

    def __panel__(self):
        return self._layout


class Results(Viewer):

    food_optimizer = param.ClassSelector(class_=FoodOptimizer, doc="The FoodOptimizer")
    nutrient_bank = param.ClassSelector(class_=NutrientBank)

    def __init__(self, **params):
        super().__init__(**params)
        self.optimal_foods = self.food_optimizer.get_optimal_foods()
        self.optimal_foods["food_name"] = self.optimal_foods["food_name"].str.replace(
            "_", " "
        )
        self.optimal_foods["fdc_id"] = self.optimal_foods["fdc_id"].astype(int)
        self.optimal_foods_tabulator = pn.widgets.Tabulator(
            self.optimal_foods[FOOD_TABLE_COLUMNS],
            titles=FOOD_TABLE_MAPPINGS,
            show_index=False,
            layout="fit_data_table",
            stylesheets=[TABULATOR_STYLESHEET],
        )
        self.aggregate_result_info = AggregateResultInfo(
            cost=self.optimal_foods.cost.sum(), n_foods=self.optimal_foods.shape[0]
        )

        self.aggregate_result_nutrition_facts = AggregateResultNutritionFacts(
            food_optimizer=self.food_optimizer,
            optimal_foods=self.optimal_foods,
            nutrient_bank=self.nutrient_bank,
        )

        self.shadow_prices = ShadowPrices(
            food_optimizer=self.food_optimizer, nutrient_bank=self.nutrient_bank
        )
        # print(self.get_aggregate_nutrition_facts().sum())

    def _layout(self):
        return pn.Column(
            self.aggregate_result_info,
            pn.pane.Markdown("## Foods"),
            pn.Accordion(("Food Info", self.optimal_foods_tabulator)),
            pn.pane.Markdown("## Nutrition Facts"),
            pn.Accordion(("Nutrition Facts", self.aggregate_result_nutrition_facts)),
            pn.pane.Markdown("## Shadow Prices"),
            pn.Accordion(("Shadow Prices", self.shadow_prices)),
        )

    def get_aggregate_results_info(self):
        total_cost = self.optimal_foods.cost.sum()
        n_foods = self.optimal_foods.shape[0]
        nutrition_facts = self.get_aggregate_nutrition_facts(self.optimal_foods)

    def __panel__(self):
        return self._layout


class ResultsTabs(Viewer):

    # results = param.List(item_type=Results, doc="List of Results")

    def __init__(self, **params):
        super().__init__(**params)
        self.results_tabs = pn.Tabs(closable=True)
        self._num_results = 0

    def add_result(self, result: Results):
        self._num_results += 1
        self.results_tabs.append((f"Result {self._num_results}", result))

    def __panel__(self):
        return self.results_tabs


class ResultsContainer(Viewer):

    results_tabs = param.ClassSelector(class_=ResultsTabs, default=ResultsTabs())

    def __init__(self, **params):
        super().__init__(**params)

    def _layout(self):
        container_header = pn.pane.Markdown("# Results", sizing_mode="stretch_width")
        return pn.Column(
            container_header,
            self.results_tabs,
            width=CONFIG_RESULTS_WIDTH,
            margin=(25, 0),
            styles={
                "border": "1px solid black",
                "border-radius": "25px",
                "padding": "25px",
            },
        )

    def add_result(self, results: Results):
        self.results_tabs.add_result(results)

    def __panel__(self):
        return self._layout
