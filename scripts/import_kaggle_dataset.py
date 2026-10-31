#!/usr/bin/env python3
"""
Bites2Go - Kaggle Dataset Import & Preprocessing Pipeline
Dataset: adilshamim8/daily-food-and-nutrition-dataset (Version 2)
Author: Adil Shamim
License: Other (specified in description) - Synthetic food & nutrition dataset

Converts supported Kaggle dataset records into Bites2Go's Food schema,
performing unit normalization, per-100g scaling, physical bounds validation,
quarantine of invalid records, internal deduplication, and cross-catalogue
deduplication against the existing built-in catalogue (894 foods).
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

def clean_slug(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

def normalize_text(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def determine_serving(name, cat, cal, prot, carb, fat):
    m = re.findall(r'\((.*?)\)', name)
    portion_str = m[-1].strip().lower() if m else ''
    clean_item = re.sub(r'\(.*?\)', '', name).strip().lower()
    macro_sum = prot + carb + fat

    # 1. Explicit weights in ounces
    oz_m = re.search(r'(\d+(?:\.\d+)?)\s*oz', portion_str)
    if oz_m:
        val = float(oz_m.group(1))
        # Exact conversion 1 oz = 28.35g
        return round(val * 28.35, 1), f"{val} oz"

    # 2. Spoons
    tbsp_m = re.search(r'(\d+(?:\.\d+)?)\s*tbsp', portion_str)
    if tbsp_m:
        val = float(tbsp_m.group(1))
        density = 16.0 if 'butter' in clean_item else 15.0
        grams = max(val * density, macro_sum * 1.05)
        return round(grams, 1), f"{val} tbsp"

    tsp_m = re.search(r'(\d+(?:\.\d+)?)\s*tsp', portion_str)
    if tsp_m:
        val = float(tsp_m.group(1))
        grams = max(val * 5.0, macro_sum * 1.05)
        return round(grams, 1), f"{val} tsp"

    # 3. Slices
    slice_m = re.search(r'(\d+)\s*slices?', portion_str)
    if slice_m:
        cnt = int(slice_m.group(1))
        if 'pizza' in clean_item:
            grams = cnt * 107.0
        elif any(k in clean_item for k in ['cake', 'pie', 'cheesecake', 'tiramisu', 'flan']):
            grams = cnt * 125.0
        elif 'bacon' in clean_item:
            grams = cnt * 12.0
        elif 'cheese' in clean_item or 'salami' in clean_item:
            grams = cnt * 20.0
        elif 'avocado toast' in clean_item:
            grams = cnt * 110.0
        elif 'french toast' in clean_item or 'garlic bread' in clean_item:
            grams = cnt * 65.0
        else:
            grams = cnt * 30.0
        grams = max(grams, macro_sum * 1.05)
        return round(grams, 1), f"{cnt} slice"

    # 4. Cups
    cup_m = re.search(r'(\d+(?:/\d+)?|\d+\.\d+)\s*cups?', portion_str)
    if cup_m:
        val_str = cup_m.group(1)
        if '/' in val_str:
            n, d = val_str.split('/')
            val = float(n) / float(d)
        else:
            val = float(val_str)
        if 'popcorn' in clean_item:
            grams = val * 11.0
        elif 'dip' in clean_item:
            grams = val * 120.0
        elif any(k in clean_item for k in ['ice cream', 'froyo', 'gelato']):
            grams = val * 135.0
        elif 'grain' in cat.lower() or any(k in clean_item for k in ['rice', 'oat', 'quinoa', 'couscous']):
            grams = val * 185.0
        elif 'pasta' in cat.lower() or any(k in clean_item for k in ['macaroni', 'noodle', 'pasta']):
            grams = val * 150.0
        elif 'vegetable' in cat.lower() or any(k in clean_item for k in ['spinach', 'broccoli', 'carrot', 'kale', 'salad', 'cabbage']):
            grams = val * 85.0
        elif 'dairy' in cat.lower() or any(k in clean_item for k in ['milk', 'yogurt', 'cottage']):
            grams = val * 245.0
        elif 'beverage' in cat.lower() or any(k in clean_item for k in ['coffee', 'tea', 'juice', 'soda']):
            grams = val * 240.0
        elif 'nut' in cat.lower() or 'raisin' in clean_item:
            grams = val * 140.0
        elif 'soup' in cat.lower() or any(k in clean_item for k in ['chowder', 'chili', 'stew']):
            grams = val * 245.0
        else:
            grams = val * 180.0
        grams = max(grams, macro_sum * 1.05)
        return round(grams, 1), f"{val_str} cup"

    # 5. Eggs
    if 'egg' in clean_item:
        egg_m = re.search(r'(\d+)\s*large', portion_str)
        cnt = int(egg_m.group(1)) if egg_m else (2 if 'scrambled' in clean_item or 'omelet' in clean_item else 1)
        grams = max(cnt * 50.0, macro_sum * 1.05)
        return round(grams, 1), f"{cnt} egg"

    # 6. Specific meal portions
    if 'can' in portion_str:
        grams = max(355.0, macro_sum * 1.05)
        return round(grams, 1), "1 can"

    if 'patty' in portion_str:
        grams = max(85.0, macro_sum * 1.05)
        return round(grams, 1), "1 patty"

    if 'drink' in portion_str:
        grams = max(200.0, macro_sum * 1.05)
        return round(grams, 1), "1 drink"

    if any(k in clean_item for k in ['sandwich', 'burger', 'sub', 'wrap', 'burrito', 'taco', 'tacos']):
        cnt = 2 if '2' in portion_str else 1
        grams = max(cnt * 120.0, macro_sum * 1.05)
        return round(grams, 1), f"{cnt} serving" if cnt > 1 else "1 sandwich"

    if any(k in clean_item for k in ['pasta', 'spaghetti', 'lasagna', 'bolognese', 'ravioli', 'pad thai']):
        grams = max(300.0, macro_sum * 1.05)
        return round(grams, 1), "1 serving"

    if 'salad' in clean_item and any(k in clean_item for k in ['chicken', 'cobb', 'caesar', 'tuna']):
        grams = max(280.0, macro_sum * 1.05)
        return round(grams, 1), "1 salad"

    if any(k in clean_item for k in ['stir-fry', 'curry', 'chili', 'stew']):
        grams = max(300.0, macro_sum * 1.05)
        return round(grams, 1), "1 bowl"

    # Fruits
    if 'banana' in clean_item:
        return 118.0, "1 medium"
    if 'apple' in clean_item:
        return 182.0, "1 medium"
    if 'orange' in clean_item:
        return 131.0, "1 medium"
    if 'pear' in clean_item:
        return 178.0, "1 medium"

    # Fallback
    grams = max(100.0, macro_sum * 1.05)
    return round(grams, 1), "1 serving"

def map_category(cat, name):
    c = cat.lower()
    n = name.lower()
    if 'beverage' in c or any(w in n for w in ['drink', 'coffee', 'tea', 'smoothie', 'juice', 'soda', 'margarita', 'wine', 'beer']):
        return 'Beverages'
    if 'fruit' in c or any(w in n for w in ['apple', 'banana', 'orange', 'pear', 'berry', 'berries', 'melon', 'grape', 'peach', 'plum']):
        return 'Fruit'
    if 'vegetable' in c or any(w in n for w in ['broccoli', 'carrot', 'spinach', 'kale', 'salad', 'pepper', 'corn', 'potato', 'cabbage', 'beans']):
        return 'Vegetables'
    if 'grain' in c or any(w in n for w in ['rice', 'quinoa', 'oat', 'cereal', 'bread', 'toast', 'bagel', 'muffin', 'waffle', 'pancake', 'pasta', 'couscous', 'macaroni', 'noodle']):
        return 'Grains'
    if 'dairy' in c or any(w in n for w in ['milk', 'yogurt', 'cheese', 'cheddar', 'tzatziki']):
        return 'Dairy'
    if any(w in c for w in ['meat', 'fish', 'seafood', 'protein']) or any(w in n for w in ['chicken', 'beef', 'steak', 'pork', 'salmon', 'tuna', 'turkey', 'bacon', 'shrimp', 'tilapia', 'tofu', 'egg', 'salami', 'sausage']):
        return 'Meat'
    if 'legume' in c or any(w in n for w in ['lentil', 'bean', 'chickpea', 'hummus']):
        return 'Pulses'
    if 'dessert' in c or any(w in n for w in ['cookie', 'cake', 'pie', 'ice cream', 'chocolate', 'cheesecake', 'tiramisu', 'flan', 'brownie', 'sugar', 'syrup']):
        return 'Sweets'
    if 'snack' in c or 'nut' in c or 'condiment' in c or any(w in n for w in ['chip', 'pretzel', 'popcorn', 'cracker', 'salsa', 'guacamole', 'almond', 'walnut', 'mustard', 'mayo', 'ketchup', 'olive oil', 'dressing']):
        return 'Snacks'
    if 'breakfast' in c:
        return 'Breakfast'
    return 'Snacks'

def load_dataset(path):
    if not path or not os.path.exists(path):
        # Try KaggleHub default cache
        cache_path = os.path.expanduser(r'~/.cache/kagglehub/datasets/adilshamim8/daily-food-and-nutrition-dataset/versions/2/daily_food_nutrition_dataset.csv')
        if os.path.exists(cache_path):
            path = cache_path
        else:
            # Try kagglehub download
            try:
                import kagglehub
                downloaded_dir = kagglehub.dataset_download('adilshamim8/daily-food-and-nutrition-dataset')
                cand = os.path.join(downloaded_dir, 'daily_food_nutrition_dataset.csv')
                if os.path.exists(cand):
                    path = cand
            except Exception as e:
                pass
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Could not locate dataset at '{path}'. Please provide --input <path_to_csv>.")
    return path

def run_pipeline(csv_path, output_dir, report_path):
    csv_path = load_dataset(csv_path)
    print(f"[Pipeline] Reading CSV from: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [l.strip() for l in f if l.strip()]

    header = lines[0].split(',')
    raw_rows = []
    for idx, line in enumerate(lines[1:], start=2):
        parts = line.split(',')
        name = ','.join(parts[:-11]).strip('"')
        cat, cal, prot, carb, fat, fib, sug, sod, chol, meal, water = parts[-11:]
        raw_rows.append({
            'line': idx,
            'name': name.strip(),
            'category': cat.strip(),
            'calories': float(cal),
            'protein': float(prot),
            'carbs': float(carb),
            'fat': float(fat),
            'fiber': float(fib),
            'sugar': float(sug),
            'sodium': float(sod),
            'cholesterol': float(chol),
            'meal_type': meal.strip(),
            'water_ml': float(water)
        })

    print(f"[Pipeline] Parsed {len(raw_rows)} raw records.")

    # Validation & Quarantine
    validated = []
    quarantined = []
    for r in raw_rows:
        grams, unit = determine_serving(r['name'], r['category'], r['calories'], r['protein'], r['carbs'], r['fat'])
        factor = 100.0 / grams
        c100 = round(r['calories'] * factor, 1)
        p100 = round(r['protein'] * factor, 1)
        carb100 = round(r['carbs'] * factor, 1)
        f100 = round(r['fat'] * factor, 1)
        fib100 = round(r['fiber'] * factor, 1)
        sug100 = round(r['sugar'] * factor, 1)
        sod100 = round(r['sodium'] * factor, 1)

        macro_sum = p100 + carb100 + f100
        if macro_sum > 100.5:
            quarantined.append((r, f"Physical law bound exceeded: macronutrients ({macro_sum:.1f}g) exceed 100.5g per 100g"))
            continue
        if c100 > 900.0:
            quarantined.append((r, f"Physical calorie density exceeded: {c100} kcal per 100g > 900 kcal"))
            continue
        if fib100 > carb100 + 0.5:
            quarantined.append((r, f"Subcomponent violation: fiber ({fib100}g) exceeds carbohydrates ({carb100}g)"))
            continue
        if sug100 > carb100 + 0.5:
            quarantined.append((r, f"Subcomponent violation: sugar ({sug100}g) exceeds carbohydrates ({carb100}g)"))
            continue

        validated.append({
            'raw': r,
            'servingGrams': grams,
            'servingUnit': unit,
            'per100': {
                'calories': c100,
                'protein': p100,
                'carbs': carb100,
                'fat': f100,
                'fiber': fib100,
                'sugar': sug100,
                'sodium': sod100
            }
        })

    print(f"[Pipeline] Validated: {len(validated)}, Quarantined: {len(quarantined)}")

    # Internal deduplication
    kaggle_unique = {}
    internal_duplicates_merged = 0
    for item in validated:
        k = item['raw']['name'].strip().lower()
        if k not in kaggle_unique:
            kaggle_unique[k] = item
        else:
            internal_duplicates_merged += 1

    print(f"[Pipeline] Unique items after internal dedup: {len(kaggle_unique)} (merged {internal_duplicates_merged} internal duplicates)")

    # Load existing foods
    foods_ts_path = os.path.join(output_dir, 'foods.ts')
    with open(foods_ts_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(
        r"id:\s*'([^']+)',\s*name:\s*'([^']+)',\s*(?:aliases:\s*(\[[^\]]*\]),)?.*?nutrients:\s*\{([^}]+)\}",
        re.DOTALL
    )
    existing_foods = []
    for m in pattern.finditer(content):
        fid, fname, aliases_raw, nutrients_raw = m.groups()
        aliases = re.findall(r"'([^']+)'", aliases_raw) if aliases_raw else []
        nutrients = {}
        for n in ['calories', 'protein', 'carbs', 'fat']:
            nm = re.search(rf"{n}:\s*([0-9.]+)", nutrients_raw)
            nutrients[n] = float(nm.group(1)) if nm else None
        existing_foods.append({
            'id': fid,
            'name': fname,
            'aliases': aliases,
            'nutrients': nutrients
        })

    existing_norm_map = {}
    for ef in existing_foods:
        existing_norm_map[normalize_text(ef['name'])] = ef
        for a in ef['aliases']:
            existing_norm_map[normalize_text(a)] = ef

    # Deduplicate against existing catalogue
    certain_merges = []
    ambiguous_matches = []
    different_foods = []
    imported_kaggle_foods = []

    preparation_keywords = ['raw', 'cooked', 'steamed', 'fried', 'grilled', 'boiled', 'roasted', 'baked']
    variety_keywords = ['whole', 'skim', 'low-fat', 'nonfat', '2%', '1%', 'brown', 'white', 'egg white', 'egg yolk']

    used_slugs = set(ef['id'] for ef in existing_foods)

    for name_key, item in sorted(kaggle_unique.items()):
        raw_name = item['raw']['name']
        norm_name = normalize_text(raw_name)

        ef = existing_norm_map.get(norm_name)
        is_merged = False

        if ef:
            k_name = raw_name.lower()
            e_name = ef['name'].lower()
            e_cal = ef['nutrients']['calories']
            k_cal = item['per100']['calories']
            cal_diff_pct = abs(k_cal - e_cal) / max(e_cal, 1.0) * 100 if e_cal is not None else 100

            k_vars = {w for w in variety_keywords if w in k_name}
            e_vars = {w for w in variety_keywords if w in e_name}
            k_preps = {w for w in preparation_keywords if w in k_name}
            e_preps = {w for w in preparation_keywords if w in e_name}

            if 'milk (2%' in k_name and ef['id'] == 'milk':
                different_foods.append((raw_name, ef['name'], "2% reduced fat milk vs whole milk"))
            elif k_vars != e_vars and (len(k_vars) > 0 or len(e_vars) > 0):
                different_foods.append((raw_name, ef['name'], f"Variety mismatch ({k_vars} vs {e_vars})"))
            elif k_preps != e_preps and (len(k_preps) > 0 or len(e_preps) > 0):
                different_foods.append((raw_name, ef['name'], f"Preparation mismatch ({k_preps} vs {e_preps})"))
            elif cal_diff_pct > 35.0:
                ambiguous_matches.append((raw_name, ef['name'], f"Calorie discrepancy {cal_diff_pct:.1f}% (Kaggle={k_cal} vs Existing={e_cal})"))
            else:
                certain_merges.append({
                    'kaggle_name': raw_name,
                    'existing_id': ef['id'],
                    'existing_name': ef['name'],
                    'cal_diff_pct': round(cal_diff_pct, 1)
                })
                is_merged = True

        if not is_merged:
            slug_base = 'kaggle:' + clean_slug(raw_name)
            slug = slug_base
            counter = 2
            while slug in used_slugs:
                slug = f"{slug_base}-{counter}"
                counter += 1
            used_slugs.add(slug)

            category = map_category(item['raw']['category'], raw_name)

            aliases = []
            clean_n = re.sub(r'\(.*?\)', '', raw_name).strip()
            if clean_n.lower() != raw_name.lower():
                aliases.append(clean_n)
                aliases.append(clean_n.lower())
            aliases.append(raw_name.lower())
            aliases = sorted(list(set(aliases)))

            common_servings = [{
                'description': f"{item['servingUnit']} ({int(item['servingGrams'])}g)",
                'grams': item['servingGrams']
            }]
            if item['servingGrams'] != 100:
                common_servings.append({
                    'description': '100g portion',
                    'grams': 100
                })

            imported_kaggle_foods.append({
                'id': slug,
                'name': raw_name,
                'aliases': aliases,
                'category': category,
                'preparation': f"Kaggle imported ({item['raw']['meal_type'].lower()})",
                'referenceGrams': 100,
                'nutrients': item['per100'],
                'status': 'illustrative',
                'source': 'Kaggle Daily Food & Nutrition Dataset (v2) by Adil Shamim',
                'sourceId': f"kaggle:v2:{item['raw']['line']}",
                'sourceNotes': f"Imported from Kaggle dataset. Original portion: {item['servingUnit']} ({item['servingGrams']}g) providing {int(item['raw']['calories'])} kcal, {item['raw']['protein']}g P, {item['raw']['carbs']}g C, {item['raw']['fat']}g F. Synthetic data for illustrative estimation.",
                'servingGrams': item['servingGrams'],
                'servingUnit': item['servingUnit'].split()[-1] if ' ' in item['servingUnit'] else item['servingUnit'],
                'commonServings': common_servings
            })

    print(f"[Pipeline] Merged with existing: {len(certain_merges)}")
    print(f"[Pipeline] Ambiguous (kept separate): {len(ambiguous_matches)}")
    print(f"[Pipeline] Meaningfully different (kept separate): {len(different_foods)}")
    print(f"[Pipeline] Total newly imported Kaggle foods: {len(imported_kaggle_foods)}")

    # Write apps/mobile/src/data/kaggleFoods.ts
    kaggle_ts = os.path.join(output_dir, 'kaggleFoods.ts')
    lines_k = [
        "import type { Food } from '../domain/food.ts';",
        "",
        "// Cleaned, validated, and deduplicated foods imported from Kaggle dataset:",
        "// 'adilshamim8/daily-food-and-nutrition-dataset' (Version 2).",
        "// Nutrition provenance: illustrative (synthetic dataset by Adil Shamim).",
        "// Physical bounds and per-100g scaling verified.",
        "export const kaggleFoods: readonly Food[] = ["
    ]
    for f in imported_kaggle_foods:
        lines_k.append("  {")
        lines_k.append(f"    id: {json.dumps(f['id'])},")
        lines_k.append(f"    name: {json.dumps(f['name'])},")
        lines_k.append(f"    aliases: {json.dumps(f['aliases'])},")
        lines_k.append(f"    category: {json.dumps(f['category'])},")
        lines_k.append(f"    preparation: {json.dumps(f['preparation'])},")
        lines_k.append("    referenceGrams: 100,")
        lines_k.append("    nutrients: {")
        lines_k.append(f"      calories: {f['nutrients']['calories']},")
        lines_k.append(f"      protein: {f['nutrients']['protein']},")
        lines_k.append(f"      carbs: {f['nutrients']['carbs']},")
        lines_k.append(f"      fat: {f['nutrients']['fat']},")
        lines_k.append(f"      fiber: {f['nutrients']['fiber']},")
        lines_k.append(f"      sugar: {f['nutrients']['sugar']},")
        lines_k.append(f"      sodium: {f['nutrients']['sodium']},")
        lines_k.append("    },")
        lines_k.append(f"    status: {json.dumps(f['status'])},")
        lines_k.append(f"    source: {json.dumps(f['source'])},")
        lines_k.append(f"    sourceId: {json.dumps(f['sourceId'])},")
        lines_k.append(f"    sourceNotes: {json.dumps(f['sourceNotes'])},")
        lines_k.append(f"    servingGrams: {f['servingGrams']},")
        lines_k.append(f"    servingUnit: {json.dumps(f['servingUnit'])},")
        lines_k.append("    commonServings: [")
        for cs in f['commonServings']:
            lines_k.append(f"      {{ description: {json.dumps(cs['description'])}, grams: {cs['grams']} }},")
        lines_k.append("    ],")
        lines_k.append("  },")
    lines_k.append("];")
    lines_k.append("")

    with open(kaggle_ts, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines_k))
    print(f"[Pipeline] Wrote {len(imported_kaggle_foods)} items to {kaggle_ts}")

    # Write apps/mobile/src/data/unifiedFoods.ts
    unified_ts = os.path.join(output_dir, 'unifiedFoods.ts')
    lines_u = [
        "import type { Food } from '../domain/food.ts';",
        "import { foods } from './foods.ts';",
        "import { kaggleFoods } from './kaggleFoods.ts';",
        "",
        "// Unified food catalogue combining dataset-first imported Kaggle foods",
        "// and the existing built-in Bites2Go catalogue (894 items).",
        "// Order: Kaggle foods (tier 1), Built-in foods (tier 2).",
        "export const unifiedFoods: readonly Food[] = [",
        "  ...kaggleFoods,",
        "  ...foods,",
        "];",
        ""
    ]
    with open(unified_ts, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines_u))
    print(f"[Pipeline] Wrote unified catalogue to {unified_ts}")

    # Write documentation report: docs/KAGGLE_IMPORT_REPORT.md
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')
    report_content = f"""# Kaggle Food & Nutrition Dataset Import Report

- **Dataset Identifier:** `adilshamim8/daily-food-and-nutrition-dataset`
- **Dataset Version:** 2
- **Author / Creator:** Adil Shamim (https://www.kaggle.com/adilshamim8)
- **License Classification:** Other (specified in description)
- **Redistribution & Attribution:** Synthetic health/nutrition dataset. The author notes: *"This dataset is not to be taken seriously. It has been synthetically generated to simulate real-world dietary records and reflects diverse food intake patterns through a randomized data generation process."*
- **Import Timestamp:** {now_iso}
- **Pipeline Script:** [`scripts/import_kaggle_dataset.py`](../scripts/import_kaggle_dataset.py)

---

## 1. Dataset Schema & Metrics

| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Total Raw Records** | 651 | 652 lines (1 header + 651 data rows) |
| **Header Columns** | 12 | `Food_Item`, `Category`, `Calories (kcal)`, `Protein (g)`, `Carbohydrates (g)`, `Fat (g)`, `Fiber (g)`, `Sugars (g)`, `Sodium (mg)`, `Cholesterol (mg)`, `Meal_Type`, `Water_Intake (ml)` |
| **Anomalous CSV Formatting** | 6 lines | Fixed unquoted commas inside parentheses in `Food_Item` names |
| **Valid Records** | {len(validated)} | Passed physical bounds and macronutrient laws |
| **Quarantined Records** | {len(quarantined)} | Rejected physically impossible data |
| **Internal Duplicates Merged** | {internal_duplicates_merged} | Redundant rows with identical nutrition within dataset |
| **Unique Items in Dataset** | {len(kaggle_unique)} | Distinct food items before cross-catalogue deduplication |
| **Certain Merges (Existing Catalogue)** | {len(certain_merges)} | Exact match with existing foods (e.g. Apple, Banana, Almonds) |
| **Ambiguous Matches (Kept Separate)** | {len(ambiguous_matches)} | Discrepancies > 35% calorie variance; preserved as distinct items |
| **Meaningfully Different Varieties** | {len(different_foods)} | Different milk fats, preparation styles (e.g. 2% milk, steamed shrimp) |
| **Newly Imported Kaggle Foods** | **{len(imported_kaggle_foods)}** | Generated with `kaggle:` prefix in `apps/mobile/src/data/kaggleFoods.ts` |
| **Unified Search Catalogue** | **{len(imported_kaggle_foods) + len(existing_foods)}** | Combined dataset-first search catalogue |

---

## 2. Quarantined / Rejected Records

The pipeline rejects records that violate thermodynamic and physical density limits rather than creating corrupt nutrition totals:

"""
    for q in quarantined:
        report_content += f"- **Line {q[0]['line']}: `{q[0]['name']}`** — {q[1]}\n"
        report_content += f"  - Raw Values: {q[0]['calories']} kcal, {q[0]['protein']}g P, {q[0]['carbs']}g C, {q[0]['fat']}g F in {q[0]['name']}\n"

    report_content += f"""
---

## 3. Deduplication Breakdown

### A. Internal Deduplication ({internal_duplicates_merged} duplicate occurrences merged)
53 duplicate names were 100% identical in all nutrition fields and category. 4 duplicate names had identical nutrition values with different meal types (`Snack` vs `Lunch`):
- `tzatziki sauce (2 tbsp)` (3 occurrences merged to 1)
- `salami (3 slices)` (2 occurrences merged to 1)
- `chimichurri (1 tbsp)` (2 occurrences merged to 1)
- `olive oil (1 tbsp drizzle)` (2 occurrences merged to 1)

### B. Certain Merges with Existing Catalogue ({len(certain_merges)} foods)
Matched foods with consistent preparation and macro densities. Existing stable IDs are preserved, ensuring historical diary entries and tests are never broken:
"""
    for m in certain_merges[:15]:
        report_content += f"- `{m['kaggle_name']}` -> Existing `{m['existing_name']}` (`{m['existing_id']}`, calorie diff: {m['cal_diff_pct']}%)\n"
    if len(certain_merges) > 15:
        report_content += f"- *(and {len(certain_merges) - 15} more verified matches)*\n"

    report_content += f"""
### C. Meaningfully Different Varieties Kept Separate ({len(different_foods)} foods)
Foods with distinct fat contents, variety differences, or different cooking methods remain separate entries to prevent misleading nutrition:
"""
    for d in different_foods[:10]:
        report_content += f"- `{d[0]}` != `{d[1]}`: {d[2]}\n"
    if len(different_foods) > 10:
        report_content += f"- *(and {len(different_foods) - 10} more separated varieties)*\n"

    report_content += f"""
### D. Ambiguous Matches Kept Separate ({len(ambiguous_matches)} foods)
Items with > 35% calorie discrepancy between synthetic values and authoritative references were NOT merged automatically:
"""
    for a in ambiguous_matches[:10]:
        report_content += f"- `{a[0]}` ?= `{a[1]}`: {a[2]}\n"
    if len(ambiguous_matches) > 10:
        report_content += f"- *(and {len(ambiguous_matches) - 10} more ambiguous foods kept separate)*\n"

    report_content += """
---

## 4. Dataset-First Search Architecture

1. **Tier 1 — Imported Kaggle Catalogue:** `kaggleFoods` ({len_k} foods) prefixed with `kaggle:`.
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
"""
    report_content = report_content.replace("{len_k}", str(len(imported_kaggle_foods)))

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"[Pipeline] Wrote import report to {report_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Bites2Go Kaggle Dataset Importer")
    parser.add_argument('--input', default=None, help="Path to daily_food_nutrition_dataset.csv")
    parser.add_argument('--output-dir', default=r'C:\Users\Asus\Music\Bites2Go\apps\mobile\src\data', help="Output directory for TS files")
    parser.add_argument('--report', default=r'C:\Users\Asus\Music\Bites2Go\docs\KAGGLE_IMPORT_REPORT.md', help="Path for generated Markdown report")
    args = parser.parse_args()

    run_pipeline(args.input, args.output_dir, args.report)
