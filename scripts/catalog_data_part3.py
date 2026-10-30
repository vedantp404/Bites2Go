"""
Catalogue data part 3: Fruits, Vegetables, International Breads/Pasta, Fast Food/Restaurant (Groups 9-12).
"""

from scripts.build_full_database import F

def get_part3():
    items = []

    # =========================================================================
    # GROUP 9: FRUITS (~65 items)
    # =========================================================================
    items.extend([
        F("orange-fresh", "Orange (Fresh)", "Fruit", "Raw, peeled segments", 47, 0.9, 11.8, 0.1, 2.4, 9.4, 0, 131, "medium orange", [
            {"description": "1 small orange (96g)", "grams": 96},
            {"description": "1 medium orange (131g)", "grams": 131},
            {"description": "1 large orange (184g)", "grams": 184},
        ], ["orange", "santra", "fresh orange"], "Citrus Fruit", image_key="orange"),
        F("mango-alphonso", "Alphonso Mango", "Fruit", "Raw, fresh sliced pulp", 65, 0.8, 17.0, 0.3, 1.8, 14.5, 1, 150, "sliced cup", [
            {"description": "1 medium mango without stone (150g)", "grams": 150},
            {"description": "1 cup diced (165g)", "grams": 165},
        ], ["mango", "aam", "hapus mango"], "Tropical Fruit", image_key="mango"),
        F("mango-generic", "Ripe Mango (Pulp)", "Fruit", "Raw edible portion", 60, 0.8, 15.0, 0.4, 1.6, 13.7, 1, 150, "mango portion", None, ["mango slice", "ripe mango"], "Tropical Fruit", image_key="mango"),
        F("papaya-ripe", "Ripe Papaya", "Fruit", "Raw, peeled and deseeded cubes", 43, 0.5, 11.0, 0.3, 1.7, 7.8, 8, 150, "cup cubes", [
            {"description": "1 cup cubes (145g)", "grams": 145},
            {"description": "1 small wedge (100g)", "grams": 100},
        ], ["papaya", "papita"], "Tropical Fruit"),
        F("watermelon-fresh", "Watermelon", "Fruit", "Raw, fresh red flesh diced", 30, 0.6, 7.6, 0.2, 0.4, 6.2, 1, 154, "wedge / cup", [
            {"description": "1 cup diced (152g)", "grams": 152},
            {"description": "1 large wedge (280g)", "grams": 280},
        ], ["watermelon", "tarbooz", "fresh watermelon"], "Melons", image_key="watermelon"),
        F("muskmelon", "Muskmelon (Cantaloupe)", "Fruit", "Raw, peeled cubes", 34, 0.8, 8.2, 0.2, 0.9, 7.9, 16, 160, "cup cubes", [
            {"description": "1 cup cubes (160g)", "grams": 160},
        ], ["cantaloupe", "kharbuja"], "Melons"),
        F("guava-fresh", "Guava (Amrood)", "Fruit", "Raw, whole edible portion", 68, 2.6, 14.3, 1.0, 5.4, 8.9, 2, 100, "medium guava", [
            {"description": "1 medium guava (100g)", "grams": 100},
            {"description": "1 large guava (150g)", "grams": 150},
        ], ["amrood", "peru", "fresh guava"], "Tropical Fruit"),
        F("pomegranate-fresh", "Pomegranate arils (Anar)", "Fruit", "Raw fresh edible seeds", 83, 1.7, 18.7, 1.2, 4.0, 13.7, 3, 87, "half cup", [
            {"description": "1/2 cup arils (87g)", "grams": 87},
            {"description": "1 whole pomegranate seeds (174g)", "grams": 174},
        ], ["anar", "dalimb", "pomegranate seeds"], "Berries & Arils"),
        F("grapes-green", "Green Seedless Grapes", "Fruit", "Raw, whole fresh grapes", 69, 0.7, 18.1, 0.2, 0.9, 15.5, 2, 150, "cup (approx 30 grapes)", [
            {"description": "1 cup (150g)", "grams": 150},
            {"description": "10 grapes (50g)", "grams": 50},
        ], ["grapes", "angoor", "green grapes"], "Berries", image_key="grapes"),
        F("grapes-black", "Black / Red Grapes", "Fruit", "Raw, whole fresh grapes", 67, 0.6, 17.5, 0.3, 0.9, 16.0, 2, 150, "cup", None, ["black grapes", "kala angoor"], "Berries", image_key="grapes"),
        F("strawberries-fresh", "Strawberries", "Fruit", "Raw, whole fresh berries capped", 32, 0.7, 7.7, 0.3, 2.0, 4.9, 1, 144, "cup halves", [
            {"description": "1 cup whole (144g)", "grams": 144},
            {"description": "5 large strawberries (90g)", "grams": 90},
        ], ["strawberries", "fresh strawberries"], "Berries", image_key="strawberry"),
        F("blueberries-fresh", "Blueberries", "Fruit", "Raw, fresh berries", 57, 0.7, 14.5, 0.3, 2.4, 9.9, 1, 148, "cup", [
            {"description": "1 cup (148g)", "grams": 148},
            {"description": "1/2 cup (74g)", "grams": 74},
        ], ["blueberries", "fresh blueberries"], "Berries"),
        F("raspberries-fresh", "Raspberries", "Fruit", "Raw, fresh berries", 52, 1.2, 11.9, 0.7, 6.5, 4.4, 1, 123, "cup", None, ["fresh raspberries"], "Berries"),
        F("blackberries-fresh", "Blackberries", "Fruit", "Raw, fresh berries", 43, 1.4, 9.6, 0.5, 5.3, 4.9, 1, 144, "cup", None, ["fresh blackberries"], "Berries"),
        F("kiwi-fruit", "Kiwi fruit (Green)", "Fruit", "Raw, peeled slices", 61, 1.1, 14.7, 0.5, 3.0, 9.0, 3, 69, "medium kiwi", [
            {"description": "1 medium kiwi (69g)", "grams": 69},
        ], ["kiwifruit", "chinese gooseberry"], "Exotic Fruit"),
        F("pineapple-fresh", "Pineapple (Fresh)", "Fruit", "Raw, peeled cored chunks", 50, 0.5, 13.1, 0.1, 1.4, 9.9, 1, 165, "cup chunks", [
            {"description": "1 cup chunks (165g)", "grams": 165},
            {"description": "1 slice (84g)", "grams": 84},
        ], ["pineapple", "ananas"], "Tropical Fruit"),
        F("pear-fresh", "Pear (Fresh)", "Fruit", "Raw, with skin", 57, 0.4, 15.2, 0.1, 3.1, 9.8, 1, 166, "medium pear", [
            {"description": "1 medium pear (166g)", "grams": 166},
        ], ["nashpati", "fresh pear"], "Pome Fruit"),
        F("peach-fresh", "Peach (Fresh)", "Fruit", "Raw, edible flesh with skin", 39, 0.9, 9.5, 0.3, 1.5, 8.4, 0, 150, "medium peach", None, ["fresh peach", "aadu"], "Stone Fruit"),
        F("plum-fresh", "Plum (Fresh)", "Fruit", "Raw, whole fruit with skin", 46, 0.7, 11.4, 0.3, 1.4, 9.9, 0, 66, "medium plum", None, ["fresh plum", "aloo bukhara"], "Stone Fruit"),
        F("chikoo-sapodilla", "Chikoo (Sapodilla)", "Fruit", "Raw, peeled sweet brown fruit", 83, 0.4, 20.0, 1.1, 5.3, 14.0, 12, 100, "medium chikoo", [
            {"description": "1 medium chikoo (100g)", "grams": 100},
            {"description": "2 chikoos (200g)", "grams": 200},
        ], ["sapodilla", "chiku", "sapota"], "Tropical Fruit"),
        F("custard-apple", "Custard Apple (Sitaphal)", "Fruit", "Raw fresh edible sweet pulp", 94, 2.1, 23.6, 0.3, 4.4, 16.0, 9, 100, "pulp portion", [
            {"description": "1 cup pulp (120g)", "grams": 120},
        ], ["sitaphal", "sharifa", "sugar apple"], "Tropical Fruit"),
        F("sweet-lime-mosambi", "Sweet Lime (Mosambi)", "Fruit", "Raw fresh peeled segments", 43, 0.7, 10.5, 0.1, 1.2, 8.2, 2, 120, "fruit", [
            {"description": "1 mosambi (120g)", "grams": 120},
        ], ["mosambi", "mousambi", "sweet lemon"], "Citrus Fruit"),
        F("dates-medjool", "Medjool Dates", "Fruit", "Dried, pitted sweet date fruit", 277, 1.8, 75.0, 0.2, 6.7, 66.5, 1, 24, "date", [
            {"description": "1 medjool date (24g)", "grams": 24},
            {"description": "3 dates (72g)", "grams": 72},
        ], ["khajoor", "dates dried"], "Dried Fruit"),
        F("raisins-kishmish", "Raisins (Kishmish)", "Fruit", "Dried seedless grapes", 299, 3.1, 79.2, 0.5, 3.7, 59.2, 11, 40, "small box", [
            {"description": "1 tbsp (14g)", "grams": 14},
            {"description": "1 small box (40g)", "grams": 40},
        ], ["kishmish", "sultanas", "dried grapes"], "Dried Fruit"),
        F("avocado-raw", "Avocado", "Fruit", "Raw, peeled Haas avocado flesh", 160, 2.0, 8.5, 14.7, 6.7, 0.7, 7, 100, "half avocado", [
            {"description": "1/2 avocado (100g)", "grams": 100},
            {"description": "1 whole medium avocado (150g)", "grams": 150},
        ], ["haas avocado", "butter fruit", "makhan phal"], "Tropical Fruit"),
        F("fig-fresh", "Fresh Figs (Anjeer)", "Fruit", "Raw fresh whole edible figs", 74, 0.8, 19.2, 0.3, 2.9, 16.3, 1, 50, "medium fig", [
            {"description": "1 medium fresh fig (50g)", "grams": 50},
        ], ["anjeer fresh", "fresh fig"], "Tropical Fruit"),
        F("fig-dried", "Dried Figs (Anjeer)", "Fruit", "Dried whole flattened figs", 249, 3.3, 63.9, 0.9, 9.8, 47.9, 10, 20, "piece", [
            {"description": "1 dried fig (20g)", "grams": 20},
            {"description": "3 dried figs (60g)", "grams": 60},
        ], ["sukha anjeer", "dried fig"], "Dried Fruit"),
    ])

    # =========================================================================
    # GROUP 10: VEGETABLES (~75 items)
    # =========================================================================
    items.extend([
        F("potato-boiled", "Boiled Potato (Skinless)", "Vegetables", "Boiled in water without salt or butter", 87, 1.9, 20.1, 0.1, 1.8, 0.9, 6, 150, "medium potato", [
            {"description": "1 medium boiled potato (150g)", "grams": 150},
            {"description": "1 small potato (100g)", "grams": 100},
        ], ["aloo ubla hua", "boiled potato", "alu boiled"], "Root Vegetables", image_key="potato"),
        F("potato-raw", "Raw Potato", "Vegetables", "Raw peeled potato tuber", 77, 2.0, 17.5, 0.1, 2.2, 0.8, 6, 150, "medium potato", None, ["raw potato", "kaccha aloo"], "Root Vegetables", image_key="potato"),
        F("sweet-potato-boiled", "Boiled Sweet Potato", "Vegetables", "Boiled orange-flesh sweet potato without skin", 76, 1.4, 17.7, 0.1, 2.5, 5.7, 27, 130, "medium sweet potato", [
            {"description": "1 medium sweet potato (130g)", "grams": 130},
        ], ["shakarkandi", "ratalu boiled", "sweet potato"], "Root Vegetables"),
        F("sweet-potato-raw", "Raw Sweet Potato", "Vegetables", "Raw unpeeled sweet potato", 86, 1.6, 20.1, 0.1, 3.0, 4.2, 55, 130, "sweet potato", None, ["raw shakarkand", "ratalu"], "Root Vegetables"),
        F("tomato-raw", "Tomato (Raw)", "Vegetables", "Raw ripe whole tomato", 18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, 123, "medium tomato", [
            {"description": "1 medium tomato (123g)", "grams": 123},
            {"description": "1 cup cherry tomatoes (149g)", "grams": 149},
        ], ["tamatar", "tomato", "fresh tomato"], "Fruiting Vegetables", image_key="tomato"),
        F("onion-raw", "Onion (Raw)", "Vegetables", "Raw, chopped red or yellow onion", 40, 1.1, 9.3, 0.1, 1.7, 4.2, 4, 100, "medium onion", [
            {"description": "1 medium onion (110g)", "grams": 110},
            {"description": "1/2 cup chopped (80g)", "grams": 80},
        ], ["pyaz", "kanda", "raw onion"], "Bulb Vegetables"),
        F("onion-sauteed", "Sautéed Onions", "Vegetables", "Sliced onions cooked in 1 tsp vegetable oil", 75, 1.2, 10.5, 3.5, 1.8, 5.0, 12, 80, "serving", None, ["cooked onions", "bhuna pyaz"], "Bulb Vegetables"),
        F("cucumber-raw", "Cucumber (Raw with peel)", "Vegetables", "Raw, sliced crisp green cucumber", 15, 0.7, 3.6, 0.1, 0.5, 1.7, 2, 100, "medium cucumber", [
            {"description": "1 medium cucumber (150g)", "grams": 150},
            {"description": "1 cup sliced (104g)", "grams": 104},
        ], ["kheera", "kakdi", "cucumber slice"], "Salad Vegetables"),
        F("carrot-raw", "Carrot (Raw)", "Vegetables", "Raw, peeled whole orange carrot", 41, 0.9, 9.6, 0.2, 2.8, 4.7, 69, 61, "medium carrot", [
            {"description": "1 medium carrot (61g)", "grams": 61},
            {"description": "1 cup chopped (128g)", "grams": 128},
        ], ["gajar", "carrot raw", "fresh carrot"], "Root Vegetables", image_key="carrot"),
        F("carrot-boiled", "Boiled Carrots", "Vegetables", "Boiled, sliced carrots without butter", 35, 0.8, 8.2, 0.2, 3.0, 3.5, 58, 100, "serving", None, ["cooked carrots"], "Root Vegetables", image_key="carrot"),
        F("spinach-raw", "Spinach (Raw leaves)", "Vegetables", "Fresh crisp raw baby or flat-leaf spinach", 23, 2.9, 3.6, 0.4, 2.2, 0.4, 79, 30, "cup leaves", [
            {"description": "1 cup packed raw (30g)", "grams": 30},
            {"description": "1 bunch leaves (250g)", "grams": 250},
        ], ["palak", "raw spinach"], "Leafy Greens", image_key="spinach"),
        F("spinach-cooked", "Boiled Spinach (Cooked)", "Vegetables", "Boiled and drained spinach leaves", 23, 3.0, 3.8, 0.3, 2.4, 0.4, 70, 180, "cup cooked", [
            {"description": "1 cup cooked (180g)", "grams": 180},
        ], ["cooked palak", "steamed spinach"], "Leafy Greens", image_key="spinach"),
        F("broccoli-steamed", "Steamed Broccoli florets", "Vegetables", "Steamed crisp-tender broccoli without butter", 35, 2.4, 7.2, 0.4, 3.3, 1.4, 41, 91, "cup florets", [
            {"description": "1 cup chopped florets (91g)", "grams": 91},
            {"description": "1 stalk (150g)", "grams": 150},
        ], ["broccoli", "steamed broccoli"], "Cruciferous", image_key="broccoli"),
        F("cauliflower-boiled", "Boiled Cauliflower", "Vegetables", "Boiled cauliflower florets drained", 23, 1.8, 4.1, 0.5, 2.3, 2.1, 15, 100, "cup florets", [
            {"description": "1 cup florets (107g)", "grams": 107},
        ], ["phool gobi", "boiled gobi"], "Cruciferous"),
        F("capsicum-green", "Green Bell Pepper (Capsicum)", "Vegetables", "Raw, sliced green bell pepper", 20, 0.9, 4.6, 0.2, 1.7, 2.4, 3, 119, "medium pepper", [
            {"description": "1 medium pepper (119g)", "grams": 119},
            {"description": "1 cup chopped (149g)", "grams": 149},
        ], ["shimla mirch", "green capsicum"], "Fruiting Vegetables"),
        F("capsicum-red", "Red Bell Pepper", "Vegetables", "Raw, sweet red bell pepper slices", 31, 1.0, 6.0, 0.3, 2.1, 4.2, 4, 119, "medium pepper", None, ["red capsicum", "sweet red pepper"], "Fruiting Vegetables"),
        F("mushrooms-button-raw", "White Button Mushrooms (Raw)", "Vegetables", "Raw, cleaned sliced white button mushrooms", 22, 3.1, 3.3, 0.3, 1.0, 2.0, 5, 70, "cup sliced", [
            {"description": "1 cup sliced (70g)", "grams": 70},
            {"description": "1 whole medium mushroom (18g)", "grams": 18},
        ], ["button mushrooms", "khumb"], "Fungi"),
        F("mushrooms-sauteed", "Sautéed Mushrooms", "Vegetables", "Button mushrooms sautéed with light oil and garlic", 55, 3.0, 4.5, 3.2, 1.2, 1.8, 160, 100, "serving", None, ["cooked mushrooms"], "Fungi"),
        F("lettuce-iceberg", "Iceberg Lettuce", "Vegetables", "Raw, crisp iceberg salad leaves shredded", 14, 0.9, 3.0, 0.1, 1.2, 2.0, 10, 72, "cup shredded", [
            {"description": "1 cup shredded (72g)", "grams": 72},
        ], ["salad leaves", "iceberg"], "Salad Vegetables"),
        F("green-peas-boiled", "Green Peas (Boiled)", "Vegetables", "Cooked green peas drained without butter", 84, 5.4, 15.6, 0.2, 5.5, 5.9, 3, 160, "cup", [
            {"description": "1 cup peas (160g)", "grams": 160},
            {"description": "1/2 cup (80g)", "grams": 80},
        ], ["matar", "green matar boiled"], "Legumes / Vegetables"),
        F("french-beans-boiled", "French Beans (Steamed)", "Vegetables", "Snap green beans trimmed, steamed plain", 35, 1.9, 7.9, 0.3, 3.2, 1.6, 6, 125, "cup", [
            {"description": "1 cup cut beans (125g)", "grams": 125},
        ], ["green beans", "french beans", "fansi"], "Pod Vegetables"),
        F("beetroot-boiled", "Boiled Beetroot", "Vegetables", "Boiled red beet sliced", 44, 1.7, 10.0, 0.2, 2.0, 8.0, 77, 100, "medium beet", [
            {"description": "1 medium beet (100g)", "grams": 100},
        ], ["chukandar", "boiled beet"], "Root Vegetables"),
        F("beetroot-raw", "Raw Beetroot (Grated)", "Vegetables", "Raw unpeeled red beet", 43, 1.6, 9.6, 0.2, 2.8, 6.8, 78, 100, "medium beet", None, ["raw chukandar", "beet salad"], "Root Vegetables"),
        F("zucchini-cooked", "Cooked Zucchini", "Vegetables", "Sliced summer squash boiled/sautéed", 17, 1.2, 3.1, 0.4, 1.0, 2.2, 8, 180, "cup slices", None, ["courgette"], "Fruiting Vegetables"),
        F("cabbage-raw", "Green Cabbage (Raw shredded)", "Vegetables", "Raw shredded fresh green cabbage", 25, 1.3, 5.8, 0.1, 2.5, 3.2, 18, 70, "cup shredded", [
            {"description": "1 cup shredded (70g)", "grams": 70},
        ], ["patta gobi raw", "cabbage"], "Cruciferous"),
        F("garlic-raw", "Garlic cloves (Raw)", "Vegetables", "Raw peeled fresh garlic", 149, 6.4, 33.1, 0.5, 2.1, 1.0, 17, 3, "clove", [
            {"description": "1 clove (3g)", "grams": 3},
            {"description": "3 cloves (9g)", "grams": 9},
        ], ["lasun", "lahsun", "garlic clove"], "Alliums"),
        F("ginger-raw", "Ginger root (Raw fresh)", "Vegetables", "Fresh peeled ginger root grated", 80, 1.8, 17.8, 0.8, 2.0, 1.7, 13, 5, "teaspoon grated", [
            {"description": "1 tsp grated (5g)", "grams": 5},
            {"description": "1 inch piece (15g)", "grams": 15},
        ], ["adrak", "ale", "ginger fresh"], "Rhizomes"),
    ])

    # =========================================================================
    # GROUP 11: INTERNATIONAL BREADS, CEREALS & PASTA (~45 items)
    # =========================================================================
    items.extend([
        F("bread-white-slice", "White Bread (1 slice)", "Bread", "Commercial enriched white sandwich bread slice", 265, 8.9, 49.1, 3.2, 2.7, 5.0, 490, 28, "slice", [
            {"description": "1 slice (28g)", "grams": 28},
            {"description": "2 slices (56g)", "grams": 56},
        ], ["white bread", "sandwich bread"], "Sandwich Breads", image_key="bread"),
        F("bread-wheat-slice", "Whole Wheat Bread (1 slice)", "Bread", "100% whole wheat commercial bread slice", 247, 12.0, 41.3, 3.4, 6.8, 5.6, 450, 32, "slice", [
            {"description": "1 slice (32g)", "grams": 32},
            {"description": "2 slices (64g)", "grams": 64},
        ], ["brown bread", "whole wheat bread"], "Sandwich Breads", image_key="bread"),
        F("bread-sourdough", "Sourdough Bread (Artisan slice)", "Bread", "Naturally fermented artisan sourdough bread", 250, 9.0, 49.0, 1.5, 2.5, 1.0, 480, 45, "thick slice", [
            {"description": "1 slice (45g)", "grams": 45},
        ], ["sourdough slice", "artisan bread"], "Artisan Breads", image_key="bread"),
        F("bagel-plain", "Plain Bagel", "Bread", "Boiled and baked dense yeast roll", 275, 10.5, 53.0, 1.5, 2.5, 5.0, 440, 95, "bagel", [
            {"description": "1 standard bagel (95g)", "grams": 95},
        ], ["bagel", "plain bagel"], "Breads"),
        F("english-muffin", "English Muffin (Plain)", "Bread", "Yeast-leavened round flatbread split horizontally", 235, 8.5, 46.0, 1.8, 2.8, 3.5, 420, 57, "muffin", [
            {"description": "1 muffin (57g)", "grams": 57},
        ], ["muffin bread"], "Breads"),
        F("pita-bread", "Pita Bread (Whole wheat)", "Bread", "Pocket flatbread baked at high heat", 260, 9.5, 52.0, 1.7, 6.0, 2.0, 380, 60, "pita pocket", [
            {"description": "1 pita (60g)", "grams": 60},
        ], ["pita pocket", "arabic bread"], "Flatbreads"),
        F("tortilla-flour", "Flour Tortilla (6-inch)", "Bread", "Soft round wheat flour tortilla", 305, 8.0, 51.0, 7.5, 2.5, 2.5, 600, 42, "tortilla", [
            {"description": "1 tortilla (42g)", "grams": 42},
            {"description": "2 tortillas (84g)", "grams": 84},
        ], ["flour tortilla", "wrap bread"], "Flatbreads"),
        F("tortilla-corn", "Corn Tortilla (6-inch)", "Bread", "Nixtamalized yellow corn masa tortilla", 218, 5.7, 45.0, 2.8, 6.3, 1.0, 46, 28, "tortilla", [
            {"description": "1 corn tortilla (28g)", "grams": 28},
            {"description": "2 corn tortillas (56g)", "grams": 56},
        ], ["corn tortilla", "taco shell soft"], "Flatbreads"),
        F("pasta-penne-cooked", "Cooked Penne Pasta", "Grains", "Enriched semolina penne boiled al dente", 157, 5.8, 30.9, 0.9, 1.8, 0.6, 1, 140, "cup cooked", [
            {"description": "1 cup cooked (140g)", "grams": 140},
            {"description": "1.5 cups cooked (210g)", "grams": 210},
        ], ["penne pasta", "boiled pasta"], "Pasta", image_key="pasta"),
        F("pasta-spaghetti-cooked", "Cooked Spaghetti", "Grains", "Spaghetti noodles boiled plain", 158, 5.8, 31.0, 0.9, 1.8, 0.6, 1, 140, "cup cooked", [
            {"description": "1 cup cooked (140g)", "grams": 140},
        ], ["spaghetti", "cooked spaghetti"], "Pasta", image_key="pasta"),
        F("pasta-wheat-cooked", "Cooked Whole Wheat Pasta", "Grains", "Whole grain durum wheat pasta boiled", 149, 6.0, 29.5, 1.2, 4.5, 1.0, 2, 140, "cup cooked", [
            {"description": "1 cup cooked (140g)", "grams": 140},
        ], ["brown pasta", "whole wheat pasta"], "Pasta", image_key="pasta"),
        F("pasta-dry-penne", "Uncooked Penne Pasta (Dry)", "Grains", "Dry semolina pasta shapes", 371, 13.0, 74.7, 1.5, 3.2, 2.7, 6, 56, "serving dry", [
            {"description": "2 oz dry (56g)", "grams": 56},
        ], ["dry pasta", "raw pasta"], "Pasta", image_key="pasta"),
        F("noodles-egg-cooked", "Cooked Egg Noodles", "Grains", "Ribbon wheat and egg noodles boiled", 138, 4.5, 25.0, 2.1, 1.2, 0.4, 8, 160, "cup", [
            {"description": "1 cup cooked (160g)", "grams": 160},
        ], ["egg noodles", "chowmein noodles"], "Noodles"),
        F("noodles-hakka-veg", "Vegetable Hakka Noodles", "Grains", "Stir-fried noodles with julienned cabbage, carrots, soy sauce", 185, 4.2, 32.0, 4.8, 2.2, 1.5, 390, 200, "plate", [
            {"description": "1 plate (220g)", "grams": 220},
        ], ["hakka noodles", "veg chowmein", "indo chinese noodles"], "Noodles"),
        F("couscous-cooked", "Cooked Couscous", "Grains", "Steamed granulated durum wheat semolina", 112, 3.8, 23.2, 0.2, 1.4, 0.1, 5, 157, "cup cooked", [
            {"description": "1 cup cooked (157g)", "grams": 157},
        ], ["couscous"], "Grains"),
    ])

    # =========================================================================
    # GROUP 12: FAST FOOD & RESTAURANT MEALS (~50 items)
    # =========================================================================
    items.extend([
        F("pizza-cheese-slice", "Cheese Pizza (1 slice, regular crust)", "Fast Food", "Standard 14-inch pizza slice with tomato sauce and mozzarella", 266, 11.3, 31.8, 10.1, 2.3, 3.8, 598, 107, "slice", [
            {"description": "1 regular slice (107g)", "grams": 107},
            {"description": "2 slices (214g)", "grams": 214},
        ], ["cheese pizza", "margherita pizza slice"], "Pizza", image_key="pizza"),
        F("pizza-pepperoni-slice", "Pepperoni Pizza (1 slice)", "Fast Food", "Regular crust pizza slice with mozzarella and pepperoni", 298, 12.2, 31.4, 13.8, 2.1, 3.6, 684, 111, "slice", [
            {"description": "1 slice (111g)", "grams": 111},
            {"description": "2 slices (222g)", "grams": 222},
        ], ["pepperoni pizza"], "Pizza", image_key="pizza"),
        F("pizza-veggie-slice", "Vegetarian Pizza (1 slice)", "Fast Food", "Pizza topped with bell peppers, onions, olives, mushrooms", 240, 9.5, 32.0, 8.2, 2.8, 4.2, 510, 115, "slice", [
            {"description": "1 slice (115g)", "grams": 115},
        ], ["veggie pizza", "farmhouse pizza"], "Pizza", image_key="pizza"),
        F("burger-cheeseburger", "Cheeseburger (Single patty)", "Fast Food", "Grilled beef patty with American cheese, pickles, mustard, ketchup in bun", 263, 14.5, 28.0, 11.0, 1.5, 5.8, 580, 120, "burger", [
            {"description": "1 cheeseburger (120g)", "grams": 120},
        ], ["cheeseburger", "cheese burger"], "Burgers", image_key="burger"),
        F("burger-chicken", "Crispy Chicken Burger", "Fast Food", "Breaded fried chicken breast fillet in sesame bun with lettuce, mayo", 270, 13.5, 29.0, 12.0, 1.8, 4.5, 620, 160, "burger", [
            {"description": "1 chicken burger (160g)", "grams": 160},
        ], ["chicken burger", "mcchicken style"], "Burgers", image_key="burger"),
        F("burger-veg-mcaloo", "Veggie Burger (Aloo Tikki style)", "Fast Food", "Spiced potato-peas patty in bun with sweet-sour mayo and tomato", 235, 5.5, 36.0, 7.8, 3.2, 6.0, 520, 140, "burger", [
            {"description": "1 veg burger (140g)", "grams": 140},
        ], ["mcaloo tikki", "veg burger"], "Burgers", image_key="burger"),
        F("french-fries-fastfood", "French Fries (Medium)", "Fast Food", "Deep-fried potato batons, salted", 312, 3.4, 41.4, 14.7, 3.8, 0.3, 210, 117, "medium carton", [
            {"description": "Small carton (71g)", "grams": 71},
            {"description": "Medium carton (117g)", "grams": 117},
            {"description": "Large carton (154g)", "grams": 154},
        ], ["french fries", "fries", "potato fries"], "Fast Food Sides"),
        F("caesar-salad-chicken", "Chicken Caesar Salad", "Salads", "Romaine lettuce, grilled chicken breast, parmesan, croutons, creamy dressing", 145, 12.5, 5.5, 8.5, 1.8, 1.5, 380, 220, "bowl", [
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["caesar salad", "chicken salad"], "Salads"),
        F("burrito-chicken-bean", "Chicken and Bean Burrito", "Fast Food", "Flour tortilla wrapped with grilled chicken, black beans, rice, salsa, cheese", 215, 11.5, 26.0, 7.2, 3.5, 2.0, 480, 250, "burrito", [
            {"description": "1 burrito (250g)", "grams": 250},
        ], ["burrito", "chipotle burrito"], "Mexican"),
        F("taco-crispy-beef", "Crispy Beef Taco", "Fast Food", "Hard corn shell with seasoned ground beef, lettuce, cheddar cheese", 240, 11.0, 18.0, 13.5, 2.2, 1.5, 420, 85, "taco", [
            {"description": "1 taco (85g)", "grams": 85},
            {"description": "2 tacos (170g)", "grams": 170},
        ], ["hard shell taco", "beef taco"], "Mexican"),
        F("sushi-california-roll", "California Roll Sushi (6 pcs)", "Fast Food", "Inside-out sushi roll with crab stick, cucumber, avocado, seasoned rice", 155, 4.2, 28.0, 2.8, 1.8, 4.5, 340, 180, "roll (6 pieces)", [
            {"description": "6 pieces (180g)", "grams": 180},
        ], ["california roll", "sushi roll"], "Japanese"),
        F("sushi-salmon-nigiri", "Salmon Nigiri (2 pcs)", "Fast Food", "Hand-pressed seasoned sushi rice topped with raw Atlantic salmon", 170, 7.5, 27.0, 3.5, 0.5, 3.5, 260, 70, "pair (2 pcs)", [
            {"description": "2 pieces (70g)", "grams": 70},
        ], ["salmon nigiri"], "Japanese", image_key="salmon"),
        F("spring-roll-veg", "Vegetable Spring Roll (Fried)", "Snacks", "Crispy fried wrapper stuffed with cabbage, carrot, glass noodles", 250, 4.5, 32.0, 11.5, 2.5, 2.0, 380, 60, "roll", [
            {"description": "1 spring roll (60g)", "grams": 60},
            {"description": "2 rolls (120g)", "grams": 120},
        ], ["chinese spring roll"], "Asian"),
        F("pasta-arrabbiata", "Penne Arrabbiata (Spicy tomato)", "Pasta", "Penne pasta in fiery tomato, garlic, dried red chili sauce with olive oil", 140, 4.2, 24.0, 3.2, 2.2, 3.5, 320, 220, "bowl", [
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["spicy penne", "arrabiata pasta"], "Pasta", image_key="pasta"),
        F("macaroni-and-cheese", "Macaroni and Cheese", "Pasta", "Elbow macaroni in rich cheddar cheese and butter sauce", 210, 8.0, 22.0, 10.0, 1.2, 3.0, 490, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["mac and cheese", "cheesy macaroni"], "Pasta"),
    ])

    return items

print("Catalogue part 3 loaded.")
