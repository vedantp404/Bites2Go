from app.models.food import ParsedVoiceFoodItem


def test_scoop_mass_and_macros_are_not_invented():
    item = ParsedVoiceFoodItem(food_description="Whey protein", quantity=1, unit="scoop", estimated_grams=30, calories=120, protein=24, carbohydrates=3, fat=2)
    assert item.quantity == 1
    assert not item.portion_specified
    assert item.estimated_grams is None
    assert item.calories is None and item.protein is None and item.carbohydrates is None and item.fat is None


def test_unspecified_portion_overrides_unjustified_model_numbers():
    item = ParsedVoiceFoodItem(food_description="Some curry", portion_specified=False, estimated_grams=200, calories=300)
    assert item.estimated_grams is None and item.calories is None


def test_measured_grams_remain_available():
    item = ParsedVoiceFoodItem(food_description="Whey protein", quantity=30, unit="g", estimated_grams=30, calories=120)
    assert item.portion_specified and item.estimated_grams == 30
