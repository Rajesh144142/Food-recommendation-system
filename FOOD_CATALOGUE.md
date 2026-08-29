# Sample Food Catalogue

This file lists the sample foods loaded by `backend/seed_sample_data.py`.

To insert / refresh missing items:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python seed_sample_data.py
```

---

## Foods overview

| ID (approx.) | Food | Category | Prep (min) | Serving | Calories | Protein (g) | Carbs (g) | Fat (g) | Fibre (g) | Sugar (g) | Sodium (mg) |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Grilled Chicken Bowl | main_course | 20 | 1 bowl | 450 | 40 | 45 | 12 | 8 | 5 | 600 |
| 2 | Spicy Paneer Wrap | main_course | 15 | 1 wrap | 520 | 22 | 55 | 24 | 6 | 8 | 700 |
| 3 | Lentil Salad | salad | 10 | 1 bowl | 320 | 18 | 40 | 8 | 12 | 4 | 350 |
| 4 | Banana Oat Smoothie | beverage | 5 | 1 glass | 280 | 12 | 48 | 6 | 5 | 22 | 90 |
| 5 | Salmon Quinoa Plate | main_course | 25 | 1 plate | 480 | 38 | 35 | 18 | 7 | 3 | 520 |
| 6 | Tofu Stir Fry | main_course | 18 | 1 bowl | 360 | 24 | 28 | 14 | 9 | 6 | 580 |
| 7 | Chickpea Buddha Bowl | main_course | 22 | 1 bowl | 420 | 16 | 52 | 16 | 14 | 5 | 410 |
| 8 | Veggie Omelette | breakfast | 12 | 1 plate | 310 | 22 | 8 | 20 | 3 | 3 | 480 |
| 9 | Peanut Butter Toast | snack | 5 | 2 slices | 390 | 14 | 42 | 18 | 6 | 12 | 320 |
| 10 | Prawn Noodle Bowl | main_course | 20 | 1 bowl | 510 | 28 | 60 | 16 | 5 | 7 | 820 |
| 11 | Berry Yoghurt Parfait | dessert | 8 | 1 cup | 260 | 11 | 38 | 7 | 4 | 24 | 85 |
| 12 | Baked Potato Meal | main_course | 35 | 1 plate | 340 | 9 | 58 | 8 | 8 | 4 | 290 |

> Note: IDs depend on insert order. If some foods already existed, new ones get the next available IDs.

---

## Tags, dietary types and allergens per food

| Food | Tags | Dietary types | Allergens | Main ingredients |
|---|---|---|---|---|
| Grilled Chicken Bowl | spicy, high_protein, quick_meal | non_vegetarian, gluten_free | — | chicken, rice, vegetables |
| Spicy Paneer Wrap | spicy, comfort_food | vegetarian | milk, gluten | paneer, vegetables, bread |
| Lentil Salad | low_calorie, high_protein, quick_meal | vegan, gluten_free, dairy_free | — | lentils, vegetables |
| Banana Oat Smoothie | sweet, quick_meal, comfort_food | vegetarian | milk, gluten | oats, banana, yoghurt |
| Salmon Quinoa Plate | high_protein | non_vegetarian, gluten_free, dairy_free | — | salmon, quinoa, vegetables |
| Tofu Stir Fry | high_protein, quick_meal, low_calorie | vegan, gluten_free, dairy_free | — | tofu, vegetables, rice |
| Chickpea Buddha Bowl | comfort_food, low_calorie | vegan, gluten_free, dairy_free | — | chickpeas, avocado, rice, vegetables |
| Veggie Omelette | high_protein, quick_meal, low_calorie | vegetarian, gluten_free | eggs, milk | eggs, vegetables, milk |
| Peanut Butter Toast | sweet, quick_meal, comfort_food | vegetarian, dairy_free | peanuts, gluten | bread, peanut_butter, banana |
| Prawn Noodle Bowl | spicy, comfort_food | non_vegetarian, dairy_free | shellfish, gluten | prawns, noodles, vegetables |
| Berry Yoghurt Parfait | sweet, quick_meal, low_calorie | vegetarian | milk, gluten | yoghurt, berries, oats |
| Baked Potato Meal | comfort_food, low_calorie | vegan, gluten_free, dairy_free | — | potato, vegetables |

---

## Lookup values used in the seed

### Tags

| Tag | Category |
|---|---|
| spicy | taste |
| sweet | taste |
| high_protein | nutrition |
| low_calorie | nutrition |
| quick_meal | context |
| comfort_food | mood |

### Dietary types

| Dietary type |
|---|
| vegetarian |
| vegan |
| non_vegetarian |
| gluten_free |
| dairy_free |

### Allergens

| Allergen |
|---|
| peanuts |
| milk |
| gluten |
| eggs |
| shellfish |

---

## Example search ideas

| Goal | Example `search_foods` filters |
|---|---|
| Spicy + high protein under 500 cal | `max_calories=500`, `min_protein=30`, `tags=["spicy"]` |
| Vegan low calorie | `dietary_types=["vegan"]`, `tags=["low_calorie"]` |
| Quick breakfast / snack | `tags=["quick_meal"]`, `food_category="breakfast"` or `"snack"` |
| Avoid peanuts | `excluded_allergens=["peanuts"]` |
| Sweet under 300 cal | `tags=["sweet"]`, `max_calories=300` |
