"""
Catalogue data part 4: Beverages, Indian Sweets, Snacks/Nuts/Desserts, Cooking Ingredients (Groups 13-16).
"""

from scripts.build_full_database import F

def get_part4():
    items = []

    # =========================================================================
    # GROUP 13: BEVERAGES (~45 items)
    # =========================================================================
    items.extend([
        F("water-plain", "Drinking Water", "Beverages", "Filtered plain water", 0, 0, 0, 0, 0, 0, 2, 240, "glass", [
            {"description": "1 glass (240ml)", "grams": 240},
            {"description": "1 bottle (500ml)", "grams": 500},
            {"description": "1 liter bottle (1000ml)", "grams": 1000},
        ], ["water", "pani"], "Water"),
        F("coffee-black", "Black Coffee (No sugar)", "Beverages", "Brewed coffee without milk or sugar", 2, 0.3, 0.2, 0.05, 0, 0, 2, 240, "mug", [
            {"description": "1 cup (150ml)", "grams": 150},
            {"description": "1 mug (240ml)", "grams": 240},
        ], ["black coffee", "espresso americano"], "Coffee", image_key="coffee"),
        F("coffee-with-milk", "Coffee with milk and sugar", "Beverages", "Filtered coffee brewed with toned milk and 1 tsp sugar", 58, 2.2, 8.5, 1.8, 0, 7.8, 38, 180, "cup", [
            {"description": "1 cup (180ml)", "grams": 180},
        ], ["milk coffee", "nescafe with milk"], "Coffee", image_key="coffee"),
        F("espresso-shot", "Espresso (1 shot)", "Beverages", "High pressure extracted concentrated coffee", 9, 0.8, 1.0, 0.1, 0, 0, 8, 30, "shot (30ml)", [
            {"description": "1 single shot (30ml)", "grams": 30},
            {"description": "Double shot (60ml)", "grams": 60},
        ], ["espresso", "single shot"], "Coffee", image_key="coffee"),
        F("cappuccino-whole-milk", "Cappuccino (Whole milk, unsweetened)", "Beverages", "Espresso with steamed whole milk and thick foam", 50, 2.8, 4.2, 2.5, 0, 4.0, 36, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["cappuccino"], "Coffee", image_key="coffee"),
        F("cafe-latte", "Café Latte (Toned milk)", "Beverages", "Espresso with steamed toned milk and light foam", 45, 2.8, 4.5, 1.8, 0, 4.2, 40, 300, "mug", [
            {"description": "1 standard mug (300ml)", "grams": 300},
        ], ["latte", "cafe latte"], "Coffee", image_key="coffee"),
        F("chai-cutting", "Cutting Chai (Indian tea with milk & sugar)", "Beverages", "Strong boiled Assam tea with toned milk and sugar", 65, 2.2, 10.0, 1.8, 0, 9.5, 35, 120, "glass", [
            {"description": "1 cutting glass (100ml)", "grams": 100},
            {"description": "1 full cup (150ml)", "grams": 150},
        ], ["chai", "cutting chai", "tea with milk", "doodh wali chai"], "Tea", image_key="tea"),
        F("masala-chai", "Masala Chai (Spiced tea)", "Beverages", "Tea brewed with ginger, cardamom, cinnamon, milk and sugar", 68, 2.2, 10.5, 1.8, 0, 9.8, 35, 150, "cup", [
            {"description": "1 cup (150ml)", "grams": 150},
        ], ["ginger tea", "adrak chai", "spiced milk tea"], "Tea", image_key="tea"),
        F("green-tea-plain", "Green Tea (Unsweetened)", "Beverages", "Steeped green tea leaves without sugar or milk", 1, 0.1, 0.0, 0.0, 0, 0, 1, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["green tea", "sencha"], "Tea", image_key="tea"),
        F("black-tea-plain", "Black Tea (Unsweetened)", "Beverages", "Steeped black tea without milk or sugar", 1, 0.1, 0.2, 0.0, 0, 0, 2, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["black tea", "red tea"], "Tea", image_key="tea"),
        F("coconut-water-tender", "Tender Coconut Water (Fresh)", "Beverages", "Natural liquid from fresh green coconut", 19, 0.7, 3.7, 0.2, 1.1, 2.6, 105, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
            {"description": "1 whole tender coconut (300ml)", "grams": 300},
        ], ["nariyal pani", "tender coconut water", "elaneer"], "Natural Drinks"),
        F("orange-juice-fresh", "Fresh Orange Juice (No added sugar)", "Beverages", "Freshly squeezed orange juice with pulp", 45, 0.7, 10.4, 0.2, 0.2, 8.4, 1, 240, "glass", [
            {"description": "1 glass (240ml)", "grams": 240},
        ], ["santra juice", "fresh orange juice"], "Juices", image_key="orange"),
        F("apple-juice-unsweetened", "Apple Juice (100% juice)", "Beverages", "Pasteurized clear apple juice without added sugar", 46, 0.1, 11.3, 0.1, 0.2, 10.0, 4, 240, "glass", [
            {"description": "1 glass (240ml)", "grams": 240},
        ], ["apple juice"], "Juices", image_key="apple"),
        F("sugarcane-juice", "Sugarcane Juice (Ganne ka ras)", "Beverages", "Freshly pressed sugarcane juice with ginger and lemon", 75, 0.2, 18.5, 0.1, 0.5, 17.5, 8, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["ganne ka ras", "sugar cane juice"], "Natural Drinks"),
        F("lemonade-nimbu-pani", "Nimbu Pani (Sweet & salted lemonade)", "Beverages", "Lemon juice with water, sugar, black salt and cumin", 35, 0.2, 8.8, 0.1, 0.1, 8.0, 180, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["shikanji", "nimbu pani", "lemonade"], "Natural Drinks"),
        F("whey-protein-water", "Whey Protein Shake (In water)", "Beverages", "1 scoop 80% whey protein isolate/concentrate shaken in water", 38, 8.0, 0.7, 0.5, 0, 0.5, 50, 330, "shaker", [
            {"description": "1 scoop in 300ml water (330g)", "grams": 330},
        ], ["protein shake water", "whey isolate shake"], "Fitness"),
        F("whey-protein-milk", "Whey Protein Shake (In toned milk)", "Beverages", "1 scoop whey protein blended with 250ml toned milk", 75, 5.6, 4.2, 1.8, 0, 4.0, 60, 330, "shaker", [
            {"description": "1 shake (330g)", "grams": 330},
        ], ["protein shake with milk"], "Fitness"),
        F("mango-milkshake", "Mango Milkshake", "Beverages", "Blended ripe mango pulp with whole milk and sugar", 98, 2.6, 16.5, 2.5, 0.8, 15.0, 35, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["mango shake"], "Shakes", image_key="mango"),
        F("cola-regular", "Cola / Soft Drink (Regular)", "Beverages", "Carbonated sweetened soft drink", 41, 0, 10.6, 0, 0, 10.6, 4, 330, "can (330ml)", [
            {"description": "1 can (330ml)", "grams": 330},
            {"description": "1 bottle (500ml)", "grams": 500},
        ], ["coca cola", "pepsi", "coke regular"], "Sodas"),
        F("cola-diet-zero", "Diet Cola / Coke Zero (Sugar-free)", "Beverages", "Zero-calorie artificially sweetened carbonated drink", 0.5, 0, 0.1, 0, 0, 0, 12, 330, "can (330ml)", [
            {"description": "1 can (330ml)", "grams": 330},
        ], ["coke zero", "diet coke", "pepsi black"], "Sodas"),
    ])

    # =========================================================================
    # GROUP 14: INDIAN SWEETS & MITHAI (~45 items)
    # =========================================================================
    items.extend([
        F("gulab-jamun", "Gulab Jamun (In sugar syrup)", "Sweets", "Fried khoya milk solid spheres soaked in rose-cardamom sugar syrup", 325, 4.5, 55.0, 10.5, 0.5, 48.0, 95, 50, "piece", [
            {"description": "1 piece (50g)", "grams": 50},
            {"description": "2 pieces (100g)", "grams": 100},
        ], ["gulab jamun", "jamun sweet"], "Mithai"),
        F("jalebi", "Jalebi", "Sweets", "Crisp spiral deep-fried fermented maida coils soaked in saffron sugar syrup", 365, 2.5, 68.0, 9.8, 0.3, 58.0, 80, 50, "serving (2-3 jalebis)", [
            {"description": "2-3 jalebis (50g)", "grams": 50},
            {"description": "100g portion", "grams": 100},
        ], ["jilapi", "crispy jalebi"], "Mithai"),
        F("rasgulla", "Rasgulla", "Sweets", "Spongy chhena cottage cheese dumplings cooked in light sugar syrup", 185, 4.2, 38.0, 1.8, 0.2, 35.0, 25, 60, "piece", [
            {"description": "1 rasgulla (60g)", "grams": 60},
            {"description": "2 rasgullas (120g)", "grams": 120},
        ], ["roshogolla", "bengali rasgulla"], "Mithai"),
        F("rasmalai", "Rasmalai", "Sweets", "Soft chhena patties soaked in sweetened saffron-cardamom thickened milk", 215, 6.5, 28.0, 9.0, 0.4, 24.0, 45, 90, "serving (2 pieces)", [
            {"description": "2 pieces with milk (90g)", "grams": 90},
        ], ["rossomalai"], "Mithai"),
        F("kaju-katli", "Kaju Katli (Cashew fudge)", "Sweets", "Diamond-cut fudge made of finely ground cashews and sugar", 440, 10.0, 56.0, 20.0, 2.2, 45.0, 15, 20, "diamond piece", [
            {"description": "1 piece (20g)", "grams": 20},
            {"description": "2 pieces (40g)", "grams": 40},
        ], ["kaju barfi", "cashew katli"], "Mithai"),
        F("besan-ladoo", "Besan Ladoo", "Sweets", "Roasted gram flour balls with desi ghee, sugar and cardamom", 485, 8.5, 58.0, 25.0, 3.8, 42.0, 20, 40, "ladoo", [
            {"description": "1 ladoo (40g)", "grams": 40},
            {"description": "2 ladoos (80g)", "grams": 80},
        ], ["besan laddu"], "Ladoos"),
        F("motichoor-ladoo", "Motichoor Ladoo", "Sweets", "Tiny fried gram flour boondi droplets bound in sugar syrup and ghee", 410, 4.5, 66.0, 14.5, 1.5, 52.0, 40, 45, "ladoo", [
            {"description": "1 ladoo (45g)", "grams": 45},
        ], ["boondi ladoo"], "Ladoos"),
        F("peda-doodh", "Doodh Peda (Mawa peda)", "Sweets", "Cooked khoya milk fudge discs flavored with cardamom and pistachios", 380, 8.2, 54.0, 15.0, 0.5, 46.0, 75, 25, "peda", [
            {"description": "1 peda (25g)", "grams": 25},
            {"description": "2 pedas (50g)", "grams": 50},
        ], ["mathura peda", "milk peda"], "Mithai"),
        F("kheer-rice", "Rice Kheer (Chawal ki kheer)", "Sweets", "Slow-simmered basmati rice pudding in whole milk with nuts and cardamom", 145, 3.8, 22.0, 4.8, 0.4, 15.5, 45, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["payasam", "rice pudding"], "Puddings"),
        F("gajar-ka-halwa", "Gajar ka Halwa (Carrot pudding)", "Sweets", "Grated red carrots simmered in milk, khoya, ghee, sugar and cashews", 245, 4.2, 32.0, 11.5, 2.5, 24.0, 65, 120, "bowl", [
            {"description": "1 small bowl (120g)", "grams": 120},
        ], ["carrot halwa", "gajrela"], "Halwa", image_key="carrot"),
        F("sooji-halwa", "Sooji Halwa (Rava Sheera)", "Sweets", "Roasted semolina cooked with ghee, sugar syrup and cardamom", 320, 4.5, 48.0, 12.8, 1.5, 34.0, 20, 100, "serving", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["rava sheera", "prasad halwa"], "Halwa"),
        F("shrikhand", "Shrikhand (Elaichi / Kesar)", "Sweets", "Strained hung curd whipped with sugar, saffron and cardamom", 265, 6.5, 38.0, 9.8, 0, 36.0, 35, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["kesar elaichi shrikhand"], "Maharashtrian"),
        F("amrakhand", "Amrakhand (Mango shrikhand)", "Sweets", "Hung curd whipped with alphonso mango pulp and sugar", 250, 5.8, 38.0, 8.8, 0.5, 35.0, 30, 100, "katori", None, ["mango shrikhand"], "Maharashtrian", image_key="mango"),
        F("puran-poli", "Puran Poli", "Sweets", "Sweet flatbread stuffed with cooked chana dal, jaggery and cardamom", 285, 6.5, 54.0, 5.0, 3.8, 28.0, 85, 90, "piece", [
            {"description": "1 puran poli (90g)", "grams": 90},
            {"description": "2 puran polis (180g)", "grams": 180},
        ], ["sweet dal roti", "vedmi", "holige"], "Maharashtrian"),
        F("modak-ukadiche", "Ukadiche Modak (Steamed)", "Sweets", "Steamed rice flour dumplings stuffed with grated fresh coconut and jaggery", 215, 3.2, 42.0, 4.2, 2.2, 24.0, 40, 50, "modak", [
            {"description": "1 modak (50g)", "grams": 50},
            {"description": "2 modaks (100g)", "grams": 100},
        ], ["steamed modak", "ganesh modak"], "Maharashtrian"),
    ])

    # =========================================================================
    # GROUP 15: SNACKS, NUTS, SEEDS & DESSERTS (~55 items)
    # =========================================================================
    items.extend([
        F("peanut-butter-creamy", "Peanut Butter (Creamy)", "Nuts", "Roasted ground peanuts spread with light salt", 588, 25.1, 20.0, 50.4, 6.0, 9.2, 429, 32, "2 tablespoons", [
            {"description": "1 tbsp (16g)", "grams": 16},
            {"description": "2 tbsp (32g)", "grams": 32},
        ], ["peanut butter", "smooth peanut butter"], "Nut Butters"),
        F("walnuts-shelled", "Walnuts (Raw halves)", "Nuts", "Shelled English walnut halves", 654, 15.2, 13.7, 65.2, 6.7, 2.6, 2, 28, "handful (14 halves)", [
            {"description": "1 handful / 1 oz (28g)", "grams": 28},
        ], ["akhrot", "walnut halves"], "Tree Nuts"),
        F("cashews-raw", "Cashews (Raw)", "Nuts", "Raw whole cashew nuts", 553, 18.2, 30.2, 43.8, 3.3, 5.9, 12, 28, "handful (18 nuts)", [
            {"description": "1 handful / 1 oz (28g)", "grams": 28},
        ], ["kaju", "raw cashews"], "Tree Nuts"),
        F("peanuts-roasted", "Roasted Peanuts (Salted)", "Nuts", "Dry-roasted shelled peanuts seasoned with salt", 585, 23.7, 21.5, 49.7, 8.0, 4.2, 412, 28, "handful", [
            {"description": "1 handful (28g)", "grams": 28},
            {"description": "50g portion", "grams": 50},
        ], ["singdana", "mungfali", "salted peanuts"], "Nuts"),
        F("pistachios-shelled", "Pistachios (Roasted, salted)", "Nuts", "Shelled roasted pistachio kernels", 562, 20.2, 27.5, 45.3, 10.6, 7.7, 428, 28, "handful", [
            {"description": "1 handful (28g)", "grams": 28},
        ], ["pista", "roasted pistachios"], "Tree Nuts"),
        F("chia-seeds", "Chia Seeds (Dry)", "Nuts", "Whole raw black chia seeds", 486, 16.5, 42.1, 30.7, 34.4, 0, 16, 12, "tablespoon", [
            {"description": "1 tbsp (12g)", "grams": 12},
            {"description": "2 tbsp (24g)", "grams": 24},
        ], ["chia seeds", "salvia hispanica"], "Seeds"),
        F("flax-seeds", "Flax Seeds (Alsi)", "Nuts", "Whole brown flax seeds", 534, 18.3, 28.9, 42.2, 27.3, 1.5, 30, 10, "tablespoon", [
            {"description": "1 tbsp (10g)", "grams": 10},
        ], ["alsi", "flaxseed ground"], "Seeds"),
        F("popcorn-air-popped", "Air-Popped Popcorn", "Snacks", "Plain popped corn without oil or butter", 387, 12.9, 77.8, 4.5, 14.5, 0.8, 8, 24, "cup (approx 8g)", [
            {"description": "3 cups popped (24g)", "grams": 24},
            {"description": "Bowl (50g)", "grams": 50},
        ], ["popcorn plain", "air popped corn"], "Snacks"),
        F("potato-chips-salted", "Potato Chips (Salted)", "Snacks", "Thin sliced deep-fried potato crisps with salt", 536, 7.0, 53.0, 34.6, 4.8, 0.5, 520, 30, "small bag", [
            {"description": "1 individual bag (30g)", "grams": 30},
        ], ["lays salted", "potato crisps", "wafers"], "Chips"),
        F("cookie-chocolate-chip", "Chocolate Chip Cookie (Commercial)", "Snacks", "Baked sweet cookie studded with chocolate chips", 488, 5.5, 64.0, 24.0, 2.4, 34.0, 380, 30, "cookie", [
            {"description": "1 cookie (30g)", "grams": 30},
            {"description": "2 cookies (60g)", "grams": 60},
        ], ["choc chip cookie", "cookie"], "Cookies"),
        F("dark-chocolate-70", "Dark Chocolate (70% cocoa)", "Sweets", "Solid high-cocoa bittersweet chocolate bar", 598, 7.8, 45.9, 42.6, 10.9, 24.0, 20, 40, "bar portion", [
            {"description": "2 squares (20g)", "grams": 20},
            {"description": "4 squares (40g)", "grams": 40},
        ], ["dark chocolate", "70 percent chocolate"], "Chocolate", image_key="chocolate"),
        F("milk-chocolate-bar", "Milk Chocolate Bar", "Sweets", "Sweet milk chocolate bar", 535, 7.6, 59.4, 29.7, 3.4, 51.5, 79, 40, "bar portion", [
            {"description": "1 standard bar (45g)", "grams": 45},
        ], ["cadbury dairy milk", "milk chocolate"], "Chocolate", image_key="chocolate"),
        F("ice-cream-vanilla", "Vanilla Ice Cream", "Sweets", "Churned frozen whole dairy milk cream and sugar with vanilla", 207, 3.5, 23.6, 11.0, 0.7, 21.2, 80, 66, "scoop", [
            {"description": "1 scoop (66g)", "grams": 66},
            {"description": "2 scoops / 1 cup (132g)", "grams": 132},
        ], ["vanilla ice cream", "ice cream scoop"], "Frozen Desserts"),
        F("protein-bar-standard", "Protein Bar (Chocolate Peanut, 20g protein)", "Snacks", "Whey/soy protein isolate snack bar", 360, 33.3, 38.0, 11.0, 8.5, 4.0, 240, 60, "bar", [
            {"description": "1 bar (60g)", "grams": 60},
        ], ["nutrition bar", "energy bar", "protein bar"], "Fitness"),
    ])

    # =========================================================================
    # GROUP 16: COOKING INGREDIENTS, OILS, SPICES & SAUCES (~45 items)
    # =========================================================================
    items.extend([
        F("oil-olive-ev", "Olive Oil (Extra virgin)", "Condiments", "Cold-pressed extra virgin olive oil", 884, 0, 0, 100.0, 0, 0, 2, 14, "tablespoon", [
            {"description": "1 tsp (5g)", "grams": 5},
            {"description": "1 tbsp (14g)", "grams": 14},
        ], ["extra virgin olive oil", "evoo"], "Cooking Oils"),
        F("oil-mustard", "Mustard Oil (Kachi ghani)", "Condiments", "Cold-pressed pungent mustard seed oil", 884, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", [
            {"description": "1 tsp (5g)", "grams": 5},
            {"description": "1 tbsp (14g)", "grams": 14},
        ], ["sarson ka tel", "kachi ghani tel"], "Cooking Oils"),
        F("oil-sunflower", "Sunflower Cooking Oil", "Condiments", "Refined sunflower seed cooking oil", 884, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", None, ["vegetable oil", "refined oil"], "Cooking Oils"),
        F("oil-coconut", "Coconut Oil (Virgin / Cooking)", "Condiments", "Pure pressed coconut oil", 862, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", None, ["nariyal tel", "edible coconut oil"], "Cooking Oils"),
        F("sugar-white", "White Granulated Sugar", "Condiments", "Refined sucrose table sugar crystals", 387, 0, 100.0, 0, 0, 100.0, 1, 4, "teaspoon", [
            {"description": "1 tsp (4g)", "grams": 4},
            {"description": "1 tbsp (12g)", "grams": 12},
        ], ["shakar", "cheeni", "sugar table"], "Sweeteners"),
        F("jaggery-gud", "Jaggery (Gud)", "Condiments", "Unrefined whole cane sugar block", 383, 0.4, 98.0, 0.1, 0, 97.0, 30, 10, "piece / tbsp", [
            {"description": "1 tbsp grated (10g)", "grams": 10},
            {"description": "1 medium piece (25g)", "grams": 25},
        ], ["gud", "gur", "cane jaggery"], "Sweeteners"),
        F("honey-pure", "Honey (Pure natural)", "Condiments", "Natural floral nectar honey", 304, 0.3, 82.4, 0, 0.2, 82.1, 4, 21, "tablespoon", [
            {"description": "1 tsp (7g)", "grams": 7},
            {"description": "1 tbsp (21g)", "grams": 21},
        ], ["shahad", "madh", "raw honey"], "Sweeteners"),
        F("salt-table", "Table Salt (Iodized)", "Condiments", "Iodized sodium chloride mineral salt", 0, 0, 0, 0, 0, 0, 38758, 1, "pinch / tsp", [
            {"description": "1 pinch (1g)", "grams": 1},
            {"description": "1 tsp (6g)", "grams": 6},
        ], ["namak", "iodized salt"], "Seasonings"),
        F("ketchup-tomato", "Tomato Ketchup", "Condiments", "Sweet and tangy tomato condiment sauce", 112, 1.3, 27.4, 0.1, 0.3, 21.8, 907, 17, "tablespoon", [
            {"description": "1 packet (10g)", "grams": 10},
            {"description": "1 tbsp (17g)", "grams": 17},
        ], ["tomato sauce", "ketchup"], "Sauces", image_key="tomato"),
        F("mayonnaise-regular", "Mayonnaise (Standard)", "Condiments", "Emulsified oil, egg yolk and vinegar dressing", 680, 1.0, 0.6, 75.0, 0, 0.6, 635, 14, "tablespoon", [
            {"description": "1 tbsp (14g)", "grams": 14},
        ], ["mayo", "egg mayo"], "Dressings"),
        F("chutney-mint-coriander", "Green Chutney (Mint Coriander)", "Condiments", "Fresh cilantro, mint, green chilies, lemon and cumin paste", 45, 2.0, 7.5, 0.8, 2.5, 1.2, 420, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["hari chutney", "pudina chutney", "green chutney"], "Chutneys"),
        F("chutney-coconut", "Coconut Chutney (South Indian)", "Condiments", "Fresh grated coconut ground with roasted chana dal, green chili, mustard tadka", 185, 3.2, 8.5, 16.0, 4.2, 1.5, 340, 30, "serving (2 tbsp)", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1 small katori (60g)", "grams": 60},
        ], ["nariyal chutney", "idli chutney"], "Chutneys"),
        F("chutney-tamarind-date", "Sweet Tamarind Chutney (Saunth)", "Condiments", "Tangy sweet cooked tamarind pulp with jaggery and roasted cumin", 175, 1.2, 42.0, 0.3, 1.5, 38.0, 310, 20, "tablespoon", [
            {"description": "1 tbsp (20g)", "grams": 20},
        ], ["meethi chutney", "imli chutney", "saunth"], "Chutneys"),
        F("papad-roasted", "Papad (Roasted urad dal)", "Condiments", "Spiced urad dal wafer roasted over open flame", 310, 22.0, 52.0, 1.2, 8.5, 1.0, 1400, 15, "piece", [
            {"description": "1 roasted papad (15g)", "grams": 15},
            {"description": "2 papads (30g)", "grams": 30},
        ], ["roasted papadum", "urad papad"], "Accompaniments"),
        F("papad-fried", "Papad (Deep fried)", "Condiments", "Urad dal wafer deep-fried in vegetable oil", 440, 18.0, 46.0, 20.5, 7.0, 0.8, 1250, 18, "piece", None, ["fried papadum"], "Accompaniments"),
        F("pickle-mango", "Mango Pickle (Aam ka aachar)", "Condiments", "Raw green mango cubes cured in mustard oil, fenugreek, red chili, salt", 175, 1.8, 12.0, 13.5, 3.5, 1.5, 3800, 15, "tablespoon", [
            {"description": "1 tsp (7g)", "grams": 7},
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["aam ka achar", "mango lonche"], "Pickles"),
    ])

    return items

print("Catalogue part 4 loaded.")
