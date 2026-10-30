"""
Catalogue data part 5: Extensive regional Indian dishes (Maharashtrian, South Indian, North Indian, Bengali, Gujarati) and Mithai (~250 items).
"""

from scripts.build_full_database import F

def get_part5():
    items = []

    # =========================================================================
    # MAHARASHTRIAN REGIONAL DISHES & CURRIES (~50 items)
    # =========================================================================
    items.extend([
        F("batata-rassa", "Batata Rassa (Potato curry)", "Curries", "Spiced thin potato curry with coconut, goda masala and ginger", 125, 2.2, 16.5, 5.5, 2.2, 1.5, 240, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["aloo rassa", "batatyacha rassa", "marathi aloo curry"], "Maharashtrian", image_key="potato"),
        F("chawli-chi-amti", "Chawli chi Amti (Black-eyed bean curry)", "Pulses", "Black-eyed beans cooked with coconut, tamarind and jaggery", 135, 6.8, 19.0, 3.8, 4.5, 2.5, 260, 160, "katori", [
            {"description": "1 katori (160g)", "grams": 160},
        ], ["lobia amti", "chavali amti"], "Maharashtrian"),
        F("shev-bhaji", "Khandeshi Shev Bhaji", "Curries", "Crisp spicy gram flour shev cooked in fiery dark rassa gravy", 240, 6.5, 22.0, 14.5, 3.2, 1.8, 380, 180, "bowl", [
            {"description": "1 bowl with shev (180g)", "grams": 180},
        ], ["shev bhaji", "khandeshi shev bhaji"], "Maharashtrian"),
        F("kolhapuri-misal", "Kolhapuri Kat / Rassa", "Curries", "Fiery thin red oil chili rassa for Kolhapuri misal", 175, 4.2, 12.0, 12.5, 2.5, 1.2, 450, 180, "bowl", None, ["kolhapuri kat", "tambda rassa veg"], "Maharashtrian"),
        F("tomato-saar", "Tomato Saar", "Curries", "Tangy Maharashtrian tomato soup tempered with cumin, coconut milk, curry leaves", 70, 1.5, 8.5, 3.5, 1.5, 4.5, 220, 180, "cup", [
            {"description": "1 cup (180g)", "grams": 180},
        ], ["marathi tomato soup", "tomato saaru"], "Maharashtrian", image_key="tomato"),
        F("kothimbir-vadi-steamed", "Steamed Kothimbir Vadi", "Snacks", "Coriander leaves and gram flour savory cakes steamed and sliced", 170, 7.5, 22.0, 5.5, 4.0, 1.2, 280, 80, "serving (4 pieces)", [
            {"description": "4 pieces (80g)", "grams": 80},
        ], ["steamed coriander cakes"], "Maharashtrian"),
        F("kothimbir-vadi-fried", "Fried Kothimbir Vadi", "Snacks", "Crispy deep-fried coriander and besan squares", 295, 6.8, 24.0, 19.0, 3.5, 1.2, 320, 80, "serving (4 pieces)", [
            {"description": "4 pieces (80g)", "grams": 80},
        ], ["crispy kothimbir vadi"], "Maharashtrian"),
        F("alu-vadi-patra", "Alu Vadi (Patra / Colocasia roll)", "Snacks", "Colocasia leaves layered with spiced sweet-tangy besan paste, rolled and sliced", 195, 5.5, 26.0, 7.8, 4.2, 5.5, 290, 80, "serving (4 pieces)", [
            {"description": "4 pieces (80g)", "grams": 80},
        ], ["patra", "colocasia leaf roll", "alu chi vadi"], "Maharashtrian"),
        F("dadpe-pohe", "Dadpe Pohe", "Breakfast", "Raw thin poha soaked in coconut water with onions, grated coconut, lemon, tadka", 185, 3.5, 30.0, 5.8, 2.2, 2.5, 180, 120, "plate", [
            {"description": "1 plate (120g)", "grams": 120},
        ], ["raw poha", "kacche pohe"], "Maharashtrian"),
        F("tarri-poha", "Nagpur Tarri Poha", "Breakfast", "Kanda poha topped with spicy black chana gravy and sev", 220, 5.8, 34.0, 6.8, 4.2, 2.0, 360, 220, "plate", [
            {"description": "1 plate (220g)", "grams": 220},
        ], ["nagpur poha", "chana tarri poha"], "Maharashtrian"),
        F("methi-bhaji-marathi", "Methi chi Bhaji (Stir-fried fenugreek)", "Curries", "Fresh fenugreek leaves stir-fried with soaked moong dal, garlic, green chili", 95, 4.2, 8.5, 4.8, 4.5, 0.8, 180, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["fenugreek stir fry", "methi moong bhaji"], "Maharashtrian"),
        F("palak-bhaji-marathi", "Palak chi Patal Bhaji", "Curries", "Spinach and chana dal simmered with ground peanuts, gram flour, tamarind", 110, 4.5, 9.5, 6.0, 3.8, 2.0, 210, 150, "katori", None, ["palak patal bhaji", "spinach dal"], "Maharashtrian", image_key="spinach"),
        F("ghevda-bhaji", "Ghevda chi Bhaji (Flat beans)", "Curries", "Flat beans cooked with onions, goda masala and toasted peanut powder", 105, 3.2, 11.0, 5.2, 4.0, 2.0, 190, 130, "katori", None, ["flat beans sabzi", "vaal papdi"], "Maharashtrian"),
        F("dodka-bhaji", "Dodka chi Bhaji (Ridge gourd)", "Curries", "Ridge gourd cooked with chana dal and crushed peanuts", 80, 2.2, 8.5, 4.2, 2.8, 2.2, 170, 140, "katori", None, ["ridge gourd marathi"], "Maharashtrian"),
        F("padwal-bhaji", "Padwal chi Bhaji (Snake gourd)", "Curries", "Snake gourd cooked with soaked chana dal, mustard and fresh coconut", 75, 2.5, 7.5, 3.8, 2.4, 1.8, 160, 140, "katori", None, ["snake gourd sabzi"], "Maharashtrian"),
        F("bharli-vangi", "Bharli Vangi (Stuffed baby brinjals)", "Curries", "Baby eggplants stuffed with roasted peanuts, sesame, goda masala and coconut", 175, 4.2, 14.0, 11.5, 5.2, 2.8, 260, 160, "serving (2 baby brinjals)", [
            {"description": "2 brinjals with gravy (160g)", "grams": 160},
        ], ["stuffed eggplant", "marathi vangi"], "Maharashtrian"),
        F("shankarpali-sweet", "Sweet Shankarpali", "Sweets", "Crisp diamond-cut sweet fried biscuits made of flour, semolina, sugar, ghee", 475, 6.5, 64.0, 21.5, 1.8, 28.0, 60, 40, "handful", [
            {"description": "1 handful (40g)", "grams": 40},
        ], ["shakarpara", "sweet diamond cuts"], "Diwali Snacks"),
        F("shankarpali-salted", "Namkeen Shankarpali (Tukdi)", "Snacks", "Savory spiced fried flour diamond biscuits with carom seeds", 460, 8.2, 58.0, 22.0, 2.5, 1.0, 480, 40, "handful", None, ["namak para", "tukdi"], "Diwali Snacks"),
        F("chirote", "Chirote (Flaky pastry)", "Sweets", "Multi-layered crispy fried flour pastry dusted with powdered sugar", 490, 5.0, 62.0, 24.5, 1.2, 26.0, 40, 40, "piece", None, ["maharashtrian chirote"], "Diwali Snacks"),
        F("karanji-gujiya", "Karanji (Gujiya)", "Sweets", "Crisp turnover stuffed with desiccated coconut, khoya, poppy seeds and sugar", 420, 6.2, 54.0, 19.8, 3.0, 28.0, 80, 45, "piece", [
            {"description": "1 karanji (45g)", "grams": 45},
            {"description": "2 karanjis (90g)", "grams": 90},
        ], ["gujiya", "coconut turnover"], "Diwali Snacks"),
        F("basundi", "Basundi (Cardamom nut flavored)", "Sweets", "Thickened sweetened whole milk reduced with cardamom, nutmeg, pistachios", 215, 6.8, 24.0, 10.5, 0.4, 22.0, 85, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["rabri marathi style", "condensed milk dessert"], "Maharashtrian"),
        F("kharvas", "Kharvas (Colostrum milk pudding)", "Sweets", "Steamed pudding made from cow/buffalo colostrum milk with saffron and nutmeg", 185, 8.5, 18.0, 8.8, 0, 16.5, 75, 80, "square slice", [
            {"description": "1 slice (80g)", "grams": 80},
        ], ["bari", "junnu", "posu", "colostrum cake"], "Maharashtrian"),
        F("shengdana-chikki", "Peanut Chikki (Shengdana chikki)", "Sweets", "Crisp brittle made of roasted peanuts and jaggery", 520, 14.5, 52.0, 28.0, 4.5, 42.0, 85, 30, "bar / square", [
            {"description": "1 piece (30g)", "grams": 30},
        ], ["groundnut chikki", "peanut brittle"], "Traditional Sweets"),
        F("tilgul-ladoo", "Tilgul Ladoo (Sesame jaggery)", "Sweets", "Toasted white sesame seeds and peanuts bound with warm jaggery syrup", 495, 12.0, 54.0, 26.0, 6.5, 44.0, 40, 30, "ladoo", [
            {"description": "1 ladoo (30g)", "grams": 30},
        ], ["til ladoo", "makar sankranti ladoo"], "Ladoos"),
    ])

    # =========================================================================
    # MORE NORTH INDIAN & SPECIALTY CURRIES (~50 items)
    # =========================================================================
    items.extend([
        F("paneer-lababdar", "Paneer Lababdar", "Curries", "Paneer cubes and grated paneer in rich spiced onion-tomato cashew gravy", 230, 8.5, 9.5, 18.0, 2.0, 3.5, 320, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["lababdar paneer"], "Paneer Dishes", image_key="paneer"),
        F("paneer-pasanda", "Paneer Pasanda", "Curries", "Stuffed shallow-fried paneer sandwiches in smooth aromatic cashew gravy", 245, 9.0, 11.0, 18.5, 2.0, 4.0, 340, 200, "bowl", None, ["stuffed paneer curry"], "Paneer Dishes", image_key="paneer"),
        F("soya-chaap-curry", "Soya Chaap Masala", "Curries", "Textured soybean flour skewers cooked in rich spicy Punjabi gravy", 195, 14.0, 15.0, 8.8, 4.5, 2.5, 360, 200, "bowl", [
            {"description": "1 bowl with chaap pieces (200g)", "grams": 200},
        ], ["soya chaap", "veg chaap curry"], "Soy"),
        F("soya-chaap-malai", "Malai Soya Chaap (Tandoori)", "Snacks", "Roasted soya chaap tossed in heavy cream, hung curd, black pepper and butter", 260, 13.5, 12.0, 17.5, 3.2, 2.0, 380, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["tandoori malai chaap"], "Soy"),
        F("bhindi-do-pyaza", "Bhindi Do Pyaza", "Curries", "Okra cooked with double the onions in crunchy and caramelized forms", 125, 2.8, 14.0, 6.5, 3.8, 3.5, 240, 150, "katori", None, ["okra onion curry"], "Dry Sabzi"),
        F("aloo-shimla-mirch", "Aloo Shimla Mirch", "Curries", "Diced potatoes and crunchy green bell peppers stir-fried with cumin", 115, 2.0, 16.0, 5.0, 2.8, 2.0, 220, 150, "katori", None, ["potato capsicum sabzi"], "Dry Sabzi", image_key="potato"),
        F("arbi-masala-fry", "Arbi Masala (Crispy taro fry)", "Curries", "Boiled colocasia tubers pan-fried crisp with carom seeds and amchur", 155, 2.2, 24.0, 5.8, 3.8, 1.0, 210, 130, "katori", [
            {"description": "1 katori (130g)", "grams": 130},
        ], ["arbi fry", "taro root masala", "ghuiya fry"], "Dry Sabzi"),
        F("lauki-chana-dal", "Lauki Chana Dal", "Curries", "Bottle gourd and split Bengal gram simmered together with mild spices", 95, 4.5, 14.0, 2.5, 3.5, 2.2, 190, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["ghiya chana dal", "dudhi chana dal"], "Curries"),
        F("tindora-fry", "Tindora Fry (Ivy gourd)", "Curries", "Sliced ivy gourd sautéed with mustard, cumin and red chili powder", 100, 2.2, 10.0, 5.8, 3.2, 2.0, 190, 120, "katori", None, ["kundru fry", "tendli bhaji"], "Dry Sabzi"),
        F("mushroom-matar", "Mushroom Matar (Curry)", "Curries", "Button mushrooms and green peas in rich spiced onion-tomato gravy", 110, 4.2, 12.0, 5.0, 3.0, 2.8, 260, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["matar mushroom"], "Curries"),
        F("mushroom-do-pyaza", "Mushroom Do Pyaza", "Curries", "Fresh mushrooms simmered with onions, capsicum, tomatoes and spices", 120, 3.8, 11.0, 6.8, 2.5, 3.2, 270, 180, "katori", None, ["spicy mushroom curry"], "Curries"),
        F("litti-chokha", "Litti Chokha (2 littis + chokha)", "Grains", "Whole wheat balls stuffed with spiced sattu baked over coals, with roasted brinjal mash", 220, 7.5, 36.0, 5.5, 5.2, 1.8, 380, 220, "serving", [
            {"description": "1 serving (2 littis + chokha, 220g)", "grams": 220},
        ], ["bihari litti chokha", "sattu litti"], "Regional Breads"),
        F("missi-roti", "Missi Roti (Gram flour flatbread)", "Bread", "Whole wheat and besan flour bread seasoned with onions, ajwain and kasuri methi", 265, 9.8, 44.0, 5.5, 6.2, 1.5, 240, 50, "piece", [
            {"description": "1 missi roti (50g)", "grams": 50},
            {"description": "2 missi rotis (100g)", "grams": 100},
        ], ["rajasthani missi roti", "besan roti"], "Breads"),
        F("makki-di-roti", "Makki di Roti", "Bread", "Cornmeal yellow flatbread cooked on tawa with desi ghee", 260, 6.5, 48.0, 5.0, 6.0, 1.2, 120, 60, "piece", [
            {"description": "1 makki roti (60g)", "grams": 60},
        ], ["makki ki roti", "punjabi corn bread"], "Breads"),
    ])

    # =========================================================================
    # MORE SOUTH INDIAN DISHES (~40 items)
    # =========================================================================
    items.extend([
        F("ven-pongal", "Ven Pongal (Ghee Pongal)", "Breakfast", "Rice and yellow moong dal cooked soft, tempered with black pepper, cumin, ginger, cashews, ghee", 185, 4.8, 26.0, 7.0, 2.0, 0.5, 210, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["khara pongal", "ghee pongal", "ven pongal"], "South Indian"),
        F("sweet-pongal", "Sweet Pongal (Sakkarai Pongal)", "Sweets", "Rice and moong dal simmered in jaggery syrup with cardamom, cashews and ghee", 255, 3.8, 48.0, 5.8, 1.8, 32.0, 45, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["sakkarai pongal", "chakkara pongal"], "South Indian"),
        F("bisi-bele-bath", "Bisi Bele Bath", "Grains", "Karnataka spicy rice, toor dal and vegetable dish flavored with bisi bele masala and ghee", 165, 4.8, 26.0, 4.8, 3.5, 1.8, 290, 250, "plate", [
            {"description": "1 plate (250g)", "grams": 250},
        ], ["sambar rice", "bisi bele huliyanna"], "South Indian"),
        F("vangi-bath", "Vangi Bath (Brinjal rice)", "Grains", "Rice cooked with spiced brinjal slices and special vangi bath spice powder", 170, 3.5, 29.0, 4.5, 2.5, 1.5, 240, 200, "plate", None, ["brinjal rice", "eggplant rice"], "South Indian"),
        F("adai-dosa", "Adai (Mixed lentil pancake)", "Breakfast", "Thick pancake made of soaked rice, toor, chana, urad and moong dals with red chilies", 195, 8.5, 30.0, 4.5, 4.8, 0.8, 190, 100, "piece", [
            {"description": "1 adai (100g)", "grams": 100},
        ], ["adai dosa", "multigrain lentil dosa"], "South Indian"),
        F("podi-dosa", "Podi Dosa (Gunpowder dosa)", "Breakfast", "Crisp dosa sprinkled with spicy roasted lentil-chili podi and ghee", 230, 5.0, 32.0, 9.5, 2.5, 0.8, 280, 100, "piece", [
            {"description": "1 podi dosa (100g)", "grams": 100},
        ], ["gunpowder dosa", "ghee podi dosa"], "South Indian", image_key="dosa"),
        F("avial", "Kerala Avial", "Curries", "Mixed vegetables (raw banana, drumstick, carrot, yam) cooked in grated coconut curd paste", 130, 2.8, 11.0, 8.2, 3.5, 3.2, 190, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["aviyal", "kerala vegetable avial"], "South Indian"),
        F("mor-kulambu", "Mor Kulambu (Buttermilk curry)", "Curries", "South Indian spiced yogurt and coconut gravy with ash gourd or okra", 85, 2.8, 6.5, 5.2, 1.2, 2.8, 240, 180, "bowl", None, ["more kuzhambu", "curd curry south"], "South Indian"),
        F("vatha-kulambu", "Vatha Kulambu", "Curries", "Tangy and spicy tamarind gravy with sundried turkey berries (sundakkai) or shallots", 115, 2.0, 15.0, 5.5, 3.0, 4.2, 360, 150, "katori", None, ["vathal kuzhambu", "kara kulambu"], "South Indian"),
        F("mangalore-buns", "Mangalore Buns (Banana puris)", "Breakfast", "Mildly sweet deep-fried puffed puris made of fermented banana, maida and curd", 340, 5.5, 48.0, 14.5, 2.0, 12.0, 140, 60, "piece", [
            {"description": "1 bun (60g)", "grams": 60},
            {"description": "2 buns (120g)", "grams": 120},
        ], ["banana buns", "mangalore puri"], "South Indian"),
        F("mysore-bonda", "Mysore Bonda", "Snacks", "Golden crispy deep-fried maida and curd fritters flavored with ginger, cumin, green chili", 310, 6.0, 36.0, 16.0, 1.8, 1.5, 280, 50, "piece", [
            {"description": "1 bonda (50g)", "grams": 50},
            {"description": "2 bondas (100g)", "grams": 100},
        ], ["mysore bajji", "maida bonda"], "South Indian"),
        F("chettinad-chicken", "Chettinad Chicken Curry", "Meat", "Chicken pieces in fiery roasted spice paste with black pepper, fennel, star anise, coconut", 195, 18.5, 4.0, 11.5, 1.5, 1.0, 340, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["chicken chettinad", "pepper chicken gravy"], "South Indian"),
        F("chicken-sukka-kori", "Kori Sukka (Mangalore chicken)", "Meat", "Dry-roasted chicken tossed with freshly grated coconut, whole red chilies, curry leaves", 235, 22.0, 4.5, 14.5, 2.0, 0.8, 350, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["chicken sukka", "mangalore kori sukka"], "South Indian"),
    ])

    # =========================================================================
    # BENGALI & EAST INDIAN DISHES (~35 items)
    # =========================================================================
    items.extend([
        F("aloo-posto", "Aloo Posto (Potatoes in poppy seed paste)", "Curries", "Diced potatoes simmered in rich creamy poppy seed paste with mustard oil", 175, 4.5, 21.0, 8.5, 3.2, 1.0, 210, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["potato posto", "bengali aloo posto"], "Bengali", image_key="potato"),
        F("chholar-dal", "Chholar Dal (Bengal gram with coconut)", "Pulses", "Chana dal simmered with ghee, ginger, hing, whole spices, fried coconut bits", 165, 8.2, 22.0, 5.2, 5.0, 3.5, 220, 160, "katori", [
            {"description": "1 katori (160g)", "grams": 160},
        ], ["bengali chana dal", "narkel chholar dal"], "Bengali"),
        F("shukto", "Bengali Shukto", "Curries", "Traditional bittersweet stew of bitter gourd, raw banana, drumstick, bori in milk-ginger paste", 95, 2.8, 12.0, 3.8, 3.0, 3.0, 190, 180, "bowl", None, ["bengali mixed veg stew"], "Bengali"),
        F("dhokar-dalna", "Dhokar Dalna (Lentil cake curry)", "Curries", "Steamed and fried chana dal cakes simmered in fragrant ginger-cumin gravy", 185, 7.5, 20.0, 8.5, 3.8, 2.0, 290, 180, "bowl", [
            {"description": "1 bowl with 2 dhokas (180g)", "grams": 180},
        ], ["lentil cake curry"], "Bengali"),
        F("macher-jhol", "Macher Jhol (Rohu / Katla fish curry)", "Meat", "Freshwater fish cooked in light turmeric, cumin and ginger gravy with potatoes", 145, 15.5, 5.0, 7.2, 1.0, 0.8, 260, 200, "bowl", [
            {"description": "1 bowl with 1 fish piece (200g)", "grams": 200},
        ], ["bengali fish curry", "rohu jhol"], "Bengali"),
        F("chingri-malai-curry", "Chingri Malai Curry (Prawn coconut curry)", "Meat", "Jumbo prawns cooked in aromatic coconut milk and garam masala gravy", 190, 15.0, 6.0, 12.0, 1.2, 2.8, 310, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["prawn malai curry", "golda chingri malai"], "Bengali"),
        F("kosha-mangsho", "Kosha Mangsho (Bengali slow-cooked mutton)", "Meat", "Rich, dark, intensely roasted goat meat curry with onions, garlic and yogurt", 260, 18.5, 5.5, 18.5, 1.2, 1.5, 360, 200, "bowl", [
            {"description": "1 bowl with mutton pieces (200g)", "grams": 200},
        ], ["bengali mutton kosha"], "Bengali"),
        F("begun-bhaja", "Begun Bhaja (Fried eggplant rounds)", "Curries", "Round slices of eggplant marinated in turmeric and salt, shallow-fried in mustard oil", 160, 2.0, 12.0, 11.5, 3.8, 3.2, 240, 100, "serving (2 rounds)", [
            {"description": "2 fried eggplant slices (100g)", "grams": 100},
        ], ["baingan bhaja", "fried brinjal"], "Bengali"),
        F("mishti-doi", "Mishti Doi (Sweetened baked yogurt)", "Sweets", "Fermented caramelized milk dessert set in earthen clay pots", 155, 4.5, 23.0, 4.8, 0, 22.0, 55, 100, "earthen pot", [
            {"description": "1 small pot (100g)", "grams": 100},
        ], ["sweet curd", "bengali sweet yogurt"], "Bengali"),
        F("sandesh-plain", "Sandesh (Kanchagolla / Plain)", "Sweets", "Delicate fresh chhena dessert kneaded with fine sugar and cardamom", 260, 9.5, 36.0, 8.5, 0.2, 34.0, 40, 35, "piece", [
            {"description": "1 sandesh (35g)", "grams": 35},
            {"description": "2 pieces (70g)", "grams": 70},
        ], ["bengali sandesh", "chhena sandesh"], "Bengali"),
        F("cham-cham", "Cham Cham (Chum Chum)", "Sweets", "Oblong poached chhena sweet cooked in sugar syrup, rolled in mawa / coconut", 295, 5.5, 52.0, 7.5, 0.5, 46.0, 60, 50, "piece", None, ["chum chum sweet"], "Bengali"),
    ])

    # =========================================================================
    # GUJARATI REGIONAL DISHES (~25 items)
    # =========================================================================
    items.extend([
        F("sev-tameta-shaak", "Sev Tameta nu Shaak", "Curries", "Sweet and tangy tomato curry topped with crunchy gram flour sev", 185, 4.2, 18.0, 10.8, 2.5, 6.5, 340, 160, "katori", [
            {"description": "1 katori (160g)", "grams": 160},
        ], ["sev tomato curry", "gujarati sev tamatar"], "Gujarati", image_key="tomato"),
        F("undhiyu", "Surti Undhiyu", "Curries", "Slow-cooked mixed winter vegetables (surti papdi, yam, baby brinjals, muthia) in green masala", 195, 5.2, 22.0, 9.8, 5.5, 3.8, 290, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["gujarati undhiyu"], "Gujarati"),
        F("dal-dhokli", "Dal Dhokli", "Grains", "Whole wheat spiced pasta squares simmered in sweet-sour Gujarati toor dal", 155, 5.5, 26.0, 3.5, 3.2, 4.5, 240, 220, "bowl", [
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["gujarati dal dhokli", "varan phal"], "Gujarati"),
        F("handvo", "Handvo (Savory baked lentil cake)", "Breakfast", "Fermented rice, chana, toor, urad dal batter with grated bottle gourd, sesame tadka", 210, 7.8, 30.0, 6.8, 4.2, 2.5, 310, 100, "slice", [
            {"description": "1 slice (100g)", "grams": 100},
        ], ["gujarati handvo", "baked dal cake"], "Gujarati"),
        F("muthia-steamed", "Methi Muthia (Steamed)", "Snacks", "Steamed dumplings made of fresh fenugreek leaves, whole wheat flour, besan, spices", 180, 6.2, 28.0, 4.8, 4.0, 2.5, 280, 80, "serving (4 pieces)", [
            {"description": "4 pieces (80g)", "grams": 80},
        ], ["steamed muthia"], "Gujarati"),
    ])

    return items

print("Catalogue part 5 loaded.")
