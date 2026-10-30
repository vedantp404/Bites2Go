"""
Catalogue data part 8: Comprehensive regional dishes, sweets, beverages, condiments, and global staples (~350 items).
"""

from scripts.build_full_database import F

def get_part8():
    items = []

    # =========================================================================
    # INDIAN REGIONAL DISHES, CURRIES & SIDES (~90 items)
    # =========================================================================
    items.extend([
        F("veg-kolhapuri", "Vegetable Kolhapuri", "Curries", "Mixed vegetables in spicy thick Kolhapuri red chili and dry coconut gravy", 175, 4.2, 14.0, 11.5, 3.8, 2.5, 340, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["veg kolhapuri", "spicy veg curry"], "Curries"),
        F("veg-jalfrezi", "Vegetable Jalfrezi", "Curries", "Stir-fried capsicum, baby corn, carrots, beans in sweet and tangy tomato-onion sauce", 130, 3.0, 16.0, 6.0, 3.5, 4.5, 290, 180, "bowl", None, ["jalfrezi"], "Curries"),
        F("veg-handi", "Vegetable Handi", "Curries", "Mixed vegetables simmered in clay pot with cashew and onion gravy", 165, 3.8, 13.0, 10.8, 3.2, 3.0, 310, 200, "bowl", None, ["handi veg"], "Curries"),
        F("veg-makhani", "Vegetable Makhani", "Curries", "Assorted vegetables cooked in buttery creamy tomato sauce", 170, 3.5, 12.5, 11.8, 3.0, 4.2, 330, 200, "bowl", None, ["veg makhanwala"], "Curries"),
        F("corn-palak", "Corn Palak", "Curries", "Sweet corn kernels simmered in seasoned vibrant spinach puree", 135, 4.5, 16.0, 6.2, 3.5, 2.8, 260, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["palak corn", "makai palak"], "Curries", image_key="spinach"),
        F("methi-paneer", "Methi Paneer", "Curries", "Fresh fenugreek leaves and paneer cubes cooked in onion-tomato masala", 185, 9.5, 8.0, 13.0, 2.8, 2.0, 290, 180, "bowl", None, ["fenugreek paneer"], "Paneer Dishes", image_key="paneer"),
        F("tawa-paneer", "Tawa Paneer Masala", "Curries", "Semi-dry marinated paneer cubes cooked on flat tawa with bell peppers", 205, 11.0, 9.0, 14.5, 2.2, 2.5, 320, 180, "bowl", None, ["tawa paneer"], "Paneer Dishes", image_key="paneer"),
        F("dal-palak", "Dal Palak (Lentils with spinach)", "Pulses", "Yellow moong and toor lentils simmered with chopped fresh spinach leaves", 115, 6.5, 16.0, 2.8, 4.2, 1.0, 210, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["spinach dal", "palak dal"], "Dals", image_key="dal"),
        F("dal-methi", "Dal Methi", "Pulses", "Yellow lentils cooked with fresh bitter fenugreek leaves and garlic tadka", 120, 6.8, 16.5, 3.2, 4.0, 0.8, 220, 180, "bowl", None, ["fenugreek dal"], "Dals", image_key="dal"),
        F("sindhi-kadhi", "Sindhi Kadhi", "Curries", "Tangy gram flour and tamarind soup loaded with drumsticks, okra, cluster beans", 95, 3.2, 13.0, 3.5, 3.2, 3.5, 260, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["sindhi besan kadhi"], "Kadhi"),
        F("poriyal-beans", "Beans Poriyal", "Curries", "Finely chopped french beans sautéed with mustard seeds, curry leaves, grated coconut", 95, 3.0, 10.5, 4.8, 3.5, 1.8, 190, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["green beans poriyal", "south indian beans"], "South Indian"),
        F("poriyal-cabbage", "Cabbage Poriyal", "Curries", "Shredded cabbage stir-fried with split urad dal, mustard and coconut", 80, 2.2, 8.5, 4.2, 2.8, 2.5, 180, 120, "katori", None, ["muttaikose poriyal"], "South Indian"),
        F("kootu-cabbage", "Cabbage Kootu", "Pulses", "Cabbage and chana dal simmered in ground coconut cumin paste", 105, 4.5, 12.0, 4.5, 3.8, 2.0, 210, 160, "katori", [
            {"description": "1 katori (160g)", "grams": 160},
        ], ["south indian kootu", "dal kootu"], "South Indian"),
        F("thoran-beans", "Kerala Beans Thoran", "Curries", "French beans stir-fried with turmeric, shallots, green chili and fresh coconut", 100, 3.2, 11.0, 5.0, 3.8, 2.0, 190, 130, "katori", [
            {"description": "1 katori (130g)", "grams": 130},
        ], ["beans thoran", "kerala thoran"], "South Indian"),
        F("olan-kerala", "Kerala Olan", "Curries", "Ash gourd and black-eyed cowpeas simmered in delicate coconut milk with curry leaves", 110, 2.8, 10.0, 6.8, 2.5, 1.8, 160, 160, "bowl", [
            {"description": "1 bowl (160g)", "grams": 160},
        ], ["olan", "sadya olan"], "South Indian"),
        F("erissery-pumpkin", "Pumpkin Erissery", "Curries", "Yellow pumpkin and cowpeas cooked in roasted coconut paste with mustard tadka", 125, 3.2, 14.0, 6.2, 3.5, 3.5, 180, 160, "bowl", None, ["mathanga erissery"], "South Indian"),
        F("malabar-parotta", "Kerala Malabar Parotta", "Bread", "Flaky layered spiral flatbread made of refined flour and ghee, pan-fried", 360, 6.5, 48.0, 16.0, 2.0, 2.5, 340, 80, "piece", [
            {"description": "1 parotta (80g)", "grams": 80},
            {"description": "2 parottas (160g)", "grams": 160},
        ], ["kerala parotta", "malabar parotta"], "South Indian Breads"),
        F("idiyappam", "Idiyappam (String hoppers)", "Breakfast", "Steamed delicate rice noodle nests", 135, 2.6, 29.5, 0.5, 1.0, 0.2, 85, 80, "piece (2 idiyappams)", [
            {"description": "2 string hoppers (80g)", "grams": 80},
            {"description": "3 string hoppers (120g)", "grams": 120},
        ], ["string hoppers", "noolappam", "sevai"], "South Indian"),
        F("kadala-curry", "Kadala Curry (Black chickpea curry)", "Pulses", "Black chickpeas in spicy roasted coconut gravy for puttu/appam", 165, 7.8, 21.0, 5.8, 6.5, 1.8, 290, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["kerala kadala curry"], "South Indian"),
        F("veg-stew-kerala", "Kerala Vegetable Stew", "Curries", "Potatoes, carrots, beans simmered in spiced fragrant coconut milk with black pepper", 125, 2.2, 12.0, 7.8, 2.5, 2.2, 210, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["ishtew", "coconut veg stew"], "South Indian"),
        F("chicken-stew-kerala", "Kerala Chicken Stew", "Meat", "Tender chicken pieces simmered in coconut milk with potatoes and whole spices", 175, 14.5, 6.5, 10.5, 1.2, 1.5, 270, 220, "bowl", [
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["kerala chicken stew", "appam stew"], "South Indian"),
        F("ghee-rice-nei-choru", "Nei Choru (Kerala Ghee Rice)", "Grains", "Kaima / Jeerakasala rice cooked in pure ghee with fried cashews, raisins, onions", 195, 3.5, 34.0, 5.5, 0.8, 1.0, 210, 180, "plate", [
            {"description": "1 plate (180g)", "grams": 180},
        ], ["ghee rice", "nei choru", "malabar ghee rice"], "Rice Dishes"),
        F("thalassery-biryani", "Thalassery Chicken Biryani", "Grains", "Malabar dum biryani using aromatic Kaima rice with mild spices and fried onions", 215, 13.0, 26.0, 6.8, 1.2, 1.0, 310, 300, "plate", [
            {"description": "1 plate (300g)", "grams": 300},
        ], ["malabar biryani", "thalassery biryani"], "Rice Dishes"),
        F("meen-pollichathu", "Meen Pollichathu (Pearl spot in banana leaf)", "Meat", "Fish marinated in shallot-chili paste, wrapped in banana leaf and pan-roasted", 185, 18.0, 3.5, 11.0, 1.0, 0.5, 290, 150, "wrapped fish", [
            {"description": "1 wrapped fish (150g)", "grams": 150},
        ], ["karimeen pollichathu", "banana leaf fish"], "Seafood"),
        F("kerala-fish-fry", "Kerala Fish Fry (Ayala / Mackerel)", "Meat", "Fish steaks coated with red chili, turmeric and curry leaf paste, shallow-fried", 220, 20.0, 2.5, 14.5, 0.5, 0, 310, 120, "fish steak", None, ["ayala fry", "tawa fish fry south"], "Seafood"),
    ])

    # =========================================================================
    # INDIAN BAKERY, FARSAN, CHIVDA & SNACKS (~80 items)
    # =========================================================================
    items.extend([
        F("poha-chivda", "Poha Chivda (Roasted poha snack)", "Snacks", "Roasted thin poha tossed with peanuts, roasted chana dal, curry leaves, turmeric", 460, 8.5, 68.0, 17.5, 4.5, 3.5, 340, 30, "katori / handful", [
            {"description": "1 handful (30g)", "grams": 30},
            {"description": "1 katori (50g)", "grams": 50},
        ], ["patla poha chivda", "roasted chivda"], "Farsan"),
        F("cornflakes-chivda", "Cornflakes Chivda", "Snacks", "Fried yellow cornflakes seasoned with peanuts, raisins, sugar, chili", 495, 6.2, 64.0, 24.0, 3.8, 8.5, 380, 30, "handful", [
            {"description": "1 handful (30g)", "grams": 30},
        ], ["makai chivda"], "Farsan"),
        F("murmura-bhadang", "Bhadang (Spicy puffed rice chivda)", "Snacks", "Kolhapuri spiced puffed rice with garlic, peanuts and red chili", 410, 7.5, 66.0, 13.5, 3.5, 2.0, 420, 40, "cup", [
            {"description": "1 cup (40g)", "grams": 40},
        ], ["kolhapuri bhadang", "spicy puffed rice"], "Farsan"),
        F("sev-nylon", "Nylon Sev (Thin chickpea noodles)", "Snacks", "Extra-fine deep-fried gram flour vermicelli for chaat toppings", 545, 9.5, 52.0, 33.5, 4.2, 1.2, 480, 20, "tablespoon / topping", [
            {"description": "2 tbsp (20g)", "grams": 20},
            {"description": "1 small katori (40g)", "grams": 40},
        ], ["nylon sev", "chaat sev", "barik sev"], "Farsan"),
        F("sev-ratlami", "Ratlami Sev (Spicy clove flavored)", "Snacks", "Thick gram flour sev seasoned with crushed cloves, black pepper, ajwain", 560, 11.0, 48.0, 36.0, 4.8, 1.0, 540, 30, "handful", [
            {"description": "1 handful (30g)", "grams": 30},
        ], ["ratlami sev", "laung sev"], "Farsan"),
        F("aloo-bhujia", "Aloo Bhujia (Haldiram style)", "Snacks", "Crispy spiced potato and gram flour extruded noodles with mint and spices", 572, 8.5, 45.0, 39.5, 4.0, 2.2, 590, 30, "serving", [
            {"description": "1 small pack (35g)", "grams": 35},
        ], ["haldiram aloo bhujia", "potato bhujia"], "Farsan"),
        F("bikaneri-bhujia", "Bikaneri Bhujia (Moth bean sev)", "Snacks", "Crispy spiced moth bean and besan sev from Bikaner", 580, 12.5, 44.0, 40.0, 5.0, 1.5, 620, 30, "serving", None, ["bikaner bhujia"], "Farsan"),
        F("chakli-bhajani", "Bhajani Chakli", "Snacks", "Crispy spiral snack made of roasted multigrain flour with sesame and ajwain", 485, 9.5, 58.0, 24.5, 5.2, 1.2, 380, 30, "piece (2 chaklis)", [
            {"description": "2 chaklis (30g)", "grams": 30},
            {"description": "4 chaklis (60g)", "grams": 60},
        ], ["maharashtrian chakli", "bhajanichi chakli"], "Farsan"),
        F("murukku-butter", "Butter Murukku", "Snacks", "Crispy South Indian spiral snack made of rice flour, fried gram and butter", 510, 8.0, 60.0, 27.0, 3.5, 0.8, 360, 30, "serving", [
            {"description": "1 serving (30g)", "grams": 30},
        ], ["butter murukku", "benne murukku"], "Farsan"),
        F("mathri-punjabi", "Punjabi Mathri (Flaky cracker)", "Snacks", "Flaky deep-fried flour crackers seasoned with ajwain, black pepper, kasuri methi", 515, 8.2, 54.0, 30.0, 2.8, 0.8, 410, 35, "cracker", [
            {"description": "1 mathri (35g)", "grams": 35},
            {"description": "2 mathris (70g)", "grams": 70},
        ], ["methi mathri", "khasta mathri"], "Farsan"),
        F("khari-biscuit", "Khari Biscuit (Puff pastry biscuit)", "Snacks", "Flaky, light, layered salted puff pastry biscuit", 520, 7.5, 54.0, 31.0, 2.0, 1.5, 390, 20, "biscuit", [
            {"description": "1 khari (20g)", "grams": 20},
            {"description": "2 kharis (40g)", "grams": 40},
        ], ["puff biscuit", "saloni khari"], "Bakery"),
        F("suji-rusk", "Suji Rusk (Crisp toast biscuit)", "Snacks", "Twice-baked sweetened semolina toast with cardamom/fennel", 415, 8.5, 76.0, 8.5, 2.5, 22.0, 190, 15, "rusk piece", [
            {"description": "1 rusk (15g)", "grams": 15},
            {"description": "2 rusks (30g)", "grams": 30},
        ], ["rusk", "tea toast", "suji toast"], "Bakery"),
        F("bun-maska", "Bun Maska", "Breakfast", "Soft sweet bakery bun sliced and generously slathered with salted butter", 340, 7.5, 48.0, 13.5, 2.0, 6.5, 360, 100, "bun", [
            {"description": "1 bun maska (100g)", "grams": 100},
        ], ["irani bun maska"], "Bakery"),
        F("nankhatai", "Nankhatai (Indian shortbread cookie)", "Sweets", "Traditional cardamom spiced crumbly shortbread made of flour, besan, ghee", 495, 6.2, 62.0, 25.0, 1.8, 28.0, 95, 25, "cookie", [
            {"description": "1 nankhatai (25g)", "grams": 25},
            {"description": "2 nankhatais (50g)", "grams": 50},
        ], ["indian shortbread"], "Bakery"),
        F("veg-puff", "Vegetable Puff / Patties", "Snacks", "Flaky golden puff pastry filled with spiced diced potatoes, carrots and peas", 310, 5.2, 34.0, 17.0, 2.8, 2.0, 420, 110, "puff", [
            {"description": "1 veg puff (110g)", "grams": 110},
        ], ["veg patties", "curry puff"], "Bakery"),
        F("paneer-puff", "Paneer Puff / Patties", "Snacks", "Flaky puff pastry stuffed with spicy crumbled paneer bhurji", 335, 8.5, 32.0, 19.5, 2.2, 2.2, 440, 120, "puff", [
            {"description": "1 paneer puff (120g)", "grams": 120},
        ], ["paneer patties"], "Bakery", image_key="paneer"),
        F("egg-puff", "Egg Puff (Kerala / South bakery)", "Snacks", "Flaky puff pastry enclosing half hard-boiled egg with spicy onion masala", 295, 9.8, 28.0, 16.5, 1.8, 1.8, 410, 110, "puff", [
            {"description": "1 egg puff (110g)", "grams": 110},
        ], ["egg patties", "mutta puff"], "Bakery", image_key="egg"),
        F("chicken-puff", "Chicken Puff", "Snacks", "Puff pastry stuffed with seasoned minced chicken and onions", 320, 12.5, 26.0, 18.5, 1.5, 1.5, 450, 120, "puff", [
            {"description": "1 chicken puff (120g)", "grams": 120},
        ], ["chicken patties"], "Bakery"),
        F("hara-bhara-kabab", "Hara Bhara Kabab", "Snacks", "Pan-fried patties made of spinach, green peas, potatoes, paneer with cashew on top", 195, 6.5, 22.0, 9.5, 3.8, 2.0, 290, 75, "serving (2 kababs)", [
            {"description": "2 kababs (75g)", "grams": 75},
        ], ["spinach kabab", "veg green kabab"], "Snacks", image_key="spinach"),
        F("dahi-vada", "Dahi Vada (Dahi Bhalla)", "Snacks", "Soft urad dal fritters soaked in spiced curd, topped with sweet and green chutneys", 165, 5.8, 21.0, 6.8, 1.8, 9.5, 280, 180, "plate (2 vadas)", [
            {"description": "1 plate with 2 vadas (180g)", "grams": 180},
        ], ["dahi bhalla", "dahi wada"], "Chaat"),
        F("raj-kachori", "Raj Kachori", "Snacks", "Large crisp hollow kachori stuffed with boiled potatoes, sprouted moong, curd, sev", 240, 5.5, 32.0, 10.5, 3.0, 7.5, 410, 220, "serving", [
            {"description": "1 royal kachori (220g)", "grams": 220},
        ], ["royal chaat kachori"], "Chaat"),
        F("chole-kulche", "Delhi Chole Kulche", "Fast Food", "Tangy boiled white peas (matar) with 2 soft tawa kulchas and pickled onions", 225, 7.8, 38.0, 4.8, 4.8, 2.5, 440, 250, "plate", [
            {"description": "1 plate with 2 kulchas (250g)", "grams": 250},
        ], ["matar kulcha", "delhi street food"], "Street Food"),
        F("roll-egg-chicken", "Kolkata Egg Chicken Roll", "Fast Food", "Paratha lined with egg, stuffed with spiced chicken tikka, sliced onions, lemon", 255, 14.5, 27.0, 10.5, 1.8, 2.2, 460, 200, "roll", [
            {"description": "1 roll (200g)", "grams": 200},
        ], ["egg chicken roll", "kolkata kathi roll"], "Wraps"),
    ])

    # =========================================================================
    # MORE TRADITIONAL MITHAI & HALWAS (~50 items)
    # =========================================================================
    items.extend([
        F("imarti", "Imarti (Jahangiri)", "Sweets", "Flower-shaped urad dal fried sweet soaked in rose sugar syrup", 355, 3.8, 64.0, 9.5, 0.8, 55.0, 70, 60, "piece", [
            {"description": "1 imarti (60g)", "grams": 60},
        ], ["amriti", "jangiri"], "Mithai"),
        F("balushahi", "Balushahi (Badusha)", "Sweets", "Flaky glazed flour doughnut-shaped pastry fried in ghee and dipped in sugar syrup", 440, 5.0, 58.0, 21.0, 1.2, 38.0, 65, 45, "piece", [
            {"description": "1 balushahi (45g)", "grams": 45},
        ], ["badusha", "glazed pastry sweet"], "Mithai"),
        F("rabdi", "Rabdi (Thickened milk)", "Sweets", "Layers of clotted whole milk cream simmered with saffron, cardamom and nuts", 250, 7.8, 26.0, 13.0, 0.2, 24.0, 95, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["rabri", "lacchedar rabdi"], "Mithai"),
        F("phirni-kesar", "Kesar Phirni", "Sweets", "Ground rice pudding set in earthen pots with saffron, cardamom and chopped pistachios", 155, 4.0, 24.0, 5.0, 0.4, 18.0, 48, 120, "earthen pot", [
            {"description": "1 pot (120g)", "grams": 120},
        ], ["rice phirni", "shahi phirni"], "Puddings"),
        F("shahi-tukda", "Shahi Tukda (Double ka meetha)", "Sweets", "Deep-fried bread triangles soaked in saffron syrup, coated with thick rabdi and nuts", 345, 6.5, 48.0, 14.8, 1.2, 36.0, 140, 120, "serving (2 triangles)", [
            {"description": "2 pieces with rabdi (120g)", "grams": 120},
        ], ["double ka meetha", "royal bread pudding"], "Mithai"),
        F("soan-papdi", "Soan Papdi (Flaky gram flour sweet)", "Sweets", "Crisp, flaky, fibrous melt-in-mouth sweet made of besan, flour, ghee, sugar", 490, 6.0, 64.0, 23.5, 1.5, 48.0, 30, 35, "cube", [
            {"description": "1 cube (35g)", "grams": 35},
        ], ["patisa", "sohan papdi"], "Mithai"),
        F("mysore-pak-ghee", "Ghee Mysore Pak", "Sweets", "Rich melt-in-mouth soft sweet made of roasted besan, copious ghee and sugar", 540, 5.5, 52.0, 34.5, 1.8, 46.0, 25, 35, "piece", [
            {"description": "1 piece (35g)", "grams": 35},
        ], ["mysore pak", "mysuru pakku"], "Mithai"),
        F("badam-halwa", "Badam Halwa (Almond fudge)", "Sweets", "Rich paste of blanched almonds cooked in pure ghee, saffron and sugar", 480, 11.5, 44.0, 29.5, 4.2, 38.0, 18, 50, "katori portion", [
            {"description": "1 portion (50g)", "grams": 50},
        ], ["almond halwa"], "Halwa", image_key="almonds"),
        F("moong-dal-halwa", "Moong Dal Halwa", "Sweets", "Yellow moong dal paste roasted slowly in pure desi ghee with milk, saffron, sugar", 410, 8.5, 48.0, 20.5, 3.2, 38.0, 45, 80, "katori", [
            {"description": "1 katori (80g)", "grams": 80},
        ], ["mung dal halwa"], "Halwa"),
        F("atta-halwa", "Atte ka Halwa (Kada Prashad)", "Sweets", "Whole wheat flour roasted in equal parts desi ghee and sugar syrup", 420, 5.2, 54.0, 20.8, 2.5, 42.0, 15, 80, "katori", [
            {"description": "1 katori (80g)", "grams": 80},
        ], ["kada prashad", "gehu halwa"], "Halwa"),
        F("chhena-poda", "Chhena Poda (Baked cottage cheese)", "Sweets", "Traditional Odia caramelized baked chhena cake with sugar, cardamom and cashews", 245, 10.5, 32.0, 8.5, 0.2, 28.0, 40, 80, "slice", [
            {"description": "1 slice (80g)", "grams": 80},
        ], ["odisha chhena poda"], "Mithai"),
        F("kalakand", "Kalakand", "Sweets", "Moist, grainy fresh milk cake made of paneer/chhena, reduced milk and sugar", 340, 9.8, 44.0, 14.0, 0.2, 38.0, 65, 40, "square", [
            {"description": "1 piece (40g)", "grams": 40},
        ], ["milk cake kalakand", "alwar kalakand"], "Mithai"),
        F("sheer-khurma", "Sheer Khurma", "Sweets", "Vermicelli pudding simmered in rich whole milk with dates, pistachios, chironji", 195, 4.8, 28.0, 7.2, 1.2, 22.0, 45, 150, "bowl", [
            {"description": "1 bowl (150g)", "grams": 150},
        ], ["eid sheer khurma", "vermicelli milk dessert"], "Puddings"),
    ])

    return items

print("Catalogue part 8 loaded.")
