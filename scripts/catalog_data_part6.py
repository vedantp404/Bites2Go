"""
Catalogue data part 6: Fruits, Vegetables, and Global Meats/Seafood (~210 items).
"""

from scripts.build_full_database import F

def get_part6():
    items = []

    # =========================================================================
    # MORE FRUITS (~55 items)
    # =========================================================================
    items.extend([
        F("grapefruit-pink", "Pink Grapefruit", "Fruit", "Raw fresh pink or red grapefruit sections", 42, 0.8, 10.7, 0.1, 1.6, 6.9, 0, 123, "half fruit", [
            {"description": "1/2 medium fruit (123g)", "grams": 123},
        ], ["grapefruit", "pink grapefruit"], "Citrus Fruit"),
        F("lemon-raw", "Lemon (Raw with peel/juice)", "Fruit", "Raw fresh lemon without seeds", 29, 1.1, 9.3, 0.3, 2.8, 2.5, 2, 58, "medium lemon", [
            {"description": "1 medium lemon (58g)", "grams": 58},
            {"description": "Juice of 1 lemon (30g)", "grams": 30},
        ], ["nimbu", "lemon fresh"], "Citrus Fruit"),
        F("lime-raw", "Lime (Raw fresh)", "Fruit", "Raw green lime whole", 30, 0.7, 10.5, 0.2, 2.8, 1.7, 2, 44, "medium lime", [
            {"description": "1 lime (44g)", "grams": 44},
        ], ["green lime", "kagzi nimbu"], "Citrus Fruit"),
        F("cherries-sweet", "Sweet Red Cherries", "Fruit", "Raw pitted sweet cherries", 63, 1.1, 16.0, 0.2, 2.1, 12.8, 0, 138, "cup with pits (approx 21 cherries)", [
            {"description": "1 cup with pits (138g)", "grams": 138},
            {"description": "10 cherries (80g)", "grams": 80},
        ], ["cherries", "red cherries"], "Stone Fruit"),
        F("apricots-fresh", "Fresh Apricots", "Fruit", "Raw fresh pitted apricot halves", 48, 1.4, 11.1, 0.4, 2.0, 9.2, 1, 35, "apricot", [
            {"description": "1 apricot (35g)", "grams": 35},
            {"description": "3 apricots (105g)", "grams": 105},
        ], ["khubani", "fresh apricot"], "Stone Fruit"),
        F("apricots-dried", "Dried Apricots", "Fruit", "Unsweetened dried pitted apricot halves", 241, 3.4, 62.6, 0.5, 7.3, 53.4, 10, 30, "serving (5 halves)", [
            {"description": "5 dried halves (30g)", "grams": 30},
        ], ["sukhi khubani", "dried apricot"], "Dried Fruit"),
        F("prunes-pitted", "Dried Prunes (Dried plums)", "Fruit", "Pitted dried plums", 240, 2.2, 63.9, 0.4, 7.1, 38.1, 2, 40, "serving (4 prunes)", [
            {"description": "4 prunes (40g)", "grams": 40},
        ], ["prunes", "dried plums"], "Dried Fruit"),
        F("cranberries-dried", "Dried Cranberries (Sweetened)", "Fruit", "Dehydrated tart cranberries lightly sweetened", 308, 0.2, 82.8, 1.1, 5.3, 72.6, 5, 40, "1/4 cup", [
            {"description": "1/4 cup (40g)", "grams": 40},
        ], ["craisins", "dried cranberries"], "Dried Fruit"),
        F("amla-gooseberry", "Indian Gooseberry (Amla)", "Fruit", "Raw, fresh whole Indian gooseberry", 44, 0.9, 10.2, 0.6, 4.3, 0, 1, 30, "amla fruit", [
            {"description": "1 amla (30g)", "grams": 30},
            {"description": "2 amlas (60g)", "grams": 60},
        ], ["amla", "awala", "indian gooseberry", "nellikai"], "Traditional Fruit"),
        F("jamun-black-plum", "Black Plum (Jamun)", "Fruit", "Raw fresh purple black plum flesh", 60, 0.7, 14.0, 0.2, 0.9, 12.0, 14, 100, "cup", [
            {"description": "1 cup fruit (135g)", "grams": 135},
        ], ["jamun", "jambhul", "black plum", "java plum"], "Tropical Fruit"),
        F("ber-jujube", "Indian Jujube (Ber / Bor)", "Fruit", "Raw fresh small Indian round fruit", 79, 1.2, 20.2, 0.2, 3.0, 10.5, 3, 50, "serving (5 bers)", [
            {"description": "5 fruits (50g)", "grams": 50},
        ], ["ber", "bor", "indian jujube"], "Traditional Fruit"),
        F("cantaloupe-melon", "Honeydew Melon", "Fruit", "Raw, peeled pale green melon cubes", 36, 0.5, 9.1, 0.1, 0.8, 8.1, 18, 160, "cup cubes", [
            {"description": "1 cup cubes (160g)", "grams": 160},
        ], ["honeydew", "green melon"], "Melons"),
        F("passion-fruit", "Passion Fruit (Purple)", "Fruit", "Raw purple passion fruit pulp with seeds", 97, 2.2, 23.4, 0.7, 10.4, 11.2, 28, 18, "fruit", [
            {"description": "1 passion fruit pulp (18g)", "grams": 18},
        ], ["passion fruit"], "Exotic Fruit"),
        F("dragon-fruit", "Dragon Fruit (Pitaya)", "Fruit", "Raw white or red flesh with tiny black seeds", 60, 1.2, 13.0, 0.5, 2.9, 8.0, 0, 150, "cup cubes", [
            {"description": "1 cup cubes (150g)", "grams": 150},
        ], ["pitaya", "dragonfruit"], "Exotic Fruit"),
        F("lychee-fresh", "Fresh Lychee", "Fruit", "Raw, peeled translucent white fruit without stone", 66, 0.8, 16.5, 0.4, 1.3, 15.2, 1, 10, "fruit", [
            {"description": "1 lychee (10g)", "grams": 10},
            {"description": "10 lychees (100g)", "grams": 100},
        ], ["litchi", "fresh lychee"], "Tropical Fruit"),
        F("plantain-raw", "Green Cooking Plantain (Raw)", "Fruit", "Raw peeled unripe green cooking banana", 122, 1.3, 31.9, 0.4, 2.3, 15.0, 4, 150, "medium plantain", [
            {"description": "1 medium plantain (150g)", "grams": 150},
        ], ["raw banana", "kaccha kela", "cooking plantain"], "Cooking Bananas"),
        F("plantain-boiled", "Boiled Green Plantain", "Fruit", "Boiled green banana slices drained", 116, 0.8, 31.2, 0.2, 2.3, 14.5, 3, 140, "cup slices", None, ["boiled raw banana"], "Cooking Bananas"),
    ])

    # =========================================================================
    # MORE VEGETABLES & GREENS (~85 items)
    # =========================================================================
    items.extend([
        F("asparagus-cooked", "Cooked Asparagus", "Vegetables", "Boiled or steamed green asparagus spears drained", 22, 2.4, 4.1, 0.2, 2.0, 1.3, 14, 90, "serving (4 spears)", [
            {"description": "4 spears (90g)", "grams": 90},
            {"description": "1 cup cut (180g)", "grams": 180},
        ], ["asparagus spears"], "Stalk Vegetables"),
        F("artichoke-boiled", "Boiled Globe Artichoke", "Vegetables", "Boiled whole globe artichoke drained", 53, 2.9, 12.0, 0.3, 8.6, 1.0, 86, 120, "medium artichoke", [
            {"description": "1 medium artichoke (120g)", "grams": 120},
        ], ["globe artichoke"], "Flower Vegetables"),
        F("brussels-sprouts-cooked", "Cooked Brussels Sprouts", "Vegetables", "Boiled or roasted miniature cabbage heads", 43, 3.4, 9.0, 0.5, 4.1, 2.2, 25, 156, "cup", [
            {"description": "1 cup (156g)", "grams": 156},
        ], ["brussels sprouts"], "Cruciferous"),
        F("celery-stalk-raw", "Raw Celery Stalks", "Vegetables", "Raw fresh crisp green celery ribs", 16, 0.7, 3.0, 0.2, 1.6, 1.3, 80, 40, "medium stalk", [
            {"description": "1 medium stalk (40g)", "grams": 40},
            {"description": "1 cup chopped (100g)", "grams": 100},
        ], ["celery ribs"], "Stalk Vegetables"),
        F("bok-choy-cooked", "Cooked Bok Choy (Pak choi)", "Vegetables", "Boiled Chinese white cabbage leaves and stalks", 12, 1.6, 1.8, 0.2, 1.0, 0.8, 34, 170, "cup shredded", [
            {"description": "1 cup cooked (170g)", "grams": 170},
        ], ["pak choi", "chinese cabbage"], "Leafy Greens"),
        F("kale-cooked", "Cooked Kale (Boiled)", "Vegetables", "Boiled dark leafy kale drained without oil", 28, 1.9, 5.6, 0.4, 2.0, 0.8, 23, 130, "cup cooked", [
            {"description": "1 cup cooked (130g)", "grams": 130},
        ], ["boiled kale"], "Leafy Greens"),
        F("kale-raw", "Raw Kale leaves", "Vegetables", "Raw chopped Tuscan / curly kale leaves", 35, 2.9, 4.4, 1.5, 4.1, 0.8, 53, 67, "cup chopped", [
            {"description": "1 cup packed (67g)", "grams": 67},
        ], ["kale raw"], "Leafy Greens"),
        F("arugula-raw", "Raw Arugula (Rocket leaves)", "Vegetables", "Raw peppery rocket salad leaves", 25, 2.6, 3.7, 0.7, 1.6, 2.1, 27, 20, "cup", [
            {"description": "1 cup (20g)", "grams": 20},
            {"description": "Bowl (100g)", "grams": 100},
        ], ["rocket leaves", "roquette"], "Salad Vegetables"),
        F("radish-white-mooli", "White Radish (Daikon / Mooli)", "Vegetables", "Raw, peeled crisp white daikon radish root", 18, 0.6, 4.1, 0.1, 1.6, 2.5, 21, 100, "medium root", [
            {"description": "1 medium mooli (150g)", "grams": 150},
            {"description": "1/2 cup sliced (60g)", "grams": 60},
        ], ["mooli", "daikon", "white radish"], "Root Vegetables"),
        F("radish-red-raw", "Red Radish (Globe)", "Vegetables", "Raw crisp round red radishes sliced", 16, 0.7, 3.4, 0.1, 1.6, 1.9, 39, 10, "radish", [
            {"description": "1 small radish (10g)", "grams": 10},
            {"description": "1/2 cup sliced (58g)", "grams": 58},
        ], ["red radish"], "Root Vegetables"),
        F("turnip-cooked", "Cooked Turnip (Shalgam)", "Vegetables", "Boiled white turnip cubes", 22, 0.7, 5.1, 0.1, 2.0, 3.0, 16, 150, "cup cubes", [
            {"description": "1 cup cubes (150g)", "grams": 150},
        ], ["shalgam", "turnip boiled"], "Root Vegetables"),
        F("suran-yam-cooked", "Elephant Foot Yam (Suran / Jimikand)", "Vegetables", "Boiled elephant yam cubes", 118, 1.5, 27.5, 0.1, 4.1, 0.5, 14, 150, "cup cubes", [
            {"description": "1 cup cooked (150g)", "grams": 150},
        ], ["suran", "jimikand", "yam cooked", "ool"], "Tubers"),
        F("arbi-colocasia-raw", "Colocasia Root (Arbi raw)", "Vegetables", "Raw peeled taro root", 112, 1.5, 26.5, 0.2, 4.1, 0.5, 11, 100, "serving", None, ["arbi", "taro root", "ghuiya"], "Tubers"),
        F("ash-gourd-raw", "Ash Gourd (Petha / Winter melon)", "Vegetables", "Raw peeled white ash gourd flesh", 13, 0.4, 3.0, 0.2, 1.2, 1.8, 11, 100, "cup cubes", [
            {"description": "1 cup cubes (120g)", "grams": 120},
        ], ["safed petha", "winter melon", "kushmanda"], "Gourds"),
        F("snake-gourd-raw", "Snake Gourd (Padwal raw)", "Vegetables", "Raw trimmed snake gourd", 18, 0.6, 3.4, 0.3, 1.5, 1.5, 15, 100, "serving", None, ["padwal", "chichinda"], "Gourds"),
        F("bitter-gourd-raw", "Bitter Gourd (Karela raw)", "Vegetables", "Raw washed green bitter gourd with ridges", 17, 1.0, 3.7, 0.2, 2.8, 0.6, 5, 100, "medium karela", [
            {"description": "1 medium karela (120g)", "grams": 120},
        ], ["karela", "bitter melon"], "Gourds"),
        F("drumstick-pods-raw", "Drumstick pods (Moringa / Shevga)", "Vegetables", "Raw fresh tender green drumsticks cut into pieces", 37, 2.1, 8.5, 0.2, 3.2, 1.4, 9, 100, "serving (4 pieces)", [
            {"description": "4 drumstick pieces (100g)", "grams": 100},
        ], ["shevga sheng", "moringa pods", "sahjan"], "Pods"),
        F("moringa-leaves-raw", "Drumstick leaves (Moringa leaves)", "Vegetables", "Raw tender green moringa leaves stripped from stems", 64, 9.4, 8.3, 1.4, 2.0, 0.8, 9, 50, "cup leaves", [
            {"description": "1 cup packed (50g)", "grams": 50},
        ], ["moringa leaves", "shevga pala", "sahjan ke patte"], "Leafy Greens"),
        F("methi-leaves-raw", "Fresh Fenugreek leaves (Methi)", "Vegetables", "Raw tender green fenugreek leaves", 49, 4.4, 6.0, 0.9, 3.5, 0.5, 67, 50, "cup leaves", [
            {"description": "1 cup packed (50g)", "grams": 50},
        ], ["methi patta", "fresh methi leaves"], "Leafy Greens"),
        F("mustard-greens-raw", "Mustard greens (Sarson leaves)", "Vegetables", "Raw fresh spicy mustard green leaves", 27, 2.9, 4.7, 0.4, 3.2, 1.3, 20, 56, "cup chopped", [
            {"description": "1 cup chopped (56g)", "grams": 56},
        ], ["sarson ke patte", "mustard leaves"], "Leafy Greens"),
        F("amaranth-leaves-raw", "Red Amaranth leaves (Lal Math)", "Vegetables", "Raw fresh red/green amaranth greens", 23, 2.5, 4.0, 0.3, 2.1, 0.5, 20, 50, "cup leaves", [
            {"description": "1 cup leaves (50g)", "grams": 50},
        ], ["lal math", "chaulai saag", "red amaranth"], "Leafy Greens"),
        F("coriander-fresh", "Fresh Coriander leaves (Cilantro)", "Vegetables", "Fresh chopped green coriander sprigs", 23, 2.1, 3.7, 0.5, 2.8, 0.9, 46, 20, "cup chopped", [
            {"description": "1/4 cup chopped (16g)", "grams": 16},
            {"description": "1 bunch (60g)", "grams": 60},
        ], ["kothimbir", "hara dhaniya", "cilantro"], "Herbs"),
        F("mint-leaves-fresh", "Fresh Mint leaves (Pudina)", "Vegetables", "Fresh green spearmint leaves", 44, 3.3, 8.4, 0.7, 6.8, 0.5, 31, 15, "handful", [
            {"description": "1 handful (15g)", "grams": 15},
        ], ["pudina", "fresh mint"], "Herbs"),
        F("curry-leaves-fresh", "Fresh Curry leaves (Kadi Patta)", "Vegetables", "Fresh aromatic neem leaves for Indian tadka", 108, 6.1, 18.7, 1.0, 6.4, 0, 16, 5, "sprig (10 leaves)", [
            {"description": "1 sprig (5g)", "grams": 5},
        ], ["kadi patta", "karivepaku", "sweet neem"], "Herbs"),
        F("green-chili-raw", "Green Chili (Raw hot pepper)", "Vegetables", "Fresh hot green Indian chili", 40, 2.0, 8.8, 0.2, 1.5, 5.3, 7, 10, "chili", [
            {"description": "1 chili (10g)", "grams": 10},
            {"description": "3 chilies (30g)", "grams": 30},
        ], ["hari mirch", "green chillies"], "Hot Peppers"),
        F("spring-onions-raw", "Spring Onions (Scallions)", "Vegetables", "Raw green onions with white bulb and green tops", 32, 1.8, 7.3, 0.2, 2.6, 2.3, 16, 50, "bunch portion", [
            {"description": "1/2 cup chopped (50g)", "grams": 50},
        ], ["scallions", "green onions", "kandachi paat"], "Alliums"),
        F("leeks-cooked", "Cooked Leeks", "Vegetables", "Boiled leeks drained without butter", 31, 0.8, 7.6, 0.2, 1.0, 1.9, 10, 100, "cup slices", None, ["leeks boiled"], "Alliums"),
        F("shallots-raw", "Raw Shallots (Sambar onions)", "Vegetables", "Peeled small shallots / pearl onions", 72, 2.5, 16.8, 0.1, 3.2, 8.0, 12, 50, "handful (5 shallots)", [
            {"description": "5 shallots (50g)", "grams": 50},
        ], ["sambar onions", "madras onions", "choti pyaz"], "Alliums"),
    ])

    # =========================================================================
    # MORE POULTRY, MEATS & SEAFOOD (~70 items)
    # =========================================================================
    items.extend([
        F("beef-ribeye-steak", "Beef Ribeye Steak (Trimmed, grilled)", "Meat", "Choice grade ribeye steak grilled without bone", 254, 24.3, 0.0, 16.7, 0, 0, 56, 170, "steak", [
            {"description": "1 standard steak (170g)", "grams": 170},
        ], ["ribeye steak", "grilled ribeye"], "Beef"),
        F("beef-sirloin-steak", "Beef Sirloin Steak (Lean, grilled)", "Meat", "Top sirloin steak broiled lean", 183, 30.2, 0.0, 6.0, 0, 0, 55, 150, "steak", [
            {"description": "1 steak (150g)", "grams": 150},
        ], ["sirloin steak", "top sirloin"], "Beef"),
        F("pork-chop-grilled", "Pork Chop (Center loin, grilled)", "Meat", "Bone-in pork chop pan-seared lean", 204, 27.5, 0.0, 9.7, 0, 0, 62, 140, "chop", [
            {"description": "1 chop (140g)", "grams": 140},
        ], ["pork loin chop"], "Pork"),
        F("pork-tenderloin-roast", "Pork Tenderloin (Roasted lean)", "Meat", "Whole pork tenderloin roasted without fat", 143, 26.2, 0.0, 3.5, 0, 0, 53, 100, "serving", [
            {"description": "3 slices (85g)", "grams": 85},
        ], ["lean pork tenderloin"], "Pork"),
        F("bacon-pork-cooked", "Cured Pork Bacon (Crisp strip)", "Meat", "Pan-fried crispy cured pork bacon strip drained", 541, 37.0, 1.4, 41.8, 0, 0, 1717, 16, "2 cooked slices", [
            {"description": "1 slice (8g)", "grams": 8},
            {"description": "2 slices (16g)", "grams": 16},
            {"description": "3 slices (24g)", "grams": 24},
        ], ["bacon strips", "crispy bacon"], "Cured Meats"),
        F("turkey-bacon", "Turkey Bacon (Cooked)", "Meat", "Pan-browned turkey bacon slices", 382, 30.0, 2.5, 28.0, 0, 1.0, 1950, 16, "2 slices", None, ["smoked turkey bacon"], "Cured Meats"),
        F("lamb-chop-grilled", "Lamb Loin Chop (Broiled)", "Meat", "Grilled domestic lamb chop lean and fat eaten", 245, 24.5, 0.0, 15.5, 0, 0, 72, 100, "chop", [
            {"description": "1 chop (100g)", "grams": 100},
        ], ["grilled lamb chop"], "Lamb"),
        F("cod-fillet-baked", "Baked Atlantic Cod", "Meat", "Atlantic cod fillet baked with lemon juice", 105, 22.8, 0.0, 0.9, 0, 0, 86, 130, "fillet", [
            {"description": "1 fillet (130g)", "grams": 130},
        ], ["cod fillet", "baked white fish"], "Seafood"),
        F("tilapia-fillet-cooked", "Cooked Tilapia Fillet", "Meat", "Tilapia baked with light seasoning", 128, 26.2, 0.0, 2.7, 0, 0, 56, 116, "fillet", [
            {"description": "1 fillet (116g)", "grams": 116},
        ], ["tilapia fillet"], "Seafood"),
        F("crab-meat-cooked", "Steamed Blue Crab Meat", "Meat", "Cooked lump crab meat", 97, 20.2, 0.0, 1.3, 0, 0, 395, 85, "serving", [
            {"description": "1 cup lump meat (135g)", "grams": 135},
        ], ["lump crab", "steamed crab"], "Seafood"),
        F("lobster-tail-steamed", "Steamed Lobster Tail", "Meat", "Cooked north atlantic lobster tail meat without butter", 98, 20.5, 1.3, 0.9, 0, 0, 480, 120, "tail", [
            {"description": "1 tail (120g)", "grams": 120},
        ], ["lobster tail"], "Seafood"),
        F("calamari-squid-grilled", "Grilled Calamari (Squid)", "Meat", "Fresh squid rings grilled with olive oil and parsley", 92, 15.6, 3.1, 1.4, 0, 0, 44, 100, "serving", [
            {"description": "1 serving (100g)", "grams": 100},
        ], ["grilled squid", "squid rings"], "Seafood"),
        F("calamari-fried", "Fried Calamari (Breaded)", "Meat", "Battered and deep-fried squid rings with dipping sauce", 240, 14.5, 19.0, 12.0, 0.8, 0.5, 410, 110, "serving", [
            {"description": "1 serving (110g)", "grams": 110},
        ], ["fried squid"], "Seafood"),
        F("roast-chicken-whole", "Roast Chicken (Meat and skin)", "Meat", "Oven-roasted whole chicken carved", 223, 24.0, 0.0, 13.4, 0, 0, 82, 140, "serving", [
            {"description": "1 leg and thigh (140g)", "grams": 140},
            {"description": "Half breast with skin (120g)", "grams": 120},
        ], ["rotisserie chicken", "roasted chicken"], "Poultry"),
        F("chicken-wings-baked", "Baked Chicken Wings (Bone-in)", "Meat", "Oven-baked crispy chicken wing sections without sauce", 216, 21.5, 0.0, 14.2, 0, 0, 82, 70, "serving (2 wings)", [
            {"description": "2 wings with bone (70g)", "grams": 70},
            {"description": "4 wings with bone (140g)", "grams": 140},
        ], ["baked buffalo wings"], "Poultry"),
    ])

    return items

print("Catalogue part 6 loaded.")
