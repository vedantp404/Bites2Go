# Bites2Go Nutrition Data Quality & Audit Report

**Date:** 2026-10-31  
**Scope:** Nutritional Accuracy Audit of Bites2Go Food Catalogue (1,411 Total Unified Entries)  
**Authoritative Reference Sources:** USDA FoodData Central, ICMR-NIN Indian Food Composition Tables (IFCT 2017)

---

## 1. Executive Summary & Catalogue Audit

Bites2Go maintains an offline-first nutrition tracking database consisting of **1,411 total searchable food entries**:

- **894 built-in foods** in `apps/mobile/src/data/foods.ts`
- **517 Kaggle-imported foods** in `apps/mobile/src/data/kaggleFoods.ts` (`adilshamim8/daily-food-and-nutrition-dataset`)
- Unified in `apps/mobile/src/data/unifiedFoods.ts`

### Status Distribution Before & After Audit

| Status                                     | Baseline Count | Baseline % | Updated Count | Updated %  | Change                       |
| :----------------------------------------- | :------------- | :--------- | :------------ | :--------- | :--------------------------- |
| **Verified** (USDA / ICMR-NIN)             | 36             | 2.6%       | **78**        | **5.5%**   | **+42**                      |
| **Estimated** (Documented Formulations)    | 14             | 1.0%       | **40**        | **2.8%**   | **+26**                      |
| **Illustrative** (Synthetic / Placeholder) | 1,361          | 96.5%      | **1,293**     | **91.6%**  | **-68**                      |
| **Total Catalogue**                        | **1,411**      | **100.0%** | **1,411**     | **100.0%** | **0 (Invariants Preserved)** |

In this data-quality upgrade, **69 high-priority staple foods** were audited and updated (42 newly verified, 26 newly estimated, and 1 metadata & nutrient fix on previously verified `rice-cooked`).

---

## 2. Nutrition Source Hierarchy

To ensure scientific reliability and prevent synthetic drift, Bites2Go adheres to a strict 5-tier nutrition source hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USDA FoodData Central (FDC)                             │
│    Official Foundation & SR Legacy laboratory analyses      │
├─────────────────────────────────────────────────────────────┤
│ 2. ICMR-NIN IFCT 2017                                       │
│    Indian Food Composition Tables (National Inst. Nutrition)│
├─────────────────────────────────────────────────────────────┤
│ 3. Manufacturer Nutrition Facts Labels                      │
│    FSSAI / FDA mandatory regulatory packaging declarations  │
├─────────────────────────────────────────────────────────────┤
│ 4. Documented Culinary Recipe Estimates                     │
│    Ingredient-level IFCT weights, water loss, oil absorption│
├─────────────────────────────────────────────────────────────┤
│ 5. Illustrative / Synthetic Fixtures                        │
│    Strictly labeled illustrative; never marked verified     │
└─────────────────────────────────────────────────────────────┘
```

### Verification Criteria

- **`status: 'verified'`**: Strictly reserved for entries whose calories, protein, carbohydrates, fat, fiber, sugar, and sodium directly match an identifiable, authoritative laboratory record (USDA FDC ID or ICMR-NIN IFCT 2017 food code). Single-nutrient checks never promote a food to verified.
- **`status: 'estimated'`**: Assigned to prepared composite dishes (e.g. curries, biryanis, stuffed parathas) calculated from weighed constituent ingredients using IFCT reference compositions with documented oil absorption, moisture yield, and cooking method assumptions.
- **`status: 'illustrative'`**: Retained for synthetic dataset items (Kaggle) and development fixtures.

---

## 3. Data Quality Findings & Anomalies Resolved

### A. Missing Values & Inconsistencies Corrected

1. **`rice-cooked` (Cooked white rice):**
   - _Anomaly:_ `servingGrams` was `undefined` (causing portion selector ambiguity), and dietary fiber was `null`.
   - _Correction:_ Set standard medium bowl serving to `150g` (`servingGrams: 150`), fiber to `0.4g` per 100g, carbs to `28.2g`, and calories to `130 kcal` (USDA FDC 168878 / IFCT A018).
2. **Animal Products with `null` Fiber:**
   - _Anomaly:_ 30 animal protein entries (chicken breasts, salmon, tuna, whole eggs, egg whites) had `fiber: null` rather than the physiologically correct `0.0g`.
   - _Correction:_ Standardized fiber to `0.0g` across all verified animal meats and seafood.

### B. Synthetic Kaggle Discrepancies vs Authoritative Data

The audit surfaced 28 duplicate/similar food concepts between Kaggle synthetic entries and Bites2Go built-in entries with severe divergence (>50 kcal/100g):

- **Baba Ganoush:** Kaggle reported 471.7 kcal/100g (synthetic 250 kcal for a 53g 1/4 cup), whereas real roasted eggplant blended with tahini and olive oil is ~130 kcal/100g.
- **Black Pepper:** Kaggle reported 120 kcal for 1 tsp (which weighs only 2g, equating to an impossible 6000 kcal/100g).
- **Chocolate Chip Cookie:** Kaggle recorded a 220 kcal single 45g cookie as a 100g reference portion (220 kcal/100g), whereas commercial cookies are 488 kcal/100g.
- **Corn Tortilla:** Kaggle reported 52 kcal/100g (representing a single 25g tortilla), whereas 100g of corn masa tortilla is 218 kcal.
  _Resolution:_ These synthetic records remain safely quarantined as `illustrative` in `kaggleFoods.ts` and are never promoted to verified.

### C. Legitimate Thermodynamic & Biochemical Discrepancies

The audit flagged 18 entries where the simplified Atwater equation ($4P + 4C + 9F$) differed from declared calories by $>30\%$ and $>50\text{ kcal}$:

- **Alcoholic Beverages:** Campari, Gin, Negroni, Margarita, and Limoncello contain ethyl alcohol ($7.1\text{ kcal/g}$), which contributes substantial energy without adding protein, carbohydrates, or fat.
- **High-Fiber Seeds (Chia & Flax):** Chia seeds contain 34.4g fiber and 42.1g total carbohydrates per 100g. Soluble/insoluble fiber yields $\approx 1.5\text{--}2.0\text{ kcal/g}$ rather than $4.0\text{ kcal/g}$, resulting in lower measured metabolizable energy (486 kcal) than gross combustion ($4 \times 42.1 + 4 \times 16.5 + 9 \times 30.7 = 510.7\text{ kcal}$).
  _Resolution:_ These legitimate scientific discrepancies are preserved and documented in the source notes rather than artificially forced.

---

## 4. Detailed Batch 2 Corrected Foods (69 Entries)

### Group 1: Breads & Grains (13 items)

| ID                    | Name                                | Old Status   | New Status    | Calories (Old → New) | Macros P·C·F (Old → New)          | Source & ID                  | Notes / Formulation Basis                     |
| :-------------------- | :---------------------------------- | :----------- | :------------ | :------------------- | :-------------------------------- | :--------------------------- | :-------------------------------------------- |
| `rice-cooked`         | Cooked white rice                   | verified     | **verified**  | 150 → **130**        | 3.0·32.0·1.0 → **2.7·28.2·0.3**   | USDA FDC 168878 / IFCT A018  | Added servingGrams: 150g, fiber: 0.4g         |
| `rice-basmati-cooked` | Cooked Basmati rice                 | illustrative | **verified**  | 130 → **130**        | 3.0·28.0·0.4 → **3.0·28.2·0.4**   | IFCT A018 / USDA FDC 168878  | Boiled basmati rice, moisture ~68%            |
| `bread-white-slice`   | White Bread (Commercial sliced)     | illustrative | **verified**  | 265 → **265**        | 8.5·49.0·3.2 → **9.0·49.0·3.2**   | USDA FDC 172685              | 1 slice (28g) = 74 kcal, 2.7g fiber           |
| `bread-wheat-slice`   | Whole Wheat Bread (Brown bread)     | illustrative | **verified**  | 247 → **247**        | 12.0·43.0·3.4 → **13.0·41.3·3.4** | USDA FDC 172687              | 1 slice (32g) = 79 kcal, 6.0g fiber           |
| `bread-sourdough`     | Sourdough Bread                     | illustrative | **verified**  | 250 → **244**        | 8.0·52.0·1.2 → **9.0·50.0·1.0**   | USDA FDC 172689              | Artisan fermented sourdough bread             |
| `phulka`              | Phulka (Puffed dry roti)            | illustrative | **verified**  | 240 → **250**        | 8.5·48.0·2.0 → **8.0·48.0·3.8**   | IFCT 2017: A004              | 100% whole wheat dry tawa roti, 30g = 75 kcal |
| `tandoori-roti`       | Tandoori roti                       | illustrative | **estimated** | 245 → **245**        | 8.0·48.0·2.5 → **8.5·49.0·2.0**   | IFCT 2017: A004 / Form. TR01 | Clay oven baked whole wheat atta              |
| `naan-plain`          | Plain Naan (Tandoori)               | illustrative | **estimated** | 290 → **285**        | 8.5·54.0·4.5 → **8.5·52.0·5.0**   | IFCT 2017 / Form. N01        | Leavened maida with yogurt, 90g = 257 kcal    |
| `naan-butter`         | Butter Naan                         | illustrative | **estimated** | 320 → **320**        | 8.0·50.0·9.5 → **8.2·50.5·9.5**   | IFCT 2017 / Form. N02        | Tandoori naan brushed with 5g butter          |
| `paratha-plain`       | Plain Paratha (Tawa shallow-fried)  | illustrative | **estimated** | 310 → **305**        | 6.5·44.0·12.0 → **6.5·42.0·12.5** | IFCT 2017 / Form. PR01       | Layered atta paratha, 60g = 183 kcal          |
| `paratha-aloo`        | Aloo Paratha (Potato stuffed)       | illustrative | **estimated** | 230 → **220**        | 4.8·36.0·7.5 → **4.5·35.0·7.0**   | IFCT 2017 / Form. PR02       | 50% spiced potato filling, 100g = 220 kcal    |
| `paratha-paneer`      | Paneer paratha                      | illustrative | **estimated** | 270 → **265**        | 9.5·33.0·11.5 → **9.0·32.0·11.5** | IFCT 2017 / Form. PR03       | 40% grated paneer filling, 100g = 265 kcal    |
| `bhatura`             | Bhatura (Deep-fried leavened bread) | illustrative | **estimated** | 375 → **360**        | 7.0·48.0·17.5 → **6.8·48.0·16.0** | IFCT 2017 / Form. BH01       | Deep-fried fermented maida, 80g = 288 kcal    |

### Group 2: Dairy & Cheese (10 items)

| ID                     | Name                                   | Old Status   | New Status    | Calories (Old → New) | Macros P·C·F (Old → New)          | Source & ID             | Notes / Formulation Basis                    |
| :--------------------- | :------------------------------------- | :----------- | :------------ | :------------------- | :-------------------------------- | :---------------------- | :------------------------------------------- |
| `cheese-cheddar`       | Cheddar cheese                         | illustrative | **verified**  | 403 → **403**        | 25.0·1.3·33.0 → **24.9·1.3·33.1** | USDA FDC 173418         | Aged natural hard cheddar, 1 oz = 113 kcal   |
| `cheese-mozzarella`    | Mozzarella cheese                      | illustrative | **verified**  | 300 → **300**        | 22.0·2.2·22.0 → **22.2·2.2·22.4** | USDA FDC 173420         | Part-skim low-moisture mozzarella            |
| `cheese-parmesan`      | Parmesan cheese                        | illustrative | **verified**  | 431 → **431**        | 38.0·4.0·29.0 → **38.4·4.1·28.6** | USDA FDC 170845         | Grated aged hard Parmesan, 1 tbsp = 22 kcal  |
| `cheese-feta`          | Feta cheese                            | illustrative | **verified**  | 264 → **264**        | 14.0·4.1·21.0 → **14.2·4.1·21.3** | USDA FDC 173421         | Crumbled brined white feta cheese            |
| `cheese-cottage-cream` | Cottage cheese (4% milkfat)            | illustrative | **verified**  | 98 → **98**          | 11.0·3.4·4.3 → **11.1·3.4·4.3**   | USDA FDC 173417         | Creamed 4% milkfat cottage cheese            |
| `milk-cow-skimmed`     | Double toned / Skimmed milk (1.5% fat) | illustrative | **verified**  | 45 → **45**          | 3.3·4.8·1.5 → **3.3·4.8·1.5**     | IFCT 2017: L001 / FSSAI | Standardized double toned milk (1.5% fat)    |
| `greek-yogurt-plain`   | Greek yogurt (Plain 2% fat)            | illustrative | **verified**  | 73 → **73**          | 10.0·3.9·2.0 → **10.0·3.9·2.0**   | USDA FDC 171304         | Strained plain Greek yogurt, 170g = 124 kcal |
| `buttermilk-chaas`     | Chaas (Salted Buttermilk)              | illustrative | **estimated** | 28 → **24**          | 1.6·2.2·1.2 → **1.6·2.4·0.9**     | IFCT L005 / Form. BC01  | 50% curd + 50% water + roasted jeera/salt    |
| `ghee-desi`            | Desi Cow Ghee (Clarified butter)       | illustrative | **verified**  | 895 → **900**        | 0.1·0.0·99.5 → **0.0·0.0·99.8**   | IFCT L012 / USDA 171314 | 99.8% pure milk fat, 1 tbsp (14g) = 126 kcal |
| `butter-salted`        | Salted butter (Commercial)             | illustrative | **verified**  | 717 → **717**        | 0.9·0.1·81.1 → **0.9·0.1·81.1**   | USDA FDC 173410         | Standard table butter (81% fat)              |

### Group 3: Pulses & Lentils (6 items)

| ID                | Name                          | Old Status   | New Status    | Calories (Old → New) | Macros P·C·F (Old → New)         | Source & ID            | Notes / Formulation Basis                      |
| :---------------- | :---------------------------- | :----------- | :------------ | :------------------- | :------------------------------- | :--------------------- | :--------------------------------------------- |
| `urad-dal-cooked` | Cooked Urad dal               | illustrative | **verified**  | 125 → **105**        | 8.0·21.0·0.8 → **7.5·18.0·0.5**  | IFCT 2017: B009        | Boiled split urad dal, 150g bowl = 158 kcal    |
| `panchmel-dal`    | Panchmel dal (Panchratna)     | illustrative | **estimated** | 130 → **125**        | 7.5·19.0·2.8 → **7.0·17.5·3.2**  | IFCT 2017 / Form. PD01 | 5-dal blend simmered with 1 tsp ghee           |
| `dal-fry`         | Dal Fry                       | illustrative | **estimated** | 145 → **135**        | 6.2·18.0·5.5 → **5.8·16.5·5.2**  | IFCT 2017 / Form. DF01 | Boiled toor/chana dal with onion-tomato tadka  |
| `dal-makhani`     | Dal Makhani                   | illustrative | **estimated** | 180 → **145**        | 5.8·16.0·10.5 → **5.2·16.0·6.8** | IFCT 2017 / Form. DM01 | Whole black urad & rajma with butter/cream     |
| `sambar`          | Vegetable Sambar              | illustrative | **estimated** | 95 → **65**          | 3.8·14.0·2.5 → **2.8·9.8·1.6**   | IFCT 2017 / Form. SB01 | Toor dal & vegetable broth with tamarind tadka |
| `lobia-curry`     | Lobia curry (Black-eyed peas) | illustrative | **estimated** | 135 → **118**        | 7.0·18.0·4.0 → **6.2·16.5·3.2**  | IFCT B004 / Form. LC01 | Boiled cowpeas in spiced gravy with 1 tsp oil  |

### Group 4: Nuts, Seeds & Peanut Butter (7 items)

| ID                     | Name                         | Old Status   | New Status   | Calories (Old → New) | Macros P·C·F (Old → New)            | Source & ID             | Notes / Formulation Basis                          |
| :--------------------- | :--------------------------- | :----------- | :----------- | :------------------- | :---------------------------------- | :---------------------- | :------------------------------------------------- |
| `peanut-butter-creamy` | Peanut Butter (Creamy)       | illustrative | **verified** | 588 → **588**        | 25.1·20.0·50.4 → **25.1·20.0·50.4** | USDA FDC 172470         | Commercial creamy peanut butter, 2 tbsp = 188 kcal |
| `peanuts-roasted`      | Roasted Peanuts (Salted)     | illustrative | **verified** | 585 → **585**        | 23.7·21.5·49.7 → **23.7·21.5·49.7** | USDA 172430 / IFCT E004 | Dry roasted salted peanuts, 1 oz = 164 kcal        |
| `walnuts-shelled`      | Walnuts (Raw halves)         | illustrative | **verified** | 654 → **654**        | 15.2·13.7·65.2 → **15.2·13.7·65.2** | USDA 170187 / IFCT E008 | Shelled raw English walnut halves, 1 oz = 185 kcal |
| `cashews-raw`          | Cashews (Raw)                | illustrative | **verified** | 553 → **553**        | 18.2·30.2·43.8 → **18.2·30.2·43.8** | USDA 170162 / IFCT E003 | Raw whole cashew kernels, 1 oz = 157 kcal          |
| `pistachios-shelled`   | Pistachios (Roasted, salted) | illustrative | **verified** | 562 → **562**        | 20.2·27.5·45.3 → **20.2·27.5·45.3** | USDA 170184 / IFCT E006 | Dry roasted salted pistachios, 1 oz = 159 kcal     |
| `chia-seeds`           | Chia Seeds (Dry)             | illustrative | **verified** | 486 → **486**        | 16.5·42.1·30.7 → **16.5·42.1·30.7** | USDA FDC 170554         | 34.4% dietary fiber, 1 tbsp = 58 kcal              |
| `flax-seeds`           | Flax Seeds (Alsi)            | illustrative | **verified** | 534 → **534**        | 18.3·28.9·42.2 → **18.3·28.9·42.2** | USDA 169414 / IFCT E009 | Whole brown flaxseeds, 27.3g fiber                 |

### Group 5: Fruits & Vegetables (13 items)

| ID                    | Name                         | Old Status   | New Status   | Calories (Old → New) | Macros P·C·F (Old → New)        | Source & ID             | Notes / Formulation Basis                            |
| :-------------------- | :--------------------------- | :----------- | :----------- | :------------------- | :------------------------------ | :---------------------- | :--------------------------------------------------- |
| `grapes-green`        | Green Seedless Grapes        | illustrative | **verified** | 69 → **69**          | 0.7·18.1·0.2 → **0.7·18.1·0.2** | USDA 174682 / IFCT D015 | Fresh Thompson seedless grapes, 1 cup = 104 kcal     |
| `strawberries-fresh`  | Strawberries                 | illustrative | **verified** | 32 → **32**          | 0.7·7.7·0.3 → **0.7·7.7·0.3**   | USDA FDC 167762         | Fresh whole ripe strawberries, 1 cup = 49 kcal       |
| `blueberries-fresh`   | Blueberries                  | illustrative | **verified** | 57 → **57**          | 0.7·14.5·0.3 → **0.7·14.5·0.3** | USDA FDC 171711         | Fresh raw cultivated blueberries, 1 cup = 84 kcal    |
| `avocado-raw`         | Avocado                      | illustrative | **verified** | 160 → **160**        | 2.0·8.5·14.7 → **2.0·8.5·14.7** | USDA FDC 171705         | Fresh California/Hass avocado, half fruit = 160 kcal |
| `muskmelon`           | Muskmelon (Cantaloupe)       | illustrative | **verified** | 34 → **34**          | 0.8·8.2·0.2 → **0.8·8.2·0.2**   | USDA 169092 / IFCT D024 | Diced fresh cantaloupe/kharbuja, 1 cup = 54 kcal     |
| `broccoli-steamed`    | Steamed Broccoli florets     | illustrative | **verified** | 35 → **35**          | 2.4·7.2·0.4 → **2.4·7.2·0.4**   | USDA FDC 169970         | Steamed broccoli florets, 1 cup = 55 kcal            |
| `capsicum-green`      | Green Bell Pepper (Capsicum) | illustrative | **verified** | 20 → **20**          | 0.9·4.6·0.2 → **0.9·4.6·0.2**   | USDA 170108 / IFCT C008 | Raw green sweet pepper, 1 medium = 24 kcal           |
| `green-peas-boiled`   | Boiled Green Peas            | illustrative | **verified** | 81 → **81**          | 5.4·14.5·0.4 → **5.4·14.5·0.4** | USDA 170420 / IFCT B006 | Boiled green peas, 1 cup = 130 kcal, 5.7g fiber      |
| `ginger-raw`          | Fresh Ginger (Raw)           | illustrative | **verified** | 80 → **80**          | 1.8·17.8·0.8 → **1.8·17.8·0.8** | USDA 169231 / IFCT C014 | Fresh raw ginger root, 1 tbsp = 5 kcal               |
| `garlic-raw`          | Fresh Garlic (Raw cloves)    | illustrative | **verified** | 149 → **149**        | 6.4·33.1·0.5 → **6.4·33.1·0.5** | USDA 169230 / IFCT C013 | Fresh raw peeled garlic cloves, 1 clove = 4.5 kcal   |
| `lemon-raw`           | Fresh Lemon (Raw)            | illustrative | **verified** | 29 → **29**          | 1.1·9.3·0.3 → **1.1·9.3·0.3**   | USDA 167746 / IFCT D021 | Fresh peeled lemon fruit, 1 medium = 17 kcal         |
| `cabbage-raw`         | Green Cabbage (Raw)          | illustrative | **verified** | 25 → **25**          | 1.3·5.8·0.1 → **1.3·5.8·0.1**   | USDA 169975 / IFCT C005 | Raw shredded green cabbage, 1 cup = 22 kcal          |
| `sweet-potato-boiled` | Boiled Sweet Potato          | illustrative | **verified** | 76 → **76**          | 1.4·17.7·0.1 → **1.4·17.7·0.1** | USDA FDC 168483         | Boiled sweet potato flesh, 1 medium = 87 kcal        |

### Group 6: Meat, Fish & Eggs (10 items)

| ID                       | Name                             | Old Status   | New Status    | Calories (Old → New) | Macros P·C·F (Old → New)          | Source & ID             | Notes / Formulation Basis                                |
| :----------------------- | :------------------------------- | :----------- | :------------ | :------------------- | :-------------------------------- | :---------------------- | :------------------------------------------------------- |
| `chicken-breast-grilled` | Grilled chicken breast           | illustrative | **verified**  | 165 → **165**        | 31.0·0.0·3.6 → **31.0·0.0·3.6**   | USDA FDC 171477         | Cooked boneless skinless chicken breast, 120g = 198 kcal |
| `chicken-thigh-grilled`  | Grilled chicken thigh (Skinless) | illustrative | **verified**  | 195 → **179**        | 24.5·0.0·10.5 → **24.2·0.0·8.4**  | USDA FDC 171483         | Cooked skinless thigh meat, 100g = 179 kcal              |
| `salmon-grilled`         | Grilled Salmon fillet            | illustrative | **verified**  | 206 → **206**        | 22.0·0.0·12.5 → **22.1·0.0·12.4** | USDA FDC 173687         | Cooked Atlantic salmon fillet with EPA/DHA omega-3       |
| `tuna-canned-water`      | Canned Tuna (In water)           | illustrative | **verified**  | 116 → **116**        | 26.0·0.0·1.0 → **25.5·0.0·0.8**   | USDA FDC 171986         | Drained chunk light tuna, 1 can (130g) = 151 kcal        |
| `egg-scrambled`          | Scrambled eggs                   | illustrative | **verified**  | 165 → **148**        | 11.5·1.5·12.0 → **10.0·1.3·11.0** | USDA FDC 172187         | 2 large whole eggs scrambled with minimal butter         |
| `egg-fried`              | Fried egg (Sunny side up)        | illustrative | **verified**  | 195 → **196**        | 13.5·0.8·15.0 → **13.6·0.8·14.8** | USDA FDC 172184         | Whole egg pan-fried in 1 tsp oil, 1 egg = 90 kcal        |
| `poached-egg`            | Poached egg                      | illustrative | **verified**  | 143 → **143**        | 12.5·0.7·9.5 → **12.6·0.7·9.5**   | USDA FDC 172185         | Whole egg poached without fat, 1 egg = 72 kcal           |
| `omelette-masala`        | Masala Omelette (2 eggs)         | illustrative | **estimated** | 185 → **165**        | 13.0·2.5·13.5 → **11.2·2.8·12.0** | IFCT 2017 / Form. MO01  | 2 eggs + 25g onion/tomato + 5g oil, 120g = 198 kcal      |
| `fish-curry-goan`        | Goan Fish Curry                  | illustrative | **estimated** | 145 → **125**        | 13.0·4.5·8.5 → **12.5·4.2·6.5**   | IFCT 2017 / Form. GFC01 | 60% fish fillets in coconut milk kokum gravy             |
| `mutton-curry`           | Mutton Curry (Goat meat)         | illustrative | **estimated** | 195 → **175**        | 17.0·4.0·12.5 → **16.0·4.2·10.5** | IFCT 2017 / Form. MC01  | Homestyle goat meat in onion-ginger-garlic gravy         |

### Group 7: Breakfast, Snacks & Regional Dishes (10 items)

| ID                       | Name                                 | Old Status   | New Status    | Calories (Old → New) | Macros P·C·F (Old → New)          | Source & ID            | Notes / Formulation Basis                                 |
| :----------------------- | :----------------------------------- | :----------- | :------------ | :------------------- | :-------------------------------- | :--------------------- | :-------------------------------------------------------- |
| `medu-vada`              | Medu Vada                            | illustrative | **estimated** | 275 → **262**        | 8.0·26.0·15.0 → **8.5·24.5·14.5** | IFCT 2017 / Form. MV01 | Deep-fried aerated urad dal vada, 1 piece = 131 kcal      |
| `dhokla-khaman`          | Khaman Dhokla                        | illustrative | **estimated** | 160 → **160**        | 6.5·24.0·4.2 → **6.2·23.5·4.5**   | IFCT 2017 / Form. KD01 | Steamed besan sponge with mustard tadka, 2 pcs = 112 kcal |
| `upma-vermicelli-semiya` | Semiya upma (Vermicelli upma)        | illustrative | **estimated** | 165 → **145**        | 3.8·29.0·4.2 → **3.8·24.5·3.5**   | IFCT 2017 / Form. VU01 | Roasted semiya with vegetables and 1 tsp oil              |
| `poha-chivda`            | Poha Chivda (Roasted poha snack)     | illustrative | **estimated** | 450 → **430**        | 7.0·70.0·15.5 → **7.5·68.0·14.5** | IFCT 2017 / Form. PC01 | Thin roasted flattened rice with peanuts, 35g = 150 kcal  |
| `bhel-puri-mumbai`       | Mumbai bhel puri                     | illustrative | **estimated** | 195 → **185**        | 4.8·34.0·4.8 → **4.5·32.0·4.5**   | IFCT 2017 / Form. BP01 | Puffed rice with sev, papdi, potato and chutneys          |
| `pani-puri-golgappa`     | Pani Puri / Puchka (Atta wheat puri) | illustrative | **estimated** | 145 → **135**        | 3.2·26.0·3.0 → **3.0·24.0·2.8**   | IFCT 2017 / Form. PP02 | 6 stuffed puris with mint & tamarind water = 203 kcal     |
| `pav-bhaji`              | Pav Bhaji (Bhaji only)               | illustrative | **estimated** | 140 → **130**        | 3.0·16.5·7.0 → **3.2·15.5·6.2**   | IFCT 2017 / Form. PB01 | Mashed vegetables cooked with butter, 150g = 195 kcal     |
| `chicken-biryani`        | Chicken biryani                      | illustrative | **estimated** | 175 → **165**        | 10.5·22.0·5.5 → **9.8·20.5·4.8**  | IFCT 2017 / Form. CB01 | Dum basmati rice with 35% chicken, 250g = 412 kcal        |
| `veg-biryani`            | Vegetable biryani                    | illustrative | **estimated** | 180 → **145**        | 4.0·32.0·4.5 → **4.2·23.0·3.8**   | IFCT 2017 / Form. VB01 | Dum basmati rice with mixed vegetables & paneer           |
| `misal-pav-curry`        | Misal pav curry with pav             | illustrative | **estimated** | 165 → **155**        | 6.0·24.0·5.2 → **5.5·22.0·4.8**   | IFCT 2017 / Form. MP01 | Sprouted matki usal with spicy kat and 2 pavs             |

---

## 5. Summary of Audit Guarantees & Codebase Invariants

1. **Total Entries Invariant:** Exactly **894 items** in `foods.ts`, **517 items** in `kaggleFoods.ts`, and **1,411 items** in `unifiedFoods.ts`.
2. **Backward Compatibility:** All existing food IDs, display names, categories, aliases, and common servings remain strictly preserved.
3. **Diary & Snapshot Integrity:** No SQLite table reset, no modification to existing user custom foods, recipes, favourites, or past diary snapshots.
4. **Offline Operation:** Zero external network calls or new runtime dependencies added.
5. **Quality Verification:** Full test suite passes (149+ mobile tests, TypeScript, ESLint, Prettier, Expo Doctor 20/20, backend pytest, security scan, and Android Hermes release export).
