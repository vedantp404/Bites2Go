"""
Catalogue data part 10: Fitness, Healthy Staples, Salads, Soups, Pasta, Cafe & International (100 items).
"""

from scripts.build_full_database import F

def get_part10():
    items = []

    # =========================================================================
    # FITNESS, PROTEIN & HEALTHY SPREADS
    # =========================================================================
    items.extend([
        F("whey-protein-isolate", "Whey protein isolate powder", "Dairy", "Powder", 370, 86.0, 3.0, 1.0, 0.5, 1.0, 150, 30, "scoop", [
            {"description": "1 scoop (30g)", "grams": 30},
            {"description": "2 scoops (60g)", "grams": 60},
        ], ["whey isolate", "protein powder", "whey"], "Sports Nutrition"),
        F("whey-protein-concentrate", "Whey protein concentrate powder", "Dairy", "Powder", 400, 78.0, 8.0, 6.0, 0.5, 4.0, 180, 32, "scoop", [
            {"description": "1 scoop (32g)", "grams": 32},
            {"description": "2 scoops (64g)", "grams": 64},
        ], ["whey concentrate", "protein powder"], "Sports Nutrition"),
        F("plant-protein-powder", "Plant protein powder (Pea & Brown Rice)", "Pulses", "Powder", 380, 75.0, 10.0, 4.0, 6.0, 1.0, 320, 33, "scoop", [
            {"description": "1 scoop (33g)", "grams": 33},
        ], ["vegan protein powder", "pea protein", "plant protein"], "Sports Nutrition"),
        F("casein-protein-powder", "Micellar casein protein powder", "Dairy", "Powder", 360, 80.0, 5.0, 1.5, 0.5, 2.0, 200, 33, "scoop", [
            {"description": "1 scoop (33g)", "grams": 33},
        ], ["casein powder", "slow release protein"], "Sports Nutrition"),
        F("protein-bar-chocolate", "High protein bar (Chocolate)", "Snacks", "Ready to eat", 350, 33.0, 35.0, 11.0, 16.0, 2.0, 280, 60, "bar", [
            {"description": "1 bar (60g)", "grams": 60},
        ], ["protein bar", "nutrition bar", "quest bar"], "Sports Nutrition", image_key="chocolate"),
        F("peanut-butter-crunchy-spread", "Crunchy peanut butter", "Nuts", "Ready to eat spread", 590, 25.0, 19.5, 51.0, 7.0, 8.5, 420, 32, "tbsp", [
            {"description": "1 tbsp (16g)", "grams": 16},
            {"description": "2 tbsp / 1 serving (32g)", "grams": 32},
        ], ["chunky peanut butter", "crunchy peanut butter"], "Nut Butters"),
        F("peanut-butter-natural", "Natural unsweetened peanut butter", "Nuts", "Ready to eat spread", 570, 26.0, 16.0, 50.0, 8.5, 3.5, 10, 32, "tbsp", [
            {"description": "1 tbsp (16g)", "grams": 16},
            {"description": "2 tbsp (32g)", "grams": 32},
        ], ["natural peanut butter", "100% peanut butter", "unsweetened pb"], "Nut Butters"),
        F("almond-butter", "Almond butter", "Nuts", "Ready to eat spread", 614, 21.0, 19.0, 55.5, 10.5, 4.4, 7, 32, "tbsp", [
            {"description": "1 tbsp (16g)", "grams": 16},
            {"description": "2 tbsp (32g)", "grams": 32},
        ], ["almond butter", "badam butter"], "Nut Butters", image_key="almonds"),
        F("cashew-butter", "Cashew butter", "Nuts", "Ready to eat spread", 587, 18.0, 27.5, 49.0, 2.0, 5.0, 15, 32, "tbsp", [
            {"description": "1 tbsp (16g)", "grams": 16},
            {"description": "2 tbsp (32g)", "grams": 32},
        ], ["cashew butter", "kaju butter"], "Nut Butters"),
        F("sunflower-seed-butter", "Sunflower seed butter (SunButter)", "Nuts", "Ready to eat spread", 617, 20.0, 22.0, 52.0, 5.8, 3.0, 110, 32, "tbsp", [
            {"description": "2 tbsp (32g)", "grams": 32},
        ], ["sunflower butter", "sunbutter"], "Nut Butters"),
        F("hemp-seeds", "Hemp seeds (hulled hearts)", "Nuts", "Raw, hulled", 553, 31.5, 8.7, 48.7, 4.0, 1.5, 5, 30, "tbsp", [
            {"description": "1 tbsp (10g)", "grams": 10},
            {"description": "3 tbsp (30g)", "grams": 30},
        ], ["hemp hearts", "hemp seeds"], "Seeds"),
        F("sunflower-seeds-roasted", "Roasted sunflower seeds", "Nuts", "Roasted, unsalted", 582, 19.3, 24.1, 49.8, 11.1, 2.7, 3, 28, "oz", [
            {"description": "1 tbsp (10g)", "grams": 10},
            {"description": "1 oz / handful (28g)", "grams": 28},
        ], ["sunflower seeds", "roasted sunflower seeds"], "Seeds"),
        F("pumpkin-seeds-roasted", "Roasted pumpkin seeds (Pepitas)", "Nuts", "Roasted, unsalted", 559, 30.2, 10.7, 49.0, 6.0, 1.4, 7, 28, "oz", [
            {"description": "1 tbsp (10g)", "grams": 10},
            {"description": "1 oz (28g)", "grams": 28},
        ], ["pumpkin seeds", "pepitas"], "Seeds"),
        F("sesame-seeds-white", "White sesame seeds", "Nuts", "Raw / lightly toasted", 573, 17.7, 23.4, 49.7, 11.8, 0.3, 11, 15, "tbsp", [
            {"description": "1 tbsp (10g)", "grams": 10},
            {"description": "1 standard serving (15g)", "grams": 15},
        ], ["til", "white til", "sesame seeds"], "Seeds"),
        F("sesame-seeds-black", "Black sesame seeds", "Nuts", "Raw", 570, 18.0, 23.0, 50.0, 12.0, 0.3, 11, 15, "tbsp", [
            {"description": "1 tbsp (10g)", "grams": 10},
        ], ["kala til", "black til", "black sesame"], "Seeds"),
        F("flax-seeds-ground", "Ground flaxseed meal", "Nuts", "Milled, raw", 534, 18.3, 28.9, 42.2, 27.3, 1.5, 30, 15, "tbsp", [
            {"description": "1 tbsp (7g)", "grams": 7},
            {"description": "2 tbsp (14g)", "grams": 14},
        ], ["ground flaxseed", "flax meal", "alsi powder"], "Seeds"),
        F("boiled-egg-white", "Hard boiled egg white", "Dairy", "Boiled, plain", 52, 11.0, 0.7, 0.2, None, 0.7, 166, 33, "large white", [
            {"description": "1 large egg white (33g)", "grams": 33},
            {"description": "2 large egg whites (66g)", "grams": 66},
            {"description": "3 large egg whites (100g)", "grams": 100},
        ], ["egg white", "boiled egg white"], "Eggs", image_key="egg"),
        F("boiled-egg-whole", "Hard boiled whole egg", "Dairy", "Boiled, shell removed", 155, 12.6, 1.1, 10.6, None, 1.1, 124, 50, "large egg", [
            {"description": "1 large egg (50g)", "grams": 50},
            {"description": "2 large eggs (100g)", "grams": 100},
        ], ["boiled egg", "hard boiled egg", "anda"], "Eggs", image_key="egg"),
        F("scrambled-egg", "Scrambled eggs with butter", "Dairy", "Cooked with butter and milk", 166, 10.0, 1.5, 13.0, None, 1.3, 180, 100, "2-egg serving", [
            {"description": "1 large egg scrambled (55g)", "grams": 55},
            {"description": "2 eggs scrambled (110g)", "grams": 110},
        ], ["scrambled eggs", "scrambled egg"], "Eggs", image_key="egg"),
        F("poached-egg", "Poached egg", "Dairy", "Poached in water", 143, 12.5, 0.8, 9.5, None, 0.7, 140, 50, "egg", [
            {"description": "1 poached egg (50g)", "grams": 50},
            {"description": "2 poached eggs (100g)", "grams": 100},
        ], ["poached egg"], "Eggs", image_key="egg"),
        F("omelette-2egg", "Plain 2-egg omelette", "Dairy", "Pan cooked with oil", 185, 12.0, 1.2, 15.0, None, 0.8, 190, 100, "omelette", [
            {"description": "1 2-egg omelette (100g)", "grams": 100},
        ], ["omelet", "plain omelette", "egg omelette"], "Eggs", image_key="egg"),
        F("beef-tenderloin-grilled", "Grilled beef tenderloin fillet", "Meat", "Grilled, trimmed lean", 205, 30.5, 0.0, 9.0, None, 0.0, 55, 150, "steak", [
            {"description": "1 steak (150g)", "grams": 150},
            {"description": "1 large cut (220g)", "grams": 220},
        ], ["tenderloin steak", "filet mignon", "grilled beef"], "Beef"),
        F("ground-turkey-lean", "Lean ground turkey (93% lean)", "Meat", "Cooked, pan-browned", 195, 27.0, 0.0, 9.5, None, 0.0, 80, 112, "serving (4 oz)", [
            {"description": "4 oz patty (112g)", "grams": 112},
        ], ["ground turkey", "turkey mince"], "Poultry"),
        F("pork-tenderloin-roasted", "Roasted pork tenderloin", "Meat", "Roasted lean tenderloin", 143, 26.0, 0.0, 3.5, None, 0.0, 52, 120, "serving", [
            {"description": "1 portion (120g)", "grams": 120},
        ], ["pork tenderloin", "roasted pork"], "Pork"),
        F("duck-breast-roasted", "Roasted duck breast (Skinless)", "Meat", "Roasted skinless duck breast", 140, 28.0, 0.0, 2.5, None, 0.0, 65, 120, "breast", [
            {"description": "1 breast (120g)", "grams": 120},
        ], ["duck breast", "roasted duck"], "Poultry"),
        F("haddock-fillet-baked", "Baked haddock fillet", "Meat", "Baked with herbs and lemon", 105, 23.0, 0.0, 1.0, None, 0.0, 85, 150, "fillet", [
            {"description": "1 fillet (150g)", "grams": 150},
        ], ["haddock fillet", "baked haddock", "white fish"], "Fish"),
        F("tilapia-fillet-baked", "Baked tilapia fillet", "Meat", "Baked seasoned fillet", 128, 26.0, 0.0, 2.7, None, 0.0, 56, 120, "fillet", [
            {"description": "1 fillet (120g)", "grams": 120},
        ], ["tilapia", "baked tilapia"], "Fish"),
        F("crab-meat-steamed", "Steamed blue crab meat", "Meat", "Steamed, shell removed", 97, 20.0, 0.0, 1.5, None, 0.0, 290, 85, "serving", [
            {"description": "1 portion (85g)", "grams": 85},
        ], ["crab meat", "blue crab", "steamed crab"], "Seafood"),
        F("king-crab-legs-steamed", "Steamed king crab legs", "Meat", "Steamed with lemon", 98, 20.5, 1.3, 0.9, None, 0.0, 380, 115, "tail", [
            {"description": "1 small portion (115g)", "grams": 115},
        ], ["king crab", "steamed crab legs"], "Seafood"),
        F("scallops-pan-seared", "Pan-seared sea scallops", "Meat", "Seared in olive oil", 137, 24.0, 5.0, 2.0, None, 0.0, 390, 100, "serving (4-5 scallops)", [
            {"description": "4-5 large scallops (100g)", "grams": 100},
        ], ["seared scallops", "sea scallops"], "Seafood"),
        F("salmon-baked-fillet", "Baked Atlantic salmon", "Meat", "Baked with herbs and olive oil", 206, 22.0, 0.0, 12.3, None, 0.0, 60, 150, "fillet", [
            {"description": "1 small fillet (120g)", "grams": 120},
            {"description": "1 standard fillet (170g)", "grams": 170},
        ], ["baked salmon", "salmon fillet", "grilled salmon"], "Fish", image_key="salmon"),
        F("salmon-smoked", "Smoked salmon slices", "Meat", "Cold smoked slices", 117, 18.3, 0.0, 4.3, None, 0.0, 784, 50, "serving", [
            {"description": "2 slices (50g)", "grams": 50},
            {"description": "100g portion", "grams": 100},
        ], ["lox", "smoked salmon"], "Fish", image_key="salmon"),
        F("shrimp-grilled-garlic", "Grilled shrimp / prawns", "Meat", "Grilled with garlic and herbs", 120, 23.0, 1.0, 2.0, None, 0.0, 380, 100, "serving", [
            {"description": "5 large shrimp (85g)", "grams": 85},
            {"description": "100g serving", "grams": 100},
        ], ["grilled prawns", "shrimp", "prawns"], "Seafood"),
        F("greek-yogurt-plain-0fat", "Non-fat Greek yogurt (Plain)", "Dairy", "Strained, non-fat", 59, 10.3, 3.6, 0.4, None, 3.2, 36, 170, "container", [
            {"description": "1 small tub (150g)", "grams": 150},
            {"description": "1 cup (200g)", "grams": 200},
        ], ["0% greek yogurt", "non fat greek yogurt", "strained yogurt"], "Cultured Dairy", image_key="curd"),
        F("greek-yogurt-plain-whole", "Whole milk Greek yogurt (Plain)", "Dairy", "Strained, whole milk", 97, 9.0, 4.0, 5.0, None, 3.8, 35, 170, "container", [
            {"description": "1 container (170g)", "grams": 170},
            {"description": "1 cup (200g)", "grams": 200},
        ], ["greek yogurt whole", "full fat greek yogurt"], "Cultured Dairy", image_key="curd"),
        F("cottage-cheese-lowfat", "Low-fat cottage cheese (2% milkfat)", "Dairy", "Plain curd", 81, 11.0, 4.5, 2.3, None, 4.0, 340, 113, "1/2 cup", [
            {"description": "1/2 cup (113g)", "grams": 113},
            {"description": "1 cup (226g)", "grams": 226},
        ], ["cottage cheese", "low fat cottage cheese"], "Fresh Cheese"),
        F("skyr-plain", "Icelandic skyr (Plain)", "Dairy", "Strained traditional skyr", 65, 11.0, 4.0, 0.2, None, 3.5, 45, 150, "cup", [
            {"description": "1 tub (150g)", "grams": 150},
        ], ["skyr", "icelandic yogurt"], "Cultured Dairy", image_key="curd"),
        F("kefir-plain", "Plain kefir (Cultured milk)", "Dairy", "Fermented liquid", 64, 3.5, 4.8, 3.5, None, 4.5, 40, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["kefir", "milk kefir"], "Cultured Dairy", image_key="milk"),
        F("tofu-silken-fresh", "Silken tofu (Raw)", "Dairy", "Steamed / fresh", 55, 5.5, 2.0, 2.8, 0.5, 0.5, 10, 100, "slice", [
            {"description": "1 block / serving (100g)", "grams": 100},
        ], ["silken tofu", "soft tofu"], "Soy Products"),
        F("tempeh-pan-fried-soy", "Pan-fried organic tempeh", "Pulses", "Fermented whole soy cake pan-fried", 195, 19.0, 9.0, 11.0, 8.0, 1.0, 15, 85, "serving", [
            {"description": "3 slices (85g)", "grams": 85},
        ], ["tempeh", "fried tempeh"], "Soy Products"),
        F("edamame-in-pods", "Steamed edamame pods with sea salt", "Vegetables", "Steamed whole pods in salt", 122, 11.9, 8.9, 5.2, 5.2, 2.2, 240, 150, "cup (with pods)", [
            {"description": "1 cup pods (150g)", "grams": 150},
        ], ["edamame", "soybeans in pod"], "Legumes"),
        F("seitan-wheat-gluten", "Cooked seitan (Vital wheat gluten)", "Grains", "Simmered seasoned gluten cutlet", 145, 24.5, 4.0, 1.8, 1.5, 0.5, 320, 85, "cutlet", [
            {"description": "1 cutlet (85g)", "grams": 85},
        ], ["seitan", "wheat meat", "gluten"], "Plant Protein"),
        F("spirulina-powder-pure", "Organic spirulina powder", "Vegetables", "Dry powder", 290, 57.0, 24.0, 7.7, 3.6, 3.1, 1048, 5, "tsp", [
            {"description": "1 tsp (5g)", "grams": 5},
            {"description": "1 tbsp (10g)", "grams": 10},
        ], ["spirulina", "blue green algae"], "Superfoods"),
        F("matcha-green-tea-powder", "Japanese ceremonial matcha powder", "Beverages", "Pure stone-ground green tea", 324, 30.6, 38.5, 5.3, 38.5, 0.0, 6, 2, "g", [
            {"description": "1/2 tsp / 1 serving (2g)", "grams": 2},
        ], ["matcha", "green tea powder"], "Teas", image_key="tea"),
        F("maca-root-powder-organic", "Organic maca root powder", "Vegetables", "Dry milled root", 325, 14.0, 65.0, 2.0, 7.0, 32.0, 18, 5, "tsp", [
            {"description": "1 tsp (5g)", "grams": 5},
        ], ["maca powder", "maca root"], "Superfoods"),
    ])

    # =========================================================================
    # HEALTHY SALADS & BOWLS
    # =========================================================================
    items.extend([
        F("sprouted-moong-salad", "Sprouted moong salad", "Salads", "Raw sprouted with lemon, onion and tomato", 85, 5.5, 14.0, 0.8, 4.0, 2.5, 120, 150, "bowl", [
            {"description": "1 small katori (100g)", "grams": 100},
            {"description": "1 medium bowl (150g)", "grams": 150},
        ], ["moong sprout salad", "sprouts salad", "ankurit moong"], "Indian Salads"),
        F("sprouted-mixed-salad", "Mixed bean sprouts salad", "Salads", "Raw mixed sprouts with chaat masala", 92, 6.0, 15.0, 1.0, 4.5, 2.0, 140, 150, "bowl", [
            {"description": "1 bowl (150g)", "grams": 150},
        ], ["mixed sprouts", "sprouts chaat"], "Indian Salads"),
        F("cucumber-tomato-koshimbir", "Cucumber koshimbir with peanuts", "Salads", "Chopped cucumber with roasted peanuts and lemon", 68, 2.2, 5.0, 4.5, 1.8, 2.2, 110, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
            {"description": "1 medium bowl (150g)", "grams": 150},
        ], ["khamang kakdi", "koshimbir", "cucumber peanut salad"], "Maharashtrian", image_key="carrot"),
        F("beetroot-salad", "Grated beetroot salad", "Salads", "Raw grated with mustard seasoning and lemon", 55, 1.6, 9.5, 1.2, 2.5, 6.5, 130, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["beet salad", "beetroot koshimbir"], "Indian Salads"),
        F("greek-salad-mediterranean", "Greek salad with feta cheese", "Salads", "Cucumber, tomato, olives, red onion and feta", 110, 3.5, 5.0, 8.5, 1.8, 3.2, 380, 200, "plate", [
            {"description": "1 side salad (120g)", "grams": 120},
            {"description": "1 meal salad (250g)", "grams": 250},
        ], ["greek salad", "horiatiki"], "Mediterranean"),
        F("quinoa-vegetable-salad", "Quinoa vegetable salad", "Salads", "Cooked quinoa with diced vegetables and lemon vinaigrette", 125, 4.0, 20.0, 3.5, 2.8, 1.8, 160, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["quinoa salad", "healthy grain bowl"], "Grain Salads"),
        F("chickpea-mediterranean-salad", "Mediterranean chickpea salad", "Salads", "Chickpeas, cucumber, bell pepper, parsley and lemon", 135, 6.0, 20.0, 3.5, 5.0, 3.0, 190, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["garbanzo salad", "chana salad mediterranean"], "Bean Salads"),
        F("fattoush-salad", "Fattoush salad with toasted pita", "Salads", "Mixed greens, radish, tomato, sumac and crispy pita", 85, 2.0, 11.0, 4.0, 2.0, 2.5, 220, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["fattoush", "lebanese salad"], "Middle Eastern"),
        F("coleslaw-mayo", "Creamy coleslaw (Mayonnaise)", "Salads", "Shredded cabbage and carrots in mayonnaise dressing", 152, 1.2, 13.0, 11.0, 2.0, 10.0, 260, 100, "serving", [
            {"description": "1 scoop (75g)", "grams": 75},
            {"description": "1 side cup (120g)", "grams": 120},
        ], ["coleslaw", "slaw", "cabbage slaw"], "Western Salads"),
        F("coleslaw-vinaigrette", "Vinegar coleslaw (No mayo)", "Salads", "Shredded cabbage and carrots in apple cider vinaigrette", 65, 1.3, 10.0, 2.5, 2.2, 6.8, 180, 100, "serving", [
            {"description": "1 cup (100g)", "grams": 100},
        ], ["vinegar slaw", "oil and vinegar slaw"], "Western Salads"),
        F("kimchi", "Traditional Korean kimchi", "Salads", "Fermented napa cabbage with chili and garlic", 23, 1.8, 4.0, 0.5, 2.4, 1.5, 670, 50, "serving", [
            {"description": "1 small dish (50g)", "grams": 50},
            {"description": "1/2 cup (75g)", "grams": 75},
        ], ["kimchi", "korean kimchi", "baechu kimchi"], "Fermented"),
        F("sauerkraut", "Sauerkraut (Fermented cabbage)", "Salads", "Raw fermented cabbage", 19, 0.9, 4.3, 0.1, 2.9, 1.8, 660, 60, "serving", [
            {"description": "1/4 cup (60g)", "grams": 60},
            {"description": "1/2 cup (120g)", "grams": 120},
        ], ["sauerkraut", "fermented cabbage"], "Fermented"),
    ])

    # =========================================================================
    # SOUPS & BROTHS
    # =========================================================================
    items.extend([
        F("chicken-bone-broth", "Simmered chicken bone broth", "Soups", "Simmered bone broth", 32, 6.0, 0.5, 0.8, None, 0.2, 340, 240, "cup", [
            {"description": "1 mug (240ml)", "grams": 240},
            {"description": "1 bowl (350ml)", "grams": 350},
        ], ["bone broth", "chicken broth"], "Broths"),
        F("chicken-clear-soup", "Clear chicken soup", "Soups", "Poached chicken and herbs in broth", 48, 5.5, 2.0, 1.8, 0.4, 0.5, 360, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["clear soup", "chicken soup"], "Broths"),
        F("sweet-corn-chicken-soup", "Sweet corn chicken soup", "Soups", "Indo-Chinese style with shredded chicken and egg drop", 65, 4.5, 8.5, 1.8, 0.8, 2.5, 380, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["corn soup chicken", "sweet corn soup"], "Indo-Chinese"),
        F("sweet-corn-veg-soup", "Sweet corn vegetable soup", "Soups", "Indo-Chinese style with sweet corn and minced vegetables", 55, 1.8, 10.5, 0.8, 1.2, 3.0, 370, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["veg corn soup", "sweet corn veg"], "Indo-Chinese"),
        F("hot-sour-veg-soup", "Hot and sour vegetable soup", "Soups", "Spicy and tangy vegetable soup Indo-Chinese", 50, 2.0, 8.0, 1.2, 1.5, 2.0, 440, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["hot and sour veg", "hot sour soup"], "Indo-Chinese"),
        F("hot-sour-chicken-soup", "Hot and sour chicken soup", "Soups", "Spicy and sour chicken soup with mushrooms", 68, 5.5, 7.5, 2.0, 1.0, 1.8, 460, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["chicken hot and sour", "hot sour chicken"], "Indo-Chinese"),
        F("tomato-soup-cream", "Creamy tomato soup", "Soups", "Pureed tomatoes finished with fresh cream", 68, 1.5, 10.0, 2.8, 1.4, 5.5, 410, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["tomato soup", "cream of tomato"], "Western Soups", image_key="tomato"),
        F("minestrone-soup", "Italian vegetable minestrone", "Soups", "Vegetable soup with beans, pasta and tomato broth", 58, 2.8, 9.5, 1.0, 2.2, 2.5, 380, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["minestrone", "vegetable bean soup"], "Western Soups"),
        F("mushroom-soup-cream", "Cream of mushroom soup", "Soups", "Sautéed mushrooms simmered with cream and garlic", 75, 1.8, 6.5, 5.0, 0.8, 1.5, 390, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["mushroom soup", "cream of mushroom"], "Western Soups"),
        F("lentil-lemon-soup", "Middle Eastern yellow lentil soup (Shorba)", "Soups", "Yellow lentils simmered with cumin and lemon", 72, 4.2, 11.5, 1.2, 2.8, 1.0, 310, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["lentil soup", "shorbat adas", "arabic lentil soup"], "Middle Eastern", image_key="dal"),
        F("miso-soup", "Japanese miso soup with tofu", "Soups", "Fermented soybean paste broth with silken tofu and seaweed", 35, 2.8, 3.5, 1.2, 0.8, 1.2, 540, 200, "bowl", [
            {"description": "1 bowl (200ml)", "grams": 200},
        ], ["miso soup", "japanese soup"], "Japanese"),
        F("pumpkin-soup", "Roasted pumpkin soup", "Soups", "Roasted butternut squash and pumpkin with coconut milk", 52, 1.2, 9.0, 1.5, 1.8, 4.0, 290, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["pumpkin soup", "squash soup"], "Western Soups"),
    ])

    # =========================================================================
    # PASTAS & NOODLES
    # =========================================================================
    items.extend([
        F("pasta-penne-arrabbiata", "Penne all'Arrabbiata", "Pasta", "Cooked penne with spicy tomato and garlic sauce", 135, 4.5, 24.0, 2.5, 2.2, 3.0, 310, 250, "plate", [
            {"description": "1 regular plate (250g)", "grams": 250},
            {"description": "1 large serving (350g)", "grams": 350},
        ], ["penne arrabbiata", "spicy pasta", "red sauce pasta"], "Italian Pasta", image_key="pasta"),
        F("pasta-fettuccine-alfredo", "Fettuccine Alfredo", "Pasta", "Pasta in rich parmesan and butter cream sauce", 215, 6.5, 22.0, 11.5, 1.2, 1.5, 380, 250, "plate", [
            {"description": "1 plate (250g)", "grams": 250},
        ], ["fettuccine alfredo", "white sauce pasta", "alfredo"], "Italian Pasta", image_key="pasta"),
        F("pasta-spaghetti-bolognese", "Spaghetti Bolognese", "Pasta", "Spaghetti with slow-cooked minced beef tomato ragù", 158, 8.5, 18.5, 5.8, 1.8, 2.8, 340, 280, "plate", [
            {"description": "1 plate (280g)", "grams": 280},
        ], ["spaghetti bolognese", "bolognese pasta", "spag bol"], "Italian Pasta", image_key="pasta"),
        F("pasta-spaghetti-aglio-olio", "Spaghetti aglio e olio", "Pasta", "Spaghetti tossed with garlic, chili flakes and extra virgin olive oil", 185, 4.8, 26.0, 7.2, 1.5, 0.8, 220, 220, "plate", [
            {"description": "1 plate (220g)", "grams": 220},
        ], ["spaghetti aglio olio", "aglio e olio"], "Italian Pasta", image_key="pasta"),
        F("pasta-mac-and-cheese", "Baked macaroni and cheese", "Pasta", "Elbow macaroni baked in rich cheddar cheese sauce", 220, 8.0, 23.0, 11.0, 1.2, 2.5, 480, 200, "bowl", [
            {"description": "1 small bowl (150g)", "grams": 150},
            {"description": "1 large serving (250g)", "grams": 250},
        ], ["mac and cheese", "macaroni cheese"], "Comfort Food", image_key="pasta"),
        F("pasta-lasagna-beef", "Beef lasagna", "Pasta", "Layered pasta with ground beef, béchamel, tomato sauce and mozzarella", 175, 9.5, 14.0, 8.8, 1.4, 2.8, 410, 250, "slice", [
            {"description": "1 slice (250g)", "grams": 250},
        ], ["lasagna", "lasagne", "beef lasagna"], "Italian Pasta", image_key="pasta"),
        F("pasta-lasagna-spinach-ricotta", "Spinach and ricotta lasagna", "Pasta", "Layered pasta with fresh spinach, ricotta and tomato sauce", 145, 7.0, 15.0, 6.2, 1.8, 3.0, 350, 250, "slice", [
            {"description": "1 slice (250g)", "grams": 250},
        ], ["veg lasagna", "spinach lasagna"], "Italian Pasta", image_key="pasta"),
        F("noodles-hakka-chicken", "Chicken Hakka noodles", "Grains", "Stir-fried noodles with chicken, eggs, and crisp vegetables", 175, 8.5, 24.5, 5.0, 1.8, 1.2, 420, 220, "plate", [
            {"description": "1 plate (220g)", "grams": 220},
        ], ["chicken hakka noodles", "chicken chow mein"], "Indo-Chinese"),
        F("noodles-schezwan-veg", "Vegetable Schezwan noodles", "Grains", "Spicy stir-fried noodles with Schezwan sauce and vegetables", 168, 3.6, 28.0, 4.8, 2.0, 2.2, 490, 200, "plate", [
            {"description": "1 plate (200g)", "grams": 200},
        ], ["schezwan noodles", "spicy noodles"], "Indo-Chinese"),
        F("ramen-shoyu", "Shoyu ramen with chashu pork", "Soups", "Soy-flavored broth with wheat ramen noodles, sliced pork and soft egg", 130, 6.5, 14.5, 5.2, 1.0, 1.2, 580, 400, "large bowl", [
            {"description": "1 complete ramen bowl (450g)", "grams": 450},
        ], ["shoyu ramen", "ramen noodles", "japanese ramen"], "Japanese"),
        F("ramen-miso", "Miso ramen with pork broth", "Soups", "Rich miso pork broth with ramen noodles, corn, bamboo and egg", 145, 7.0, 15.0, 6.5, 1.5, 2.0, 620, 450, "large bowl", [
            {"description": "1 complete bowl (450g)", "grams": 450},
        ], ["miso ramen", "ramen bowl"], "Japanese"),
        F("pad-thai-tofu", "Vegetarian tofu Pad Thai", "Grains", "Rice noodles stir-fried with firm tofu, vegetables, peanuts and tamarind sauce", 155, 6.0, 23.0, 4.8, 2.2, 4.5, 360, 250, "plate", [
            {"description": "1 standard plate (250g)", "grams": 250},
        ], ["tofu pad thai", "veg pad thai"], "Thai"),
        F("noodles-soba-cooked", "Cooked Japanese soba noodles", "Grains", "Boiled buckwheat noodles", 99, 5.1, 21.4, 0.1, 1.5, 0.2, 60, 150, "bowl", [
            {"description": "1 bowl (150g)", "grams": 150},
        ], ["soba", "buckwheat noodles", "zaru soba"], "Japanese"),
        F("noodles-udon-cooked", "Cooked Japanese udon noodles", "Grains", "Thick boiled wheat noodles", 105, 3.2, 22.5, 0.4, 1.0, 0.3, 85, 180, "bowl", [
            {"description": "1 serving (180g)", "grams": 180},
        ], ["udon", "udon noodles"], "Japanese"),
        F("rice-vermicelli-cooked", "Cooked rice vermicelli noodles", "Grains", "Boiled thin rice noodles", 108, 1.8, 24.2, 0.2, 0.8, 0.1, 5, 150, "cup portion", [
            {"description": "1 cup cooked (150g)", "grams": 150},
        ], ["rice noodles", "vermicelli", "rice sev"], "Rice"),
    ])

    # =========================================================================
    # INTERNATIONAL BREAKFAST & CAFE
    # =========================================================================
    items.extend([
        F("avocado-toast-sourdough", "Avocado toast on sourdough", "Breakfast", "Toasted sourdough bread topped with mashed avocado, chili flakes and olive oil", 185, 4.5, 18.0, 11.0, 4.5, 1.0, 240, 130, "slice", [
            {"description": "1 slice with avocado (130g)", "grams": 130},
            {"description": "2 slices (260g)", "grams": 260},
        ], ["avocado toast", "avo toast"], "Cafe Breakfast", image_key="bread"),
        F("french-toast-classic", "Classic cinnamon French toast", "Breakfast", "Egg-battered bread pan-toasted with cinnamon and milk", 220, 6.5, 30.0, 8.5, 1.5, 8.5, 310, 110, "slice", [
            {"description": "1 thick slice (110g)", "grams": 110},
            {"description": "2 slices (220g)", "grams": 220},
        ], ["french toast", "eggy bread"], "Western Breakfast", image_key="bread"),
        F("buttermilk-pancakes", "Fluffy buttermilk pancakes", "Breakfast", "Griddled buttermilk pancakes with butter and syrup", 227, 6.0, 38.0, 6.0, 1.2, 12.0, 430, 80, "pancake (4 inch)", [
            {"description": "1 4-inch pancake (80g)", "grams": 80},
            {"description": "Stack of 2 (160g)", "grams": 160},
            {"description": "Stack of 3 (240g)", "grams": 240},
        ], ["pancakes", "buttermilk pancake", "hotcakes"], "Western Breakfast"),
        F("belgian-waffle", "Belgian waffle", "Breakfast", "Deep-pocketed golden waffle", 290, 7.5, 42.0, 10.5, 1.8, 14.0, 410, 100, "waffle (7 inch)", [
            {"description": "1 waffle (100g)", "grams": 100},
        ], ["waffle", "belgian waffle"], "Western Breakfast"),
        F("bagel-cream-cheese", "Bagel with cream cheese", "Breakfast", "Toasted bagel spread with 30g plain cream cheese", 285, 9.5, 42.0, 9.0, 2.0, 5.5, 460, 125, "whole bagel with spread", [
            {"description": "1 bagel with spread (125g)", "grams": 125},
        ], ["bagel cream cheese", "bagel with shmear"], "Cafe Breakfast", image_key="bread"),
        F("eggs-benedict", "Eggs Benedict with hollandaise", "Breakfast", "Poached egg on English muffin with ham and creamy hollandaise", 240, 11.0, 12.0, 16.5, 0.5, 1.5, 520, 150, "half portion (1 muffin half)", [
            {"description": "1 half (150g)", "grams": 150},
            {"description": "Full serving / 2 halves (300g)", "grams": 300},
        ], ["eggs benedict", "benedict"], "Western Breakfast", image_key="egg"),
        F("breakfast-burrito", "Breakfast burrito with eggs and cheese", "Breakfast", "Scrambled eggs, cheddar cheese, potatoes and salsa wrapped in flour tortilla", 215, 9.0, 21.0, 10.5, 1.8, 1.8, 480, 200, "burrito", [
            {"description": "1 burrito (200g)", "grams": 200},
        ], ["breakfast burrito", "egg burrito"], "Mexican"),
        F("overnight-oats-berries", "Overnight rolled oats with chia and berries", "Breakfast", "Rolled oats soaked in milk with chia seeds, maple syrup and mixed berries", 135, 4.5, 23.0, 3.0, 3.8, 7.5, 50, 200, "jar", [
            {"description": "1 jar (200g)", "grams": 200},
            {"description": "1 large portion (300g)", "grams": 300},
        ], ["overnight oats", "bircher muesli"], "Healthy Breakfast", image_key="oats"),
        F("granola-greek-yogurt-bowl", "Greek yogurt bowl with granola and fruit", "Breakfast", "Thick Greek yogurt topped with toasted granola, honey and fresh sliced banana", 145, 6.8, 20.0, 4.5, 2.0, 11.0, 65, 220, "bowl", [
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["yogurt bowl", "granola bowl", "parfait"], "Healthy Breakfast", image_key="curd"),
        F("acai-bowl", "Acai smoothie bowl with toppings", "Breakfast", "Blended frozen acai pulp topped with sliced banana, blueberries and granola", 125, 2.5, 22.0, 3.5, 3.5, 14.0, 25, 250, "bowl", [
            {"description": "1 bowl (250g)", "grams": 250},
        ], ["acai bowl", "acai", "smoothie bowl"], "Healthy Breakfast"),
        F("chia-pudding-almond-milk", "Chia seed pudding with almond milk", "Breakfast", "Chia seeds hydrated in unsweetened almond milk with vanilla and honey", 110, 3.2, 11.0, 6.0, 5.5, 4.5, 60, 160, "cup", [
            {"description": "1 cup (160g)", "grams": 160},
        ], ["chia pudding", "chia seed pudding"], "Healthy Breakfast"),
    ])

    # =========================================================================
    # MIDDLE EASTERN & MEDITERRANEAN CONDIMENTS
    # =========================================================================
    items.extend([
        F("pita-bread-whole-wheat-pocket", "Whole wheat pita bread", "Bread", "100% whole wheat baked pocket bread", 250, 10.0, 48.0, 1.8, 6.0, 1.5, 420, 64, "pita", [
            {"description": "1 pita (64g)", "grams": 64},
        ], ["whole wheat pita", "brown pita"], "Flatbreads", image_key="bread"),
        F("shawarma-chicken-wrap", "Chicken shawarma wrap with garlic sauce", "Fast Food", "Spiced rotisserie chicken, garlic toum and pickles wrapped in thin pita", 215, 12.5, 21.0, 9.2, 1.5, 1.8, 540, 220, "wrap", [
            {"description": "1 wrap (220g)", "grams": 220},
        ], ["shawarma", "chicken shawarma", "shawarma roll"], "Middle Eastern", image_key="chicken_breast"),
        F("toum-garlic-sauce", "Lebanese garlic sauce (Toum)", "Condiments", "Whipped garlic, oil, lemon juice and salt", 510, 1.8, 6.0, 55.0, 0.5, 0.5, 450, 15, "tbsp", [
            {"description": "1 tbsp (15g)", "grams": 15},
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["toum", "garlic paste", "garlic toum"], "Condiments"),
        F("tzatziki-sauce", "Greek tzatziki cucumber yogurt dip", "Condiments", "Strained yogurt with grated cucumber, garlic, dill and olive oil", 90, 4.5, 3.5, 6.5, 0.4, 2.5, 260, 30, "tbsp", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1/4 cup (60g)", "grams": 60},
        ], ["tzatziki", "cucumber yogurt sauce"], "Mediterranean", image_key="curd"),
        F("guacamole-avocado", "Fresh guacamole dip", "Condiments", "Mashed ripe avocado with diced tomatoes, onions, cilantro, jalapeño and lime", 157, 2.0, 8.5, 14.5, 5.5, 1.2, 280, 50, "serving (3 tbsp)", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1/4 cup / 3 tbsp (50g)", "grams": 50},
        ], ["guacamole", "guac", "avocado dip"], "Mexican"),
        F("salsa-fresca", "Pico de gallo fresh salsa", "Condiments", "Chopped fresh ripe tomatoes, onions, cilantro and jalapeño peppers with lime", 25, 1.1, 5.0, 0.2, 1.5, 3.0, 290, 30, "tbsp", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1/4 cup (60g)", "grams": 60},
        ], ["pico de gallo", "fresh salsa", "salsa"], "Mexican", image_key="tomato"),
    ])

    return items

print("Catalogue part 10 loaded.")
