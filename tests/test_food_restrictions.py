import pytest
import pandas as pd
import param
from src.pyfoodopt import FoodRestrictions  # Replace with your module's name


def test_get_restrictions_from_series():
    # Initialize FoodRestrictions instance with default values
    fr = FoodRestrictions()

    # Create a pandas Series that mimics input data for restrictions
    series_data = pd.Series(
        {
            "vegetarian": True,
            "vegan": False,
            "gluten_free": True,
            "kosher": None,
            "halal": False,
            "dairy_free": True,
            "wheat": False,
            "nuts": True,
            "fish_shellfish": None,
            "eggs": False,
            "soy": True,
        }
    )

    # Call the method with the series data
    fr.get_restrictions_from_series(series_data)

    # Assert each attribute's value to check correctness
    assert fr.vegetarian is True
    assert fr.vegan is False
    assert fr.gluten_free is True
    assert fr.kosher is None
    assert fr.halal is False
    assert fr.dairy_free is True
    assert fr.wheat is False
    assert fr.nuts is True
    assert fr.fish_shellfish is None
    assert fr.eggs is False
    assert fr.soy is True


def test_empty_series():
    # Test the case where an empty series is passed
    fr = FoodRestrictions()
    series_data = pd.Series({})  # Empty Series
    fr.get_restrictions_from_series(series_data)

    # Ensure all parameters remain at default None
    assert fr.vegetarian is None
    assert fr.vegan is None
    assert fr.gluten_free is None
    assert fr.kosher is None
    assert fr.halal is None
    assert fr.dairy_free is None
    assert fr.wheat is None
    assert fr.nuts is None
    assert fr.fish_shellfish is None
    assert fr.eggs is None
    assert fr.soy is None


def test_partial_series():
    # Test the case where only some restrictions are set in the series
    fr = FoodRestrictions()
    series_data = pd.Series(
        {
            "vegetarian": True,
            "nuts": False,
        }
    )
    fr.get_restrictions_from_series(series_data)

    # Ensure only the provided parameters are updated, others remain None
    assert fr.vegetarian is True
    assert fr.vegan is None
    assert fr.gluten_free is None
    assert fr.kosher is None
    assert fr.halal is None
    assert fr.dairy_free is None
    assert fr.wheat is None
    assert fr.nuts is False
    assert fr.fish_shellfish is None
    assert fr.eggs is None
    assert fr.soy is None
