from enum import Enum
import pandas as pd
import param
import pulp
import pint
from pulp import LpProblem, LpVariable, LpMinimize
import json

ureg = pint.UnitRegistry()
DATA_DIR = "../data"


class UNITS(Enum):
    g = ureg.gram
    kg = ureg.kilogram
    lb = ureg.pound
    oz = ureg.ounce
    mg = ureg.milligram


CONSTRAINT_TYPES = [
    "equality",
    "upper_bound",
    "lower_bound",
]

NUTRIENT_CONSTRAINT_CSV_COLUMNS = [
    "nutrient_nbrs",
    "constraint_name",
    "unit_name",
    "constraint_type",
    "constraint_value",
]

PANTRY_CSV_COLUMNS = [
    "price_per_100_g",
    "food_name",
    "fdc_id",
]


class BasePrice(param.Parameterized):

    price_per_100_g = param.Number(
        default=None, bounds=(0.0, None), doc="Price per 100 g of food as prepared"
    )
    price_dollars = param.Number(default=None, bounds=(0.0, None), doc="Price of food")
    weight = param.Number(default=None, bounds=(0.0, None), doc="Weight of food")
    # weight_units = param.ClassSelector(
    #     class_=UNITS, default=UNITS.g, doc="Units of weight"
    # )

    def __init__(
        self,
        price_dollars: float = None,
        weight: float = None,
        weight_units: UNITS = None,
        **params,
    ):
        super().__init__(**params)
        if params.get("price_per_100_g") is not None:
            return
        if price_dollars and weight and weight_units:
            weight_grams = (weight * weight_units.value).to(ureg.gram).magnitude
            self.price_per_100_g = price_dollars / (weight_grams / 100)


class FoodName(param.Parameterized):

    food_name = param.String(default=None, doc="Name of food")


class FoodRestrictions(param.Parameterized):

    vegetarian = param.Boolean(default=None, doc="Vegetarian")
    vegan = param.Boolean(default=None, doc="Vegan")
    gluten_free = param.Boolean(default=None, doc="Gluten-free")
    kosher = param.Boolean(default=None, doc="Kosher")
    halal = param.Boolean(default=None, doc="Halal")
    dairy_free = param.Boolean(default=None, doc="Dairy-free")
    wheat_free = param.Boolean(default=None, doc="Wheat")
    nut_free = param.Boolean(default=None, doc="Nuts")
    fish_shellfish_free = param.Boolean(default=None, doc="Fish/Shellfish")
    egg_free = param.Boolean(default=None, doc="Eggs")
    soy_free = param.Boolean(default=None, doc="Soy")

    def __init__(self, **params):
        super().__init__(**params)


def get_non_name_params(param_class):
    return [
        param_name
        for param_name in param_class.param.objects().keys()
        if param_name != "name"
    ]


def get_food_restrictions_from_dict(restrictions_dict):
    return FoodRestrictions(
        **{key: restrictions_dict[key] for key in get_non_name_params(FoodRestrictions)}
    )


class FoodMeta(param.Parameterized):

    description = param.String(default=None, doc="Description of food")
    nutrition_url = param.String(default=None, doc="URL of food")
    image_url = param.String(default=None, doc="Image of food")
    restrictions = param.ClassSelector(
        class_=FoodRestrictions, default=None, doc="Restrictions"
    )


class BaseFood(param.Parameterized):

    price = param.ClassSelector(class_=BasePrice, default=None, doc="Price of food")
    food_name = param.String(default=None, doc="Name of food")
    fdc_id = param.Integer(default=None, doc="FDC ID")
    food_nutrition = param.Dict(default={}, doc="Nutrition data")
    food_meta = param.ClassSelector(class_=FoodMeta, default=None, doc="Meta data")


class Pantry(param.Parameterized):

    foods = param.Dict(default={}, doc="Dict of foods keyed by fdc_id")

    def __init__(self, **params):
        super().__init__(**params)
        self.active_foods = set()

    def add_food(self, food: BaseFood, set_active=True):
        if not isinstance(food, BaseFood):
            raise TypeError("Invalid parameter type")
        self.foods[food.fdc_id] = food
        if set_active:
            self.active_foods.add(food.fdc_id)

    def build_pantry_from_csv(self, csv_path: str, set_active=False):
        df = pd.read_csv(csv_path, index_col=0)
        for index, row in df.iterrows():
            price = BasePrice(price_per_100_g=row["price_per_100_g"])
            food_name = row["food_name"]

            nutrition_values = row.loc[~row.index.isin(PANTRY_CSV_COLUMNS)]
            food_nutrition = {
                int(key): value for key, value in nutrition_values.items()
            }
            food = BaseFood(
                price=price,
                food_name=food_name,
                fdc_id=row["fdc_id"],
                food_nutrition=food_nutrition,
                food_meta=FoodMeta(restrictions=FoodRestrictions()),
            )
            self.add_food(food)
            if set_active:
                self.active_foods.add(food.fdc_id)

    def deactivate_food(self, fdc_id: int):
        self.active_foods.remove(fdc_id)

    def deactivate_foods(self, fdc_ids: list):
        for fdc_id in fdc_ids:
            self.active_foods.remove(fdc_id)

    def activate_foods(self, fdc_ids: list):
        for fdc_id in fdc_ids:
            self.active_foods.add(fdc_id)

    def set_active_foods(self, fdc_ids: list):
        self.active_foods = set(fdc_ids)

    def activate_food(self, fdc_id: int):
        self.active_foods.add(fdc_id)

    def get_all_fdc_ids(self):
        return list(self.foods.keys())

    def get_food_by_fdc_id(self, fdc_id: int):
        if fdc_id not in self.foods:
            raise ValueError(f"FDC ID {fdc_id} not found in pantry")
        return self.foods[fdc_id]

    def get_active_foods(self):
        return {fdc_id: self.foods[fdc_id] for fdc_id in self.active_foods}

    def build_pantry_from_json(self, json_path: str):
        with open(json_path, "r") as f:
            data = json.load(f)
        for fdc_id in data:
            food = BaseFood(
                price=BasePrice(price_per_100_g=data[fdc_id]["price_per_100_g"]),
                food_name=data[fdc_id]["food_name"],
                fdc_id=int(fdc_id),
                food_nutrition={int(k): v for k, v in data[fdc_id]["food_nutrition"].items()},
                food_meta=FoodMeta(
                    restrictions=get_food_restrictions_from_dict(
                        data[fdc_id]["restrictions"]
                    )
                ),
            )
            self.add_food(food)


class FoodStore(param.Parameterized):

    food_store = param.ClassSelector(class_=Pantry, default=None, doc="Pantry")
    fdc_ids = param.List(default=[], item_type=int, doc="List of FDC IDs")

    def __init__(self, **params):
        super().__init__(**params)

    def add_pantry(self, pantry: Pantry):
        self.food_store = pantry

    def add_all_foods_from_pantry(self):
        self.fdc_ids = self.food_store.get_all_fdc_ids()

    def remove_food(self, fdc_id: int):
        self.fdc_ids.remove(fdc_id)

    def add_food(self, fdc_id: int):
        self.fdc_ids.append(fdc_id)

    def get_all_foods(self):
        return [self.food_store.get_food_by_fdc_id(fdc_id) for fdc_id in self.fdc_ids]


class BaseConstraint(param.Parameterized):

    constraint_name = param.String(default=None, doc="Name of constraint")
    constraint_type = param.Selector(
        default=None, objects=CONSTRAINT_TYPES, doc="Type of constraint"
    )
    constraint_value = param.Number(default=None, doc="Value of constraint")


class NutrientConstraint(BaseConstraint):

    nbr_to_coefficient = param.Dict(default={}, doc="Dict of nutrient to coefficient")

    def get_id(self):
        return tuple(sorted(self.nbr_to_coefficient.keys()))


class FoodConstraint(BaseConstraint):

    fdc_id_to_coefficient = param.Dict(default={}, doc="Dict of FDC ID to coefficient")


class BaseNutrient(param.Parameterized):

    RDA_CATEGORIES = ["default"]

    nutrient_name = param.String(default=None, doc="Name of nutrient")
    nutrient_id = param.Integer(default=None, doc="ID of nutrient")
    unit_name = param.String(default=None, doc="Unit of nutrient")


class NutrientBank(param.Parameterized):

    nutrients = param.Dict(default={}, doc="Dict of nutrients")

    def __init__(self, **params):
        super().__init__(**params)

    def add_nutrient(self, nutrient: BaseNutrient):
        self.nutrients[nutrient.nutrient_id] = nutrient

    def remove_nutrient(self, nutrient_id):
        del self.nutrients[nutrient_id]

    def get_default_constraints(self):
        constraints = Constraints()
        for nutrient in self.nutrients.values():
            constraints.add_constraints(nutrient.nutrient_rdas["default"])
        return constraints

    def get_nutrient_by_id(self, nutrient_id, default=None):
        return self.nutrients.get(nutrient_id, default)

    def build_nutrient_bank_from_json(self, json_path: str):
        with open(json_path, "r") as f:
            data = json.load(f)
        for nutrient_id in data:
            nutrient = BaseNutrient(
                nutrient_name=data[nutrient_id]["nutrient_name"],
                nutrient_id=int(nutrient_id),
                unit_name=data[nutrient_id]["unit_name"],
            )
            self.add_nutrient(nutrient)

    def build_nutrient_bank_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path, index_col=0)
        for index, row in df.iterrows():
            nutrient = BaseNutrient(
                nutrient_name=row["nutrient_name"],
                nutrient_id=row["nutrient_nbr"],
                unit_name=row["unit_name"],
            )
            self.add_nutrient(nutrient)


class Constraints(param.Parameterized):

    constraints = param.Dict(default={}, doc="Dict of constraints")
    nutrient_constraints = param.Dict(default={}, doc="Dict of nutrient constraints")

    def __init__(self, **params):
        super().__init__(**params)
        self.nconstraints_added = 0

    def add_constraint(self, constraint: BaseConstraint):
        self.constraints[self.nconstraints_added] = constraint
        self.nconstraints_added += 1

    def add_constraints(self, constraints):
        if isinstance(constraints, list):
            for constraint in constraints:
                self.add_constraint(constraint)
        elif isinstance(constraints, BaseConstraint):
            self.add_constraint(constraints)

    def add_nutrient_constraint(self, nutrient_constraint: NutrientConstraint):
        nutrient_constraint_id = nutrient_constraint.get_id()
        if nutrient_constraint_id not in self.nutrient_constraints:
            self.nutrient_constraints[nutrient_constraint_id] = {}
        self.nutrient_constraints[nutrient_constraint_id][
            nutrient_constraint.constraint_type
        ] = nutrient_constraint
        self.nconstraints_added += 1

    def add_nutrient_constraints_from_json(self, json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
        for constraint_id, info in data.items():
            nutrient_nbrs = [int(nbr) for nbr in constraint_id.split(";")]
            nbr_to_coefficient = {nbr: 1 for nbr in nutrient_nbrs}
            for constraint_type, constraint_value in info["constraints"].items():
                if constraint_type not in CONSTRAINT_TYPES:
                    continue
                constraint = NutrientConstraint(
                    constraint_type=constraint_type,
                    constraint_value=constraint_value,
                    nbr_to_coefficient=nbr_to_coefficient,
                )
                self.add_nutrient_constraint(constraint)

    """
    Adds nutrient constraints from a CSV file. Assumes all coefficients are one.
    """

    def add_nutrient_constraints_from_csv(self, csv_path):
        df = pd.read_csv(csv_path)
        for index, row in df.iterrows():
            nutrient_nbrs = sorted(
                [int(nbr) for nbr in row["nutrient_nbrs"].split(";")]
            )
            constraint_name = row.get("constraint_name")
            if pd.isna(constraint_name):
                constraint_name = (
                    row["nutrient_nbrs"]
                    + " "
                    + row["constraint_type"]
                    + " "
                    + row.get("constraint_value")
                )
            constraint = NutrientConstraint(
                constraint_name=constraint_name,
                constraint_type=row["constraint_type"],
                constraint_value=row["constraint_value"],
                nbr_to_coefficient={nbr: 1 for nbr in nutrient_nbrs},
            )
            self.add_constraint(constraint)

    def remove_constraint(self, constraint_id):
        del self.constraints[constraint_id]


class BaseObjective(param.Parameterized):

    objective_name = param.String(default=None, doc="Name of objective")
    objective_type = param.Selector(
        default=None, objects=["maximize", "minimize"], doc="Objective type"
    )


class FoodOptimizer(param.Parameterized):

    pantry = param.ClassSelector(class_=Pantry, doc="Pantry")
    constraints = param.ClassSelector(class_=Constraints, doc="Constraints")
    # objective = param.ClassSelector(class_=BaseObjective, doc="Objective")

    def __init__(self, starting_foods: dict = {}, **params):
        super().__init__(**params)
        self.results = []
        self.starting_foods = starting_foods

    def optimize(self):
        # Define the problem

        prob = LpProblem("Minimize_Cost", LpMinimize)
        decision_variables = {}
        slack_vars = []

        # Define decision variables for each food item
        for fdc_id, food in self.pantry.get_active_foods().items():
            lowBound = self.starting_foods.get(fdc_id, 0)
            decision_variables[fdc_id] = LpVariable(
                f"{fdc_id} {food.food_name}", lowBound=lowBound
            )

        active_fdc_ids = list(self.pantry.get_active_foods().keys())
        # Add constraints based on nutrient requirements
        for nutrient_nbrs, constraints in self.constraints.nutrient_constraints.items():
            # print(nutrient_nbrs)
            # print(self.pantry.get_active_foods().keys())
            coefficient_list = []

            for constraint_type, constraint_value in constraints.items():

                for nbr in nutrient_nbrs:

                    for fdc_id in active_fdc_ids:

                        if nbr not in self.pantry.foods[fdc_id].food_nutrition:
                            # print(f"Nutrient {nbr} not found in food {self.pantry.foods[fdc_id].food_name}", type(nbr))
                            continue

                        coefficient_list.append(
                            decision_variables[fdc_id]
                            * self.pantry.foods[fdc_id].food_nutrition.get(nbr, 0)
                            / self.pantry.foods[fdc_id].price.price_per_100_g
                        )
                    # coefficient_list += [
                    #     decision_variables[fdc_id]
                    #     * self.pantry.foods[fdc_id].food_nutrition.get(nbr, 0)
                    #     / self.pantry.foods[fdc_id].price.price_per_100_g
                    #     for fdc_id in active_fdc_ids
                    # ]

                
                slack_var_up = pulp.LpVariable(f"{nutrient_nbrs} {constraint_type} up", lowBound=0)
                slack_var_down = pulp.LpVariable(f"{nutrient_nbrs} {constraint_type} down", lowBound=0)
                slack_vars.append(slack_var_up)
                slack_vars.append(slack_var_down)

                pulp_sum = pulp.lpSum(coefficient_list) + slack_var_up - slack_var_down


                if constraint_type == "equality":
                    prob += pulp_sum == constraint_value
                elif constraint_type == "upper_bound":
                    prob += pulp_sum <= constraint_value
                elif constraint_type == "lower_bound":
                    prob += pulp_sum >= constraint_value

        # Objective function: minimize the sum of decision variables (or add specific costs if needed)
        prob += sum(list(decision_variables.values()))
        prob += sum([sv * 10000 for sv in slack_vars])


        status = prob.solve()
        self.results.append(prob)
        return status

    def get_optimal_foods(self, prob=None):
        if prob is None:
            prob = self.results[-1]

        optimal_amounts = []
        for v in prob.variables():
            if v.varValue != 0:
                optimal_amounts.append([v.name, v.varValue])
        df = pd.DataFrame(optimal_amounts, columns=["food", "cost"])
        df[["fdc_id", "food_name"]] = df.food.str.split("_", n=1, expand=True)
        df = df.drop(columns="food")
        df["price_per_100_g"] = df.fdc_id.apply(
            lambda x: self.pantry.foods[int(x)].price.price_per_100_g
        )
        df["amount"] = df.cost / df.price_per_100_g * 100
        return df
    
    def get_shadow_prices(self, prob=None):
        if prob is None:
            prob = self.results[-1]

        pis = []

        for name, constraint in prob.constraints.items():
            pis.append([name, constraint.pi])

        constraint_shadow_prices = pd.DataFrame(pis, columns=['constraint_name', 'pi'])
        return constraint_shadow_prices
    
    def get_optimal_values(self, prob=None):
        if prob is None:
            prob = self.results[-1]

        optimal_amounts = []
        for v in prob.variables():
            optimal_amounts.append([v.name, v.varValue])

        ov = pd.DataFrame(optimal_amounts, columns=['variable_name', 'variable_value'])
        return ov