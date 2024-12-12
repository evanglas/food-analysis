from pyfoodopt import FoodRestrictions

CONFIG_RESULTS_WIDTH = 700

FOOD_RESTRICTIONS = [r for r in FoodRestrictions.param.objects() if r != "name"]


FOOD_RESTRICTION_NAME_MAPPINGS = {
    "vegan": "Vegan",
    "vegetarian": "Vegetarian",
    # "pescatarian": "Pescatarian",
    # "keto": "Keto",
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
