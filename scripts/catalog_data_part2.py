"""
Catalogue data part 2: South Indian breakfast, street food/chaat, dairy/protein, meats, fruits, vegetables (Groups 5-10).
"""

from scripts.build_full_database import F

def get_part2():
    items = []

    # =========================================================================
    # GROUP 5: BREAKFAST & SOUTH INDIAN SPECIALTIES (~50 items)
    # =========================================================================
    items.extend([
        F("idli-steamed", "Steamed Idli", "Breakfast", "Fermented rice and black gram batter steamed into soft cakes", 135, 4.2, 28.0, 0.4, 1.4, 0.5, 95, 60, "piece (2 idlis)", [
            {"description": "1 idli (40g)", "grams": 40},
            {"description": "2 idlis (80g)", "grams": 80},
            {"description": "3 idlis (120g)", "grams": 120},
        ], ["idli", "steamed rice cake", "idly"], "South Indian", image_key="idli"),
        F("rava-idli", "Rava Idli", "Breakfast", "Steamed semolina and curd cakes with mustard, cashews, ginger", 155, 4.8, 26.0, 3.5, 1.2, 0.8, 180, 50, "piece", [
            {"description": "1 rava idli (50g)", "grams": 50},
            {"description": "2 rava idlis (100g)", "grams": 100},
        ], ["sooji idli"], "South Indian", image_key="idli"),
        F("dosa-plain", "Plain Dosa (Sada Dosa)", "Breakfast", "Thin crisp fermented crepe cooked on tawa with light oil", 175, 4.0, 30.0, 4.2, 1.5, 0.5, 160, 80, "piece", [
            {"description": "1 plain dosa (80g)", "grams": 80},
        ], ["sada dosa", "plain crepe"], "South Indian", image_key="dosa"),
        F("dosa-masala", "Masala Dosa", "Breakfast", "Crisp dosa filled with spiced mashed potato and onion curry", 195, 4.2, 29.0, 7.0, 2.2, 1.0, 260, 150, "piece", [
            {"description": "1 masala dosa (150g)", "grams": 150},
            {"description": "1 large restaurant masala dosa (220g)", "grams": 220},
        ], ["aloo masala dosa"], "South Indian", image_key="dosa"),
        F("dosa-rava", "Rava Dosa (Plain)", "Breakfast", "Lacy crisp semolina and rice flour crepe cooked with cumin", 210, 4.5, 34.0, 6.5, 1.8, 0.5, 190, 90, "piece", None, ["suji dosa", "crispy rava dosa"], "South Indian", image_key="dosa"),
        F("dosa-rava-masala", "Rava Masala Dosa", "Breakfast", "Crisp rava dosa filled with spiced potato masala", 225, 4.5, 32.0, 8.8, 2.2, 1.0, 270, 160, "piece", None, ["onion rava masala dosa"], "South Indian", image_key="dosa"),
        F("dosa-mysore-masala", "Mysore Masala Dosa", "Breakfast", "Crisp dosa lined with spicy red chili-garlic chutney and potato filling", 215, 4.5, 30.0, 8.5, 2.5, 1.2, 310, 170, "piece", None, ["red chutney dosa"], "South Indian", image_key="dosa"),
        F("uttapam-onion", "Onion Uttapam", "Breakfast", "Thick fermented pancake topped with chopped onions and coriander", 180, 4.2, 30.0, 4.8, 2.0, 1.5, 210, 120, "piece", [
            {"description": "1 uttapam (120g)", "grams": 120},
        ], ["uthappam", "onion pancake"], "South Indian"),
        F("uttapam-tomato", "Tomato Onion Uttapam", "Breakfast", "Thick pancake topped with diced tomatoes, onions, green chili", 170, 4.0, 28.0, 4.5, 2.2, 1.8, 200, 130, "piece", None, ["tomato uttapam"], "South Indian"),
        F("medu-vada", "Medu Vada", "Breakfast", "Crisp deep-fried urad dal doughnut-shaped fritters with cumin and pepper", 285, 9.5, 32.0, 13.5, 4.2, 0.5, 240, 50, "piece", [
            {"description": "1 vada (50g)", "grams": 50},
            {"description": "2 vadas (100g)", "grams": 100},
        ], ["urad dal vada", "ulundu vadai", "sambar vada base"], "South Indian"),
        F("appam", "Appam (Hoppers)", "Breakfast", "Fermented rice and coconut milk bowl-shaped pancake with soft center", 140, 2.5, 28.0, 2.0, 1.0, 2.5, 90, 75, "piece", [
            {"description": "1 appam (75g)", "grams": 75},
            {"description": "2 appams (150g)", "grams": 150},
        ], ["kerala appam", "hoppers", "palappam"], "South Indian"),
        F("puttu", "Kerala Puttu", "Breakfast", "Steamed cylindrical layers of coarse rice flour and grated coconut", 195, 3.8, 38.0, 3.2, 2.4, 1.5, 80, 100, "piece", None, ["steamed rice cake with coconut"], "South Indian"),
        F("neer-dosa", "Neer Dosa", "Breakfast", "Delicate, lace-thin steamed rice crepes from Mangalore", 145, 2.8, 30.0, 1.2, 0.8, 0.2, 95, 60, "piece", [
            {"description": "1 neer dosa (60g)", "grams": 60},
            {"description": "2 neer dosas (120g)", "grams": 120},
        ], ["water dosa", "mangalore neer dosa"], "South Indian"),
        F("pesarattu", "Pesarattu (Green moong dosa)", "Breakfast", "Andhra whole green gram crepe with ginger, cumin and green chili", 190, 8.5, 28.0, 4.8, 4.5, 0.8, 170, 90, "piece", [
            {"description": "1 pesarattu (90g)", "grams": 90},
        ], ["green gram dosa", "moong dal dosa"], "South Indian"),
    ])

    # =========================================================================
    # GROUP 6: INDIAN STREET FOOD, SNACKS & CHAAT (~45 items)
    # =========================================================================
    items.extend([
        F("vada-pav", "Vada Pav", "Snacks", "Spiced potato batata vada in pav with dry garlic chutney and green chutney", 270, 5.5, 38.0, 10.5, 2.5, 2.2, 420, 130, "piece", [
            {"description": "1 vada pav (130g)", "grams": 130},
            {"description": "2 vada pavs (260g)", "grams": 260},
        ], ["wada pav", "bombay burger", "batata vada pav"], "Street Food"),
        F("samosa-veg", "Vegetable Samosa", "Snacks", "Crisp fried pastry filled with spiced potatoes and peas", 290, 4.5, 35.0, 15.0, 2.5, 1.5, 340, 80, "piece", [
            {"description": "1 medium samosa (80g)", "grams": 80},
            {"description": "2 samosas (160g)", "grams": 160},
        ], ["samosa", "punjabi samosa", "aloo samosa"], "Street Food", image_key="samosa"),
        F("bread-pakora", "Bread Pakora (Potato stuffed)", "Snacks", "Bread slices filled with aloo masala, dipped in besan and deep-fried", 260, 5.2, 32.0, 12.5, 2.2, 1.8, 360, 110, "piece", [
            {"description": "1 piece (110g)", "grams": 110},
        ], ["stuffed bread pakoda"], "Snacks"),
        F("onion-pakora", "Onion Pakora (Kanda Bhaji)", "Snacks", "Crispy spiced onion slivers coated in gram flour and deep-fried", 310, 6.5, 30.0, 18.5, 3.8, 2.5, 310, 80, "plate", [
            {"description": "1 small plate (80g)", "grams": 80},
            {"description": "1 medium plate (120g)", "grams": 120},
        ], ["kanda bhaji", "pyaz pakoda", "onion fritters"], "Snacks"),
        F("palak-pakora", "Palak Pakora (Spinach fritters)", "Snacks", "Fresh spinach leaves battered in spiced gram flour and fried crisp", 275, 5.8, 26.0, 16.5, 4.0, 1.5, 290, 80, "plate", None, ["spinach bhajiya"], "Snacks"),
        F("dhokla-khaman", "Khaman Dhokla", "Snacks", "Steamed spongy fermented besan cakes with mustard tadka and green chilies", 160, 6.5, 24.0, 4.2, 2.0, 4.5, 380, 80, "piece (2 squares)", [
            {"description": "2 pieces (80g)", "grams": 80},
            {"description": "4 pieces (160g)", "grams": 160},
        ], ["dhokla", "besan dhokla", "gujarati khaman"], "Snacks"),
        F("khandvi", "Khandvi", "Snacks", "Delicate rolled sheets of cooked besan and curd tempered with mustard and coconut", 145, 5.2, 17.0, 6.2, 1.8, 2.0, 260, 80, "serving (4 rolls)", [
            {"description": "4 rolls (80g)", "grams": 80},
        ], ["gujarati khandvi", "suralichi vadi"], "Snacks"),
        F("kachori-pyaaz", "Pyaaz Kachori (Onion)", "Snacks", "Flaky deep-fried Rajasthani pastry stuffed with spicy onion masala", 340, 5.5, 40.0, 17.5, 3.0, 2.2, 380, 100, "piece", [
            {"description": "1 kachori (100g)", "grams": 100},
        ], ["onion kachori", "rajasthani kachori"], "Snacks"),
        F("kachori-dal", "Khasta Dal Kachori (Moong)", "Snacks", "Crisp flaky pastry stuffed with seasoned yellow moong dal", 360, 7.5, 42.0, 18.0, 3.8, 1.5, 360, 80, "piece", [
            {"description": "1 dal kachori (80g)", "grams": 80},
        ], ["moong dal kachori", "khasta kachori"], "Snacks"),
        F("fafda", "Fafda", "Snacks", "Crisp savory deep-fried gram flour strips seasoned with carom seeds (ajwain)", 420, 10.5, 48.0, 21.0, 4.2, 1.0, 440, 50, "serving", [
            {"description": "1 serving (50g)", "grams": 50},
        ], ["gujarati fafda"], "Snacks"),
        F("dabeli", "Kutchi Dabeli", "Snacks", "Spiced sweet-sour potato filling in pav with roasted masala peanuts, sev, pomegranate", 250, 4.8, 38.0, 8.8, 2.5, 6.5, 360, 120, "piece", [
            {"description": "1 dabeli (120g)", "grams": 120},
        ], ["double roti", "kutch dabeli"], "Street Food"),
        F("bhel-puri", "Bhel Puri", "Snacks", "Puffed rice tossed with boiled potatoes, onions, sev, tangy chutneys", 185, 4.2, 32.0, 4.8, 2.5, 6.2, 340, 150, "plate", [
            {"description": "1 plate (150g)", "grams": 150},
        ], ["bhel", "mumbai bhel"], "Chaat"),
        F("sev-puri", "Sev Puri", "Snacks", "Crisp flat puris topped with potatoes, onions, three chutneys and nylon sev", 240, 4.5, 33.0, 10.2, 2.8, 5.5, 380, 130, "plate (6 puris)", [
            {"description": "1 plate (6 puris, 130g)", "grams": 130},
        ], ["sev batata puri"], "Chaat"),
        F("pani-puri", "Pani Puri (Golgappa)", "Snacks", "Crisp hollow semolina spheres filled with spiced potato/chickpeas and mint water", 130, 2.8, 24.0, 2.2, 1.5, 2.5, 290, 150, "serving (6 puris)", [
            {"description": "6 puris with water (150g)", "grams": 150},
            {"description": "8 puris (200g)", "grams": 200},
        ], ["golgappa", "puchka", "batashe"], "Chaat"),
        F("dahi-puri", "Dahi Puri (SPDP)", "Snacks", "Crisp hollow puris stuffed with potatoes, topped with sweetened curd, sev and chutneys", 210, 4.8, 28.0, 8.8, 2.0, 7.5, 260, 160, "plate (6 puris)", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["dahi sev batata puri"], "Chaat"),
        F("papdi-chaat", "Papdi Chaat", "Snacks", "Crisp wheat wafers layered with curd, boiled potatoes, chickpeas and tamarind chutney", 215, 5.2, 29.0, 9.0, 2.8, 6.5, 320, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["dahi papdi chaat"], "Chaat"),
        F("aloo-tikki-chaat", "Aloo Tikki Chaat", "Snacks", "Pan-fried crisp potato patties served with chole, curd, sev and chutneys", 225, 4.8, 30.0, 9.5, 3.2, 4.5, 360, 180, "plate", [
            {"description": "1 plate (180g)", "grams": 180},
        ], ["tikki chaat", "potato patty chaat"], "Chaat"),
        F("frankie-veg", "Vegetable Frankie / Roll", "Snacks", "Flatbread wrap stuffed with spiced potato roll, chopped onions, chaat masala", 220, 5.0, 36.0, 6.5, 2.5, 2.5, 360, 140, "roll", [
            {"description": "1 veg roll (140g)", "grams": 140},
        ], ["veg roll", "mumbai frankie", "kathi roll veg"], "Wraps"),
        F("frankie-paneer", "Paneer Frankie / Roll", "Snacks", "Roti wrap filled with spiced sautéed paneer cubes, capsicum, mint sauce", 245, 9.5, 32.0, 9.0, 2.2, 2.8, 380, 160, "roll", [
            {"description": "1 paneer roll (160g)", "grams": 160},
        ], ["paneer kathi roll"], "Wraps"),
        F("sandwich-bombay-grilled", "Bombay Grilled Veg Sandwich", "Snacks", "Toasted sandwich with beetroot, potato, cucumber, tomato, green chutney, butter", 210, 4.8, 32.0, 7.0, 2.8, 2.5, 390, 160, "sandwich", [
            {"description": "1 sandwich (160g)", "grams": 160},
        ], ["mumbai sandwich", "veg grilled sandwich"], "Sandwiches"),
        F("veg-cutlet", "Vegetable Cutlet", "Snacks", "Mashed vegetable patties coated in breadcrumbs and shallow-fried", 215, 4.2, 28.0, 9.5, 3.0, 2.0, 280, 75, "piece", [
            {"description": "1 cutlet (75g)", "grams": 75},
            {"description": "2 cutlets (150g)", "grams": 150},
        ], ["veg patty"], "Snacks"),
    ])

    # =========================================================================
    # GROUP 7: DAIRY & VEGETARIAN PROTEIN (~45 items)
    # =========================================================================
    items.extend([
        F("milk-cow-toned", "Toned milk (3% fat)", "Dairy", "Pasteurized, homogenized cow milk with 3.0% fat", 58, 3.2, 4.7, 3.0, 0, 4.7, 48, 240, "glass", [
            {"description": "1 cup (150ml)", "grams": 150},
            {"description": "1 glass (240ml)", "grams": 240},
        ], ["toned milk", "cow milk toned"], "Liquid Milk", image_key="milk"),
        F("milk-cow-skimmed", "Double toned / Skimmed milk (1.5% fat)", "Dairy", "Pasteurized low-fat milk", 45, 3.3, 4.8, 1.5, 0, 4.8, 50, 240, "glass", None, ["skim milk", "low fat milk"], "Liquid Milk", image_key="milk"),
        F("milk-buffalo-whole", "Buffalo milk (Whole 6.5% fat)", "Dairy", "Full-fat fresh buffalo milk", 97, 3.8, 5.2, 6.5, 0, 5.2, 40, 240, "glass", None, ["bhains ka doodh", "full fat milk"], "Liquid Milk", image_key="milk"),
        F("greek-yogurt-plain", "Greek yogurt (Plain 2% fat)", "Dairy", "Strained high-protein yogurt", 73, 10.0, 3.9, 2.0, 0, 3.6, 36, 150, "cup", [
            {"description": "1 container (150g)", "grams": 150},
            {"description": "1 cup (200g)", "grams": 200},
        ], ["strained yogurt", "hung curd"], "Cultured Dairy", image_key="curd"),
        F("buttermilk-chaas", "Chaas (Salted Buttermilk)", "Dairy", "Diluted curd churned with water, cumin, salt, ginger", 28, 1.6, 2.2, 1.2, 0, 2.2, 160, 240, "glass", [
            {"description": "1 glass (240ml)", "grams": 240},
        ], ["mattha", "mor", "spiced buttermilk"], "Cultured Dairy"),
        F("lassi-sweet", "Sweet Lassi", "Dairy", "Thick blended whole milk curd with sugar and cardamom", 115, 3.2, 17.5, 3.5, 0, 16.5, 45, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["punjabi lassi", "sweet yogurt drink"], "Cultured Dairy"),
        F("lassi-mango", "Mango Lassi", "Dairy", "Curd blended with alphonso mango pulp and sugar", 125, 3.0, 20.0, 3.5, 0.5, 18.5, 42, 250, "glass", None, ["mango yogurt shake"], "Cultured Dairy"),
        F("ghee-desi", "Desi Cow Ghee (Clarified butter)", "Dairy", "Simmered and strained pure milk fat", 895, 0.1, 0.0, 99.5, 0, 0, 2, 15, "tablespoon", [
            {"description": "1 tsp (5g)", "grams": 5},
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["clarified butter", "cow ghee", "shuddh ghee"], "Fats"),
        F("butter-salted", "Salted butter (Commercial)", "Dairy", "Pasteurized churned cream with salt", 717, 0.9, 0.1, 81.1, 0, 0.1, 643, 14, "tablespoon", [
            {"description": "1 pat (10g)", "grams": 10},
            {"description": "1 tbsp (14g)", "grams": 14},
        ], ["amul butter", "table butter"], "Fats"),
        F("butter-white", "White butter (Makhan)", "Dairy", "Homemade fresh unsalted churned cultured cream", 740, 0.8, 0.5, 82.0, 0, 0.5, 12, 15, "tablespoon", None, ["safed makhan", "desi makkhan"], "Fats"),
        F("paneer-lowfat", "Low-fat Paneer", "Dairy", "Cottage cheese made from skimmed milk", 160, 25.0, 3.5, 4.5, 0, 2.0, 35, 100, "serving", [
            {"description": "100g portion", "grams": 100},
        ], ["diet paneer", "skim paneer"], "Fresh Cheese", image_key="paneer"),
        F("tofu-firm", "Firm Tofu", "Pulses", "Coagulated soybean curd, pressed firm", 144, 15.5, 2.8, 8.0, 2.3, 0.5, 14, 100, "serving", [
            {"description": "1 block / serving (100g)", "grams": 100},
        ], ["bean curd", "soy paneer"], "Soy"),
        F("tofu-silken", "Silken Tofu", "Pulses", "Soft unpressed soybean curd", 55, 5.0, 2.0, 2.8, 0.5, 1.0, 30, 100, "serving", None, ["soft tofu"], "Soy"),
        F("soya-chunks-dry", "Soya chunks (Dry TVP)", "Pulses", "Defatted textured soy flour chunks", 345, 52.0, 33.0, 0.5, 13.0, 0, 20, 30, "serving", [
            {"description": "1 cup dry (30g)", "grams": 30},
        ], ["mealmaker", "soy nuggets", "nutrela"], "Soy"),
        F("soya-chunks-boiled", "Soya chunks (Boiled / Rehydrated)", "Pulses", "Boiled, squeezed textured soy protein", 115, 17.5, 11.0, 0.2, 4.3, 0, 7, 100, "serving", [
            {"description": "1 cup cooked (100g)", "grams": 100},
        ], ["cooked mealmaker"], "Soy"),
        F("soy-milk-plain", "Soy milk (Unsweetened)", "Dairy", "Water extract of whole soybeans, unsweetened", 33, 2.8, 1.6, 1.8, 0.5, 0.8, 51, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["soya milk"], "Plant Milk"),
        F("almond-milk-unsweetened", "Almond milk (Unsweetened)", "Dairy", "Filtered almond beverage without added sugar", 15, 0.6, 0.6, 1.2, 0.4, 0.1, 70, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["badam milk unsweetened"], "Plant Milk"),
        F("oat-milk-plain", "Oat milk (Plain)", "Dairy", "Oat and water beverage", 48, 1.0, 7.5, 1.5, 0.8, 3.2, 45, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
        ], ["oat drink"], "Plant Milk"),
        F("cheese-cheddar", "Cheddar cheese", "Dairy", "Aged natural hard cheese", 403, 24.9, 1.3, 33.1, 0, 0.5, 621, 28, "slice", [
            {"description": "1 slice (28g)", "grams": 28},
        ], ["cheddar block"], "Cheese"),
        F("cheese-mozzarella", "Mozzarella cheese (Part skim)", "Dairy", "Semi-soft Italian style curd cheese", 280, 27.5, 3.1, 17.1, 0, 1.0, 627, 28, "slice", [
            {"description": "1 slice (28g)", "grams": 28},
            {"description": "1/4 cup shredded (28g)", "grams": 28},
        ], ["pizza cheese"], "Cheese"),
        F("cheese-parmesan", "Parmesan cheese (Grated)", "Dairy", "Hard granular Italian cheese", 431, 38.4, 4.1, 28.6, 0, 0.9, 1529, 10, "tablespoon", [
            {"description": "1 tbsp grated (10g)", "grams": 10},
        ], ["parmigiano"], "Cheese"),
        F("cheese-process-slice", "Processed cheese slice", "Dairy", "Pasteurized processed cheddar slice", 320, 18.0, 4.5, 26.0, 0, 4.0, 1200, 20, "slice", [
            {"description": "1 slice (20g)", "grams": 20},
        ], ["amul cheese slice", "sandwich slice"], "Cheese"),
    ])

    # =========================================================================
    # GROUP 8: EGGS, POULTRY, MEAT & SEAFOOD (~65 items)
    # =========================================================================
    items.extend([
        F("egg-boiled-whole", "Boiled egg (Whole, large)", "Meat", "Hard boiled shell egg", 155, 12.6, 1.1, 10.6, 0, 1.1, 124, 50, "large egg", [
            {"description": "1 large egg (50g)", "grams": 50},
            {"description": "2 large eggs (100g)", "grams": 100},
        ], ["boiled egg", "hard boiled egg", "anda ubla hua"], "Eggs", image_key="egg"),
        F("egg-white-boiled", "Egg white (Boiled, large)", "Meat", "Cooked white of egg without yolk", 52, 10.9, 0.7, 0.2, 0, 0.7, 166, 33, "white", [
            {"description": "1 egg white (33g)", "grams": 33},
            {"description": "3 egg whites (100g)", "grams": 100},
        ], ["boiled egg white", "ande ki safedi"], "Eggs"),
        F("egg-fried", "Fried egg (Sunny side up)", "Meat", "Whole egg pan-fried in 1 tsp oil", 195, 13.5, 0.8, 15.0, 0, 0.8, 180, 55, "egg", [
            {"description": "1 fried egg (55g)", "grams": 55},
        ], ["sunny side up", "half fry anda"], "Eggs"),
        F("egg-scrambled", "Scrambled eggs", "Meat", "Whisked eggs scrambled with touch of butter and salt", 165, 11.5, 1.5, 12.0, 0, 1.2, 210, 100, "serving (2 eggs)", [
            {"description": "2 eggs scrambled (100g)", "grams": 100},
        ], ["scrambled anda"], "Eggs"),
        F("egg-bhurji", "Egg Bhurji (Indian style)", "Meat", "Scrambled eggs sautéed with onions, tomatoes, green chilies, cilantro", 175, 12.0, 3.5, 12.5, 0.8, 2.0, 260, 120, "serving (2 eggs)", [
            {"description": "1 serving (2 eggs, 120g)", "grams": 120},
        ], ["anda bhurji", "spiced scrambled eggs"], "Eggs"),
        F("egg-curry", "Egg Curry (Dhaba style)", "Meat", "Hard-boiled eggs simmered in onion-tomato ginger gravy", 160, 10.5, 6.0, 10.5, 1.2, 2.5, 290, 180, "serving (2 eggs + gravy)", [
            {"description": "1 serving with 2 eggs (180g)", "grams": 180},
        ], ["anda curry", "egg masala"], "Eggs"),
        F("omelette-masala", "Masala Omelette (2 eggs)", "Meat", "Beaten eggs pan-fried with onions, tomatoes, green chilies", 185, 13.0, 2.5, 13.5, 0.8, 1.5, 240, 110, "omelette", [
            {"description": "2-egg omelette (110g)", "grams": 110},
        ], ["indian omelette"], "Eggs"),
        F("chicken-breast-raw", "Chicken breast (Raw, boneless skinless)", "Meat", "Raw boneless trimmed poultry breast", 120, 22.5, 0.0, 2.6, 0, 0, 65, 100, "serving", [
            {"description": "1 raw breast (170g)", "grams": 170},
            {"description": "100g raw", "grams": 100},
        ], ["raw chicken breast", "kaccha chicken"], "Poultry"),
        F("chicken-breast-grilled", "Grilled chicken breast", "Meat", "Boneless skinless chicken breast grilled with salt and pepper", 165, 31.0, 0.0, 3.6, 0, 0, 74, 120, "fillet", [
            {"description": "1 small fillet (100g)", "grams": 100},
            {"description": "1 standard fillet (140g)", "grams": 140},
        ], ["chicken breast", "grilled chicken"], "Poultry", image_key="chicken_breast"),
        F("chicken-breast-boiled", "Boiled chicken breast (Shredded)", "Meat", "Poached chicken breast pulled into shreds", 150, 30.0, 0.0, 3.0, 0, 0, 70, 100, "serving", None, ["poached chicken"], "Poultry"),
        F("chicken-thigh-grilled", "Grilled chicken thigh (Skinless)", "Meat", "Boneless skinless chicken thigh roasted", 195, 24.5, 0.0, 10.5, 0, 0, 85, 110, "thigh", [
            {"description": "1 thigh (110g)", "grams": 110},
        ], ["chicken thigh"], "Poultry"),
        F("chicken-curry-homestyle", "Homestyle Chicken Curry", "Meat", "Chicken pieces on bone simmered in onion-tomato spiced gravy", 170, 16.5, 4.5, 9.5, 1.2, 1.5, 290, 200, "bowl", [
            {"description": "1 bowl with chicken pieces (200g)", "grams": 200},
        ], ["tariwala chicken", "murgh curry"], "Poultry"),
        F("butter-chicken", "Butter Chicken (Murgh Makhani)", "Meat", "Tandoori chicken pieces in creamy tomato cashew butter gravy", 225, 15.0, 8.5, 15.0, 1.5, 4.5, 340, 220, "bowl", [
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["murgh makhani"], "Poultry"),
        F("chicken-tikka-tandoori", "Chicken Tikka (Tandoori boneless)", "Meat", "Spiced yogurt-marinated boneless chicken cubes charred in tandoor", 180, 26.0, 3.5, 6.8, 1.0, 1.5, 360, 150, "serving (6 pcs)", [
            {"description": "6 pieces (150g)", "grams": 150},
        ], ["tandoori chicken tikka"], "Poultry"),
        F("tandoori-chicken", "Tandoori Chicken (On bone)", "Meat", "Chicken legs/breast marinated in yogurt and spices, clay oven roasted", 175, 25.0, 2.5, 7.0, 0.8, 1.0, 340, 160, "leg quarter", [
            {"description": "1 leg quarter with bone (160g)", "grams": 160},
        ], ["tandoori murgh"], "Poultry"),
        F("chicken-kebab", "Chicken Seekh Kebab", "Meat", "Minced spiced chicken skewers grilled over charcoal", 205, 21.0, 5.0, 11.0, 1.2, 1.0, 380, 100, "skewer (2 kebabs)", [
            {"description": "2 seekh kebabs (100g)", "grams": 100},
        ], ["chicken seekh"], "Poultry"),
        F("chicken-nuggets", "Chicken Nuggets (Crispy fried)", "Meat", "Breaded and deep-fried ground chicken bites", 295, 15.0, 18.0, 18.0, 1.0, 0.5, 540, 90, "serving (5 nuggets)", [
            {"description": "5 nuggets (90g)", "grams": 90},
        ], ["fried nuggets"], "Fast Food"),
        F("salmon-grilled", "Grilled Salmon fillet", "Meat", "Fresh Atlantic salmon pan-seared with olive oil and lemon", 206, 22.0, 0.0, 12.3, 0, 0, 60, 140, "fillet", [
            {"description": "1 standard fillet (140g)", "grams": 140},
        ], ["salmon", "pan seared salmon"], "Seafood", image_key="salmon"),
        F("tuna-canned-water", "Canned Tuna (In water)", "Meat", "Chunk light tuna canned in spring water, drained", 116, 25.5, 0.0, 1.0, 0, 0, 335, 100, "can portion", [
            {"description": "1 can drained (120g)", "grams": 120},
        ], ["canned tuna", "tuna in water"], "Seafood"),
        F("pomfret-fry", "Pomfret Fish Fry (Rava crusted)", "Meat", "Silver pomfret steaks marinated in spicy masala, rava coated and pan-fried", 215, 19.5, 8.0, 11.5, 0.8, 0.5, 310, 120, "fish steak", [
            {"description": "1 whole small pomfret (120g)", "grams": 120},
        ], ["rava fried fish", "paplet fry"], "Seafood"),
        F("fish-curry-goan", "Goan Fish Curry", "Meat", "Fish steaks simmered in coconut milk, red chili, kokum gravy", 165, 14.5, 5.0, 9.8, 1.2, 1.0, 280, 200, "bowl", [
            {"description": "1 bowl with fish piece (200g)", "grams": 200},
        ], ["coconut fish curry", "malabar fish curry"], "Seafood"),
        F("prawns-masala", "Prawns Masala (Shrimp curry)", "Meat", "Prawns tossed in spicy onion-tomato garlic gravy", 140, 18.0, 5.5, 4.8, 1.0, 1.2, 320, 160, "katori", [
            {"description": "1 bowl (160g)", "grams": 160},
        ], ["shrimp masala", "kolambi masala"], "Seafood"),
        F("prawns-boiled", "Boiled Shrimp / Prawns (Plain)", "Meat", "Steamed peeled shrimp without added oil", 99, 21.0, 0.2, 1.1, 0, 0, 111, 100, "serving", None, ["shrimp boiled", "plain prawns"], "Seafood"),
        F("mutton-curry", "Mutton Curry (Goat meat)", "Meat", "Tender goat meat cubes on bone simmered in thick spiced onion gravy", 220, 17.0, 4.5, 14.8, 1.0, 1.2, 330, 200, "bowl", [
            {"description": "1 bowl with pieces (200g)", "grams": 200},
        ], ["goat meat curry", "mutton rassa"], "Meat"),
        F("mutton-sukka", "Mutton Sukka (Dry roast)", "Meat", "Goat meat pan-roasted with black pepper, dry coconut and spices", 260, 22.0, 5.0, 17.0, 1.5, 0.8, 340, 150, "katori", None, ["sukka mutton", "sukha gosht"], "Meat"),
        F("ground-beef-90-10", "Lean Ground Beef (90% lean, cooked)", "Meat", "Pan-browned extra lean ground beef, drained", 215, 26.0, 0.0, 11.5, 0, 0, 75, 100, "patty / serving", [
            {"description": "1 burger patty (110g)", "grams": 110},
        ], ["minced beef", "lean beef mince"], "Meat"),
        F("turkey-breast-roasted", "Roasted Turkey Breast", "Meat", "Skinless turkey breast roasted and carved into slices", 135, 30.0, 0.0, 1.0, 0, 0, 55, 100, "slices", [
            {"description": "3 slices (85g)", "grams": 85},
        ], ["turkey breast slices"], "Poultry"),
    ])

    return items

print("Catalogue part 2 loaded.")
