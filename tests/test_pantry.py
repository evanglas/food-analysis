import pytest
import pandas as pd
from io import StringIO
from src.pyfoodopt import Pantry
from src.pyfoodopt import (
    BaseFood,
    BasePrice,
    FoodName,
)  # Assuming these are implemented


# Define mock objects for testing
class MockBaseFood(BaseFood):
    def __init__(self, price, food_name, fdc_id):
        self.price = price
        self.food_name = food_name
        self.fdc_id = fdc_id


@pytest.fixture
def mock_food():
    price = BasePrice(price_per_100_g=10.0)
    food_name = FoodName(food_name="Apple")
    return MockBaseFood(price=price, food_name=food_name, fdc_id=12345)


@pytest.fixture
def mock_csv_data():
    data = """price_per_100_g,food_name,fdc_id
10.0,Apple,12345
20.0,Banana,67890"""
    return StringIO(data)


def test_pantry_initialization():
    pantry = Pantry()
    assert pantry.foods == []


def test_add_valid_food(mock_food):
    pantry = Pantry()
    pantry.add_food(mock_food)
    assert len(pantry.foods) == 1
    assert pantry.foods[0] == mock_food


def test_add_invalid_food():
    pantry = Pantry()
    with pytest.raises(TypeError):
        pantry.add_food("Not a BaseFood")


def test_food_assignment_with_invalid_type():
    pantry = Pantry()
    with pytest.raises(TypeError):
        pantry.foods = ["Not a BaseFood"]


def test_build_pantry_from_csv(mock_csv_data):
    pantry = Pantry()

    # Mock the CSV reading process
    pantry.build_pantry_from_csv(mock_csv_data)

    assert len(pantry.foods) == 2
    assert pantry.foods[0].food_name.food_name == "Apple"
    assert pantry.foods[1].food_name.food_name == "Banana"
    assert pantry.foods[0].price.price_per_100_g == 10.0
    assert pantry.foods[1].price.price_per_100_g == 20.0
