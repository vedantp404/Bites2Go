# Kaggle Food & Nutrition Dataset Import Report

- **Dataset Identifier:** `adilshamim8/daily-food-and-nutrition-dataset`
- **Dataset Version:** 2
- **Author / Creator:** Adil Shamim (https://www.kaggle.com/adilshamim8)
- **License Classification:** Other (specified in description)
- **Redistribution & Attribution:** Synthetic health/nutrition dataset. The author notes: _"This dataset is not to be taken seriously. It has been synthetically generated to simulate real-world dietary records and reflects diverse food intake patterns through a randomized data generation process."_
- **Import Timestamp:** 2026-10-31 04:31:19Z
- **Pipeline Script:** [`scripts/import_kaggle_dataset.py`](../scripts/import_kaggle_dataset.py)

---

## 1. Dataset Schema & Metrics

| Metric                                  | Value    | Notes                                                                                                                                                                                     |
| :-------------------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Total Raw Records**                   | 651      | 652 lines (1 header + 651 data rows)                                                                                                                                                      |
| **Header Columns**                      | 12       | `Food_Item`, `Category`, `Calories (kcal)`, `Protein (g)`, `Carbohydrates (g)`, `Fat (g)`, `Fiber (g)`, `Sugars (g)`, `Sodium (mg)`, `Cholesterol (mg)`, `Meal_Type`, `Water_Intake (ml)` |
| **Anomalous CSV Formatting**            | 6 lines  | Fixed unquoted commas inside parentheses in `Food_Item` names                                                                                                                             |
| **Valid Records**                       | 650      | Passed physical bounds and macronutrient laws                                                                                                                                             |
| **Quarantined Records**                 | 1        | Rejected physically impossible data                                                                                                                                                       |
| **Internal Duplicates Merged**          | 58       | Redundant rows with identical nutrition within dataset                                                                                                                                    |
| **Unique Items in Dataset**             | 592      | Distinct food items before cross-catalogue deduplication                                                                                                                                  |
| **Certain Merges (Existing Catalogue)** | 75       | Exact match with existing foods (e.g. Apple, Banana, Almonds)                                                                                                                             |
| **Ambiguous Matches (Kept Separate)**   | 35       | Discrepancies > 35% calorie variance; preserved as distinct items                                                                                                                         |
| **Meaningfully Different Varieties**    | 40       | Different milk fats, preparation styles (e.g. 2% milk, steamed shrimp)                                                                                                                    |
| **Newly Imported Kaggle Foods**         | **517**  | Generated with `kaggle:` prefix in `apps/mobile/src/data/kaggleFoods.ts`                                                                                                                  |
| **Unified Search Catalogue**            | **1410** | Combined dataset-first search catalogue                                                                                                                                                   |

---

## 2. Quarantined / Rejected Records

The pipeline rejects records that violate thermodynamic and physical density limits rather than creating corrupt nutrition totals:

- **Line 486: `Corn Nuts (1 oz)`** — Physical law bound exceeded: macronutrients (102.1g) exceed 100.5g per 100g
  - Raw Values: 130.0 kcal, 2.0g P, 23.0g C, 4.0g F in Corn Nuts (1 oz)

---

## 3. Deduplication Breakdown

### A. Internal Deduplication (58 duplicate occurrences merged)

53 duplicate names were 100% identical in all nutrition fields and category. 4 duplicate names had identical nutrition values with different meal types (`Snack` vs `Lunch`):

- `tzatziki sauce (2 tbsp)` (3 occurrences merged to 1)
- `salami (3 slices)` (2 occurrences merged to 1)
- `chimichurri (1 tbsp)` (2 occurrences merged to 1)
- `olive oil (1 tbsp drizzle)` (2 occurrences merged to 1)

### B. Certain Merges with Existing Catalogue (75 foods)

Matched foods with consistent preparation and macro densities. Existing stable IDs are preserved, ensuring historical diary entries and tests are never broken:

- `Almond Milk (Unsweetened 1 cup)` -> Existing `Almond milk (Unsweetened)` (`almond-milk-unsweetened`, calorie diff: 18.7%)
- `Almonds (1 oz)` -> Existing `Almonds` (`almonds`, calorie diff: 0.3%)
- `Apple` -> Existing `Apple` (`apple`, calorie diff: 0.4%)
- `Avocado (1/2 fruit)` -> Existing `Avocado` (`avocado-raw`, calorie diff: 0.0%)
- `Avocado Toast (1 slice)` -> Existing `Avocado toast on sourdough` (`avocado-toast-sourdough`, calorie diff: 27.8%)
- `Bagel (plain)` -> Existing `Plain Bagel` (`bagel-plain`, calorie diff: 1.8%)
- `Banana` -> Existing `Banana` (`banana`, calorie diff: 0.0%)
- `BBQ Sauce (2 tbsp)` -> Existing `Barbecue Sauce (Smoky sweet)` (`sauce-barbecue`, calorie diff: 16.3%)
- `Blackberries (1 cup)` -> Existing `Blackberries` (`blackberries-fresh`, calorie diff: 20.0%)
- `Blue Cheese (1 oz)` -> Existing `Blue cheese (Gorgonzola / Roquefort)` (`cheese-blue`, calorie diff: 0.3%)
- `Blueberries (1/2 cup)` -> Existing `Blueberries` (`blueberries-fresh`, calorie diff: 18.1%)
- `Brie Cheese (1 oz)` -> Existing `Brie cheese (Soft ripened)` (`cheese-brie`, calorie diff: 0.1%)
- `Brown Rice (1 cup cooked)` -> Existing `Cooked brown rice` (`rice-brown-cooked`, calorie diff: 3.8%)
- `Caesar Salad (with chicken)` -> Existing `Chicken Caesar Salad` (`caesar-salad-chicken`, calorie diff: 15.8%)
- `Cheddar Cheese (1 oz)` -> Existing `Cheddar cheese` (`cheese-cheddar`, calorie diff: 0.5%)
- _(and 60 more verified matches)_

### C. Meaningfully Different Varieties Kept Separate (40 foods)

Foods with distinct fat contents, variety differences, or different cooking methods remain separate entries to prevent misleading nutrition:

- `Cannellini Beans (1/2 cup in soup)` != `Cannellini Beans (White kidney beans)`: Variety mismatch (set() vs {'white'})
- `Carrot (1/4 minced in sauce)` != `Carrot (Raw)`: Preparation mismatch (set() vs {'raw'})
- `Cashews (1 oz roasted)` != `Cashews (Raw)`: Preparation mismatch ({'roasted'} vs {'raw'})
- `Chicken Breast (4oz roasted)` != `Grilled chicken breast`: Preparation mismatch ({'roasted'} vs {'grilled'})
- `Chicken Thigh (1 roasted)` != `Grilled chicken thigh (Skinless)`: Preparation mismatch ({'roasted'} vs {'grilled'})
- `Cottage Cheese (1 cup low fat)` != `Low-fat cottage cheese (2% milkfat)`: Variety mismatch (set() vs {'low-fat', '2%'})
- `Cottage Cheese (1/2 cup)` != `Low-fat cottage cheese (2% milkfat)`: Variety mismatch (set() vs {'low-fat', '2%'})
- `Cucumber (1/4 cup side)` != `Cucumber (Raw with peel)`: Preparation mismatch (set() vs {'raw'})
- `Edamame (in pod 1 cup)` != `Steamed edamame pods with sea salt`: Preparation mismatch (set() vs {'steamed'})
- `Egg White (in drink)` != `Hard boiled egg white`: Preparation mismatch (set() vs {'boiled'})
- _(and 30 more separated varieties)_

### D. Ambiguous Matches Kept Separate (35 foods)

Items with > 35% calorie discrepancy between synthetic values and authoritative references were NOT merged automatically:

- `Acai Bowl (1 serving)` ?= `Acai smoothie bowl with toppings`: Calorie discrepancy 180.0% (Kaggle=350.0 vs Existing=125.0)
- `Baba Ganoush (1/4 cup)` ?= `Baba Ganoush (Eggplant dip)`: Calorie discrepancy 262.8% (Kaggle=471.7 vs Existing=130.0)
- `Cabbage Slaw (side)` ?= `Creamy coleslaw (Mayonnaise)`: Calorie discrepancy 60.5% (Kaggle=60.0 vs Existing=152.0)
- `Caprese Salad` ?= `Caprese Salad (Tomato Mozzarella)`: Calorie discrepancy 50.0% (Kaggle=240.0 vs Existing=160.0)
- `Chocolate Chip Cookie (1 large)` ?= `Chocolate Chip Cookie (Commercial)`: Calorie discrepancy 54.9% (Kaggle=220.0 vs Existing=488.0)
- `Cilantro (2 tbsp garnish)` ?= `Fresh Coriander leaves (Cilantro)`: Calorie discrepancy 85.7% (Kaggle=3.3 vs Existing=23.0)
- `Corn Flakes (1 cup)` ?= `Cornflakes with milk`: Calorie discrepancy 56.7% (Kaggle=54.1 vs Existing=125.0)
- `Corn Tortilla (1 medium)` ?= `Corn Tortilla (6-inch)`: Calorie discrepancy 76.1% (Kaggle=52.0 vs Existing=218.0)
- `Eggs Benedict (1 serving)` ?= `Eggs Benedict with hollandaise`: Calorie discrepancy 150.5% (Kaggle=601.2 vs Existing=240.0)
- `Espresso (double shot)` ?= `Espresso (1 shot)`: Calorie discrepancy 44.4% (Kaggle=5.0 vs Existing=9.0)
- _(and 25 more ambiguous foods kept separate)_

---

## 4. Dataset-First Search Architecture

1. **Tier 1 — Imported Kaggle Catalogue:** `kaggleFoods` (517 foods) prefixed with `kaggle:`.
2. **Tier 2 — Built-in Catalogue:** `foods` (894 foods) preserving baseline 0-11 and verified ICMR/USDA entries.
3. **Tier 3 — User Custom Foods:** `customFoods` and `recipes` with `custom:` / `recipe:` prefixes.

### Ranking Formula:

```ts
score = relevanceScore + tierBonus;
// where tierBonus:
//   Kaggle:   +0.4
//   Built-in: +0.2
//   Custom:   +0.0
```

- Equal match relevance prioritizes Kaggle matches first.
- Exact matches across any tier always outrank partial/prefix matches from another tier.
- Preserves the stable search header focus fix without keyboard-blur on Android.
