# seed_sample_data.py
# Inserts sample foods so we can test search_foods.
#
# How to run (from the backend folder):
#   python seed_sample_data.py

from app.database.session import SessionLocal
from app.models.allergen import Allergen
from app.models.dietary_type import DietaryType
from app.models.food import Food
from app.models.ingredient import Ingredient
from app.models.nutrition import FoodNutrition
from app.models.tag import Tag


def get_or_create(db, model, defaults=None, **lookup):
    """Find one row. If it does not exist, create it."""
    row = db.query(model).filter_by(**lookup).first()
    if row:
        return row

    data = dict(lookup)
    if defaults:
        data.update(defaults)
    row = model(**data)
    db.add(row)
    db.flush()
    return row


def add_food_if_missing(
    db,
    *,
    name,
    description,
    food_category,
    preparation_time_minutes,
    serving_size,
    serving_unit,
    nutrition,
    tags,
    dietary_types,
    allergens,
    ingredients,
):
    """Create one food only if that name is not already in the database."""
    existing = db.query(Food).filter_by(name=name).first()
    if existing:
        return existing

    food = Food(
        name=name,
        description=description,
        food_category=food_category,
        preparation_time_minutes=preparation_time_minutes,
        serving_size=serving_size,
        serving_unit=serving_unit,
    )
    food.nutrition = FoodNutrition(**nutrition)
    food.tags = tags
    food.dietary_types = dietary_types
    food.allergens = allergens
    food.ingredients = ingredients
    db.add(food)
    return food


def seed():
    db = SessionLocal()

    try:
        # ---------- tags ----------
        spicy = get_or_create(db, Tag, name="spicy", defaults={"category": "taste"})
        sweet = get_or_create(db, Tag, name="sweet", defaults={"category": "taste"})
        high_protein = get_or_create(db, Tag, name="high_protein", defaults={"category": "nutrition"})
        low_calorie = get_or_create(db, Tag, name="low_calorie", defaults={"category": "nutrition"})
        quick_meal = get_or_create(db, Tag, name="quick_meal", defaults={"category": "context"})
        comfort_food = get_or_create(db, Tag, name="comfort_food", defaults={"category": "mood"})

        # ---------- dietary types ----------
        vegetarian = get_or_create(db, DietaryType, name="vegetarian")
        vegan = get_or_create(db, DietaryType, name="vegan")
        non_vegetarian = get_or_create(db, DietaryType, name="non_vegetarian")
        gluten_free = get_or_create(db, DietaryType, name="gluten_free")
        dairy_free = get_or_create(db, DietaryType, name="dairy_free")

        # ---------- allergens ----------
        peanuts = get_or_create(db, Allergen, name="peanuts")
        milk = get_or_create(db, Allergen, name="milk")
        gluten = get_or_create(db, Allergen, name="gluten")
        eggs = get_or_create(db, Allergen, name="eggs")
        shellfish = get_or_create(db, Allergen, name="shellfish")

        # ---------- ingredients ----------
        chicken = get_or_create(db, Ingredient, name="chicken")
        rice = get_or_create(db, Ingredient, name="rice")
        vegetables = get_or_create(db, Ingredient, name="vegetables")
        paneer = get_or_create(db, Ingredient, name="paneer")
        lentils = get_or_create(db, Ingredient, name="lentils")
        oats = get_or_create(db, Ingredient, name="oats")
        banana = get_or_create(db, Ingredient, name="banana")
        yoghurt = get_or_create(db, Ingredient, name="yoghurt")
        salmon = get_or_create(db, Ingredient, name="salmon")
        quinoa = get_or_create(db, Ingredient, name="quinoa")
        tofu = get_or_create(db, Ingredient, name="tofu")
        chickpeas = get_or_create(db, Ingredient, name="chickpeas")
        eggs_ing = get_or_create(db, Ingredient, name="eggs")
        bread = get_or_create(db, Ingredient, name="bread")
        peanut_butter = get_or_create(db, Ingredient, name="peanut_butter")
        prawns = get_or_create(db, Ingredient, name="prawns")
        noodles = get_or_create(db, Ingredient, name="noodles")
        avocado = get_or_create(db, Ingredient, name="avocado")
        berries = get_or_create(db, Ingredient, name="berries")
        potato = get_or_create(db, Ingredient, name="potato")

        foods = [
            {
                "name": "Grilled Chicken Bowl",
                "description": "Grilled chicken with rice and vegetables",
                "food_category": "main_course",
                "preparation_time_minutes": 20,
                "serving_size": "1",
                "serving_unit": "bowl",
                "nutrition": {
                    "calories": 450,
                    "protein_g": 40,
                    "carbohydrates_g": 45,
                    "fat_g": 12,
                    "fibre_g": 8,
                    "sugar_g": 5,
                    "sodium_mg": 600,
                },
                "tags": [spicy, high_protein, quick_meal],
                "dietary_types": [non_vegetarian, gluten_free],
                "allergens": [],
                "ingredients": [chicken, rice, vegetables],
            },
            {
                "name": "Spicy Paneer Wrap",
                "description": "Soft wrap filled with spicy paneer and veggies",
                "food_category": "main_course",
                "preparation_time_minutes": 15,
                "serving_size": "1",
                "serving_unit": "wrap",
                "nutrition": {
                    "calories": 520,
                    "protein_g": 22,
                    "carbohydrates_g": 55,
                    "fat_g": 24,
                    "fibre_g": 6,
                    "sugar_g": 8,
                    "sodium_mg": 700,
                },
                "tags": [spicy, comfort_food],
                "dietary_types": [vegetarian],
                "allergens": [milk, gluten],
                "ingredients": [paneer, vegetables, bread],
            },
            {
                "name": "Lentil Salad",
                "description": "Fresh salad with lentils and vegetables",
                "food_category": "salad",
                "preparation_time_minutes": 10,
                "serving_size": "1",
                "serving_unit": "bowl",
                "nutrition": {
                    "calories": 320,
                    "protein_g": 18,
                    "carbohydrates_g": 40,
                    "fat_g": 8,
                    "fibre_g": 12,
                    "sugar_g": 4,
                    "sodium_mg": 350,
                },
                "tags": [low_calorie, high_protein, quick_meal],
                "dietary_types": [vegan, gluten_free, dairy_free],
                "allergens": [],
                "ingredients": [lentils, vegetables],
            },
            {
                "name": "Banana Oat Smoothie",
                "description": "Creamy smoothie with oats, banana and yoghurt",
                "food_category": "beverage",
                "preparation_time_minutes": 5,
                "serving_size": "1",
                "serving_unit": "glass",
                "nutrition": {
                    "calories": 280,
                    "protein_g": 12,
                    "carbohydrates_g": 48,
                    "fat_g": 6,
                    "fibre_g": 5,
                    "sugar_g": 22,
                    "sodium_mg": 90,
                },
                "tags": [sweet, quick_meal, comfort_food],
                "dietary_types": [vegetarian],
                "allergens": [milk, gluten],
                "ingredients": [oats, banana, yoghurt],
            },
            {
                "name": "Salmon Quinoa Plate",
                "description": "Baked salmon served with quinoa and greens",
                "food_category": "main_course",
                "preparation_time_minutes": 25,
                "serving_size": "1",
                "serving_unit": "plate",
                "nutrition": {
                    "calories": 480,
                    "protein_g": 38,
                    "carbohydrates_g": 35,
                    "fat_g": 18,
                    "fibre_g": 7,
                    "sugar_g": 3,
                    "sodium_mg": 520,
                },
                "tags": [high_protein],
                "dietary_types": [non_vegetarian, gluten_free, dairy_free],
                "allergens": [],
                "ingredients": [salmon, quinoa, vegetables],
            },
            {
                "name": "Tofu Stir Fry",
                "description": "Crispy tofu with mixed vegetables in light sauce",
                "food_category": "main_course",
                "preparation_time_minutes": 18,
                "serving_size": "1",
                "serving_unit": "bowl",
                "nutrition": {
                    "calories": 360,
                    "protein_g": 24,
                    "carbohydrates_g": 28,
                    "fat_g": 14,
                    "fibre_g": 9,
                    "sugar_g": 6,
                    "sodium_mg": 580,
                },
                "tags": [high_protein, quick_meal, low_calorie],
                "dietary_types": [vegan, gluten_free, dairy_free],
                "allergens": [],
                "ingredients": [tofu, vegetables, rice],
            },
            {
                "name": "Chickpea Buddha Bowl",
                "description": "Roasted chickpeas, avocado and vegetables over rice",
                "food_category": "main_course",
                "preparation_time_minutes": 22,
                "serving_size": "1",
                "serving_unit": "bowl",
                "nutrition": {
                    "calories": 420,
                    "protein_g": 16,
                    "carbohydrates_g": 52,
                    "fat_g": 16,
                    "fibre_g": 14,
                    "sugar_g": 5,
                    "sodium_mg": 410,
                },
                "tags": [comfort_food, low_calorie],
                "dietary_types": [vegan, gluten_free, dairy_free],
                "allergens": [],
                "ingredients": [chickpeas, avocado, rice, vegetables],
            },
            {
                "name": "Veggie Omelette",
                "description": "Egg omelette loaded with fresh vegetables",
                "food_category": "breakfast",
                "preparation_time_minutes": 12,
                "serving_size": "1",
                "serving_unit": "plate",
                "nutrition": {
                    "calories": 310,
                    "protein_g": 22,
                    "carbohydrates_g": 8,
                    "fat_g": 20,
                    "fibre_g": 3,
                    "sugar_g": 3,
                    "sodium_mg": 480,
                },
                "tags": [high_protein, quick_meal, low_calorie],
                "dietary_types": [vegetarian, gluten_free],
                "allergens": [eggs, milk],
                "ingredients": [eggs_ing, vegetables],
            },
            {
                "name": "Peanut Butter Toast",
                "description": "Toasted bread topped with peanut butter and banana",
                "food_category": "snack",
                "preparation_time_minutes": 5,
                "serving_size": "2",
                "serving_unit": "slices",
                "nutrition": {
                    "calories": 390,
                    "protein_g": 14,
                    "carbohydrates_g": 42,
                    "fat_g": 18,
                    "fibre_g": 6,
                    "sugar_g": 12,
                    "sodium_mg": 320,
                },
                "tags": [sweet, quick_meal, comfort_food],
                "dietary_types": [vegetarian, dairy_free],
                "allergens": [peanuts, gluten],
                "ingredients": [bread, peanut_butter, banana],
            },
            {
                "name": "Prawn Noodle Bowl",
                "description": "Spicy prawn noodles with vegetables",
                "food_category": "main_course",
                "preparation_time_minutes": 20,
                "serving_size": "1",
                "serving_unit": "bowl",
                "nutrition": {
                    "calories": 510,
                    "protein_g": 28,
                    "carbohydrates_g": 60,
                    "fat_g": 16,
                    "fibre_g": 5,
                    "sugar_g": 7,
                    "sodium_mg": 820,
                },
                "tags": [spicy, comfort_food],
                "dietary_types": [non_vegetarian, dairy_free],
                "allergens": [shellfish, gluten],
                "ingredients": [prawns, noodles, vegetables],
            },
            {
                "name": "Berry Yoghurt Parfait",
                "description": "Layered yoghurt with berries and oats",
                "food_category": "dessert",
                "preparation_time_minutes": 8,
                "serving_size": "1",
                "serving_unit": "cup",
                "nutrition": {
                    "calories": 260,
                    "protein_g": 11,
                    "carbohydrates_g": 38,
                    "fat_g": 7,
                    "fibre_g": 4,
                    "sugar_g": 24,
                    "sodium_mg": 85,
                },
                "tags": [sweet, quick_meal, low_calorie],
                "dietary_types": [vegetarian],
                "allergens": [milk, gluten],
                "ingredients": [yoghurt, berries, oats],
            },
            {
                "name": "Baked Potato Meal",
                "description": "Baked potato with vegetables and light toppings",
                "food_category": "main_course",
                "preparation_time_minutes": 35,
                "serving_size": "1",
                "serving_unit": "plate",
                "nutrition": {
                    "calories": 340,
                    "protein_g": 9,
                    "carbohydrates_g": 58,
                    "fat_g": 8,
                    "fibre_g": 8,
                    "sugar_g": 4,
                    "sodium_mg": 290,
                },
                "tags": [comfort_food, low_calorie],
                "dietary_types": [vegan, gluten_free, dairy_free],
                "allergens": [],
                "ingredients": [potato, vegetables],
            },
        ]

        for item in foods:
            add_food_if_missing(db, **item)

        db.commit()
        print(f"Sample data inserted successfully ({len(foods)} foods in catalogue).")

    except Exception as error:
        db.rollback()
        print("Error while seeding data:", error)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
