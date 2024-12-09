import param
import panel as pn
from panel.viewable import Viewer
from pyfoodopt import FoodOptimizer, NutrientBank
import pandas as pd
from bokeh.models.widgets.tables import NumberFormatter


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


class Results(Viewer):

    food_optimizer = param.ClassSelector(class_=FoodOptimizer, doc="The FoodOptimizer")

    def __init__(self, **params):
        super().__init__(**params)
        self.optimal_foods = self.food_optimizer.get_optimal_foods()
        self.optimal_foods["fdc_id"] = self.optimal_foods["fdc_id"].astype(int)
        self.optimal_foods_tabulator = pn.widgets.Tabulator(self.optimal_foods)
        self.aggregate_result_info = AggregateResultInfo(
            cost=self.optimal_foods.cost.sum(), n_foods=self.optimal_foods.shape[0]
        )

        self.aggregate_result_nutrition_facts = AggregateResultNutritionFacts(
            food_optimizer=self.food_optimizer, optimal_foods=self.optimal_foods
        )
        # print(self.get_aggregate_nutrition_facts().sum())
        self._layout = pn.Column(
            self.optimal_foods_tabulator,
            self.aggregate_result_info,
            self.aggregate_result_nutrition_facts,
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
