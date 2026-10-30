"""
Catalogue data part 11: Maharashtrian dishes, North Indian curries/breads, South Indian breakfast/mains, beverages & traditional sweets (100 items).
"""

from scripts.build_full_database import F

def get_part11():
    items = []

    # =========================================================================
    # MAHARASHTRIAN & MUMBAI STREET FOOD & SPECIALTIES
    # =========================================================================
    items.extend([
        F("misal-pav-curry", "Misal pav curry with pav", "Breakfast", "Spicy sprouted moth bean curry with crunchy farsan and pav bread", 168, 5.2, 22.0, 7.0, 3.5, 2.5, 480, 250, "plate (with 2 pav)", [
            {"description": "1 small plate (180g)", "grams": 180},
            {"description": "1 full plate with 2 pav (300g)", "grams": 300},
        ], ["misal pav", "puneri misal", "kolhapuri misal"], "Maharashtrian", image_key="bread"),
        F("usal-pav-matki", "Matki usal with pav", "Breakfast", "Sprouted moth beans cooked with onions, goda masala and fresh coconut", 142, 5.8, 19.5, 5.0, 4.0, 1.8, 380, 200, "plate", [
            {"description": "1 bowl (150g)", "grams": 150},
            {"description": "1 plate with 2 pav (250g)", "grams": 250},
        ], ["usal pav", "matki usal", "moth bean curry"], "Maharashtrian"),
        F("batata-vada-mumbai", "Batata vada (Spiced potato fritter)", "Snacks", "Spiced mashed potato ball coated in gram flour batter and deep-fried", 235, 3.5, 28.0, 12.0, 2.2, 1.0, 390, 65, "piece", [
            {"description": "1 vada (65g)", "grams": 65},
            {"description": "2 vadas (130g)", "grams": 130},
        ], ["batata vada", "aloo bonda", "potato vada"], "Street Food", image_key="potato"),
        F("vada-pav-mumbai", "Vada pav (Mumbai burger)", "Snacks", "Batata vada sandwiched in pav with spicy garlic chutney and green chutney", 260, 5.5, 38.0, 10.0, 3.0, 2.0, 520, 120, "piece", [
            {"description": "1 vada pav (120g)", "grams": 120},
            {"description": "2 vada pavs (240g)", "grams": 240},
        ], ["vada pav", "wada pav", "bombay burger"], "Street Food", image_key="bread"),
        F("dabeli-kutch-mumbai", "Kutchi dabeli", "Snacks", "Spiced sweet-tangy potato filling inside pav with roasted masala peanuts, sev and pomegranate", 245, 4.8, 36.0, 9.2, 2.8, 6.0, 410, 110, "piece", [
            {"description": "1 dabeli (110g)", "grams": 110},
            {"description": "2 dabelis (220g)", "grams": 220},
        ], ["dabeli", "kutchi dabeli", "double roti"], "Street Food", image_key="bread"),
        F("ragda-pattice-mumbai", "Ragda pattice", "Snacks", "Pan-fried potato patties topped with warm dried white pea curry, chutneys and sev", 165, 4.5, 26.0, 5.0, 4.2, 3.5, 460, 220, "plate (2 pattice)", [
            {"description": "1 plate (220g)", "grams": 220},
        ], ["ragda pattice", "ragda patties"], "Street Food", image_key="potato"),
        F("bhel-puri-mumbai", "Mumbai bhel puri", "Snacks", "Puffed rice, sev, chopped onions, boiled potatoes and tangy tamarind-mint chutneys", 185, 4.0, 32.0, 4.8, 2.5, 5.0, 420, 150, "plate", [
            {"description": "1 plate (150g)", "grams": 150},
        ], ["bhel", "bhelpuri", "sukha bhel"], "Street Food"),
        F("sev-puri-chaat", "Sev puri", "Snacks", "Crispy flat puris topped with seasoned diced potatoes, onions, chutneys and nylon sev", 215, 3.8, 28.0, 10.0, 2.2, 3.0, 460, 120, "plate (6 puris)", [
            {"description": "1 plate (6 pieces / 120g)", "grams": 120},
        ], ["sev puri", "sev batata puri"], "Street Food"),
        F("dahi-puri-chaat", "Dahi sev batata puri (SPDP)", "Snacks", "Crisp puffed puris filled with potatoes, sweetened curd, tamarind chutney and sev", 195, 4.2, 28.0, 7.5, 1.8, 6.5, 380, 150, "plate (6 puris)", [
            {"description": "1 plate (6 puris / 150g)", "grams": 150},
        ], ["dahi puri", "spdp", "dahi batata puri"], "Street Food", image_key="curd"),
        F("pani-puri-golgappa", "Pani puri / Golgappa", "Snacks", "Crisp hollow semolina puris filled with spicy mint water, sweet tamarind chutney and boiled potatoes", 130, 2.5, 22.0, 3.5, 1.5, 2.8, 510, 150, "portion (6 puris)", [
            {"description": "1 plate (6 puris with pani / 150g)", "grams": 150},
            {"description": "8 puris (200g)", "grams": 200},
        ], ["golgappa", "puchka", "pani ke batashe"], "Street Food"),
        F("kolhapuri-tambda-rassa", "Kolhapuri tambda rassa (Red curry)", "Curries", "Spicy mutton stock broth cooked with red chilies and Kolhapuri masala", 125, 8.5, 3.0, 9.0, 0.8, 0.5, 450, 180, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
            {"description": "1 bowl (220ml)", "grams": 220},
        ], ["tambda rassa", "kolhapuri rassa", "red mutton curry"], "Maharashtrian"),
        F("kolhapuri-pandhra-rassa", "Kolhapuri pandhra rassa (White curry)", "Curries", "Rich mutton broth infused with coconut milk, poppy seeds and whole spices", 140, 7.0, 3.5, 11.0, 0.5, 0.8, 380, 180, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
        ], ["pandhra rassa", "white mutton soup"], "Maharashtrian"),
        F("zunka-bhakri-combo", "Zunka (Dry spiced gram flour)", "Curries", "Gram flour tempered with onions, garlic, mustard seeds, curry leaves and green chilies", 175, 7.5, 18.0, 8.5, 4.0, 1.5, 410, 120, "serving", [
            {"description": "1 portion (120g)", "grams": 120},
        ], ["zunka", "jhunka", "dry besan"], "Maharashtrian"),
        F("pithla-gram-flour", "Pithla (Savory gram flour curry)", "Curries", "Semi-liquid spiced besan curry tempered with cumin, garlic and green chilies", 135, 6.0, 14.0, 6.0, 3.0, 1.2, 390, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["pithla", "pitla", "besan curry"], "Maharashtrian"),
        F("bharli-vangi-brinjal", "Bharli vangi (Stuffed baby eggplants)", "Curries", "Baby eggplants stuffed with roasted peanuts, sesame, goda masala and dry coconut", 155, 3.8, 12.0, 10.5, 4.5, 2.5, 360, 150, "katori", [
            {"description": "2 stuffed baby brinjals (150g)", "grams": 150},
        ], ["bharli vangi", "stuffed brinjal maharashtrian", "baingan masala"], "Maharashtrian"),
        F("katachi-amti-tangy", "Katachi amti (Spiced chana dal water)", "Curries", "Tangy thin dal strained from puran poli lentils, tempered with goda masala and tamarind", 75, 3.0, 10.0, 2.5, 1.8, 2.0, 320, 150, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
        ], ["katachi amti", "amti", "maharashtrian amti"], "Maharashtrian", image_key="dal"),
        F("solkadhi-beverage", "Solkadhi (Kokum coconut digestive)", "Beverages", "Fresh coconut milk infused with tangy kokum fruit juice, garlic, green chilies and salt", 78, 1.2, 4.0, 6.8, 0.4, 1.2, 280, 150, "glass", [
            {"description": "1 small glass (150ml)", "grams": 150},
            {"description": "1 glass (200ml)", "grams": 200},
        ], ["sol kadhi", "kokum kadi", "solkadhi"], "Beverages"),
        F("modak-ukadiche-steamed", "Ukadiche modak (Steamed coconut dumpling)", "Sweets", "Steamed rice flour dumplings stuffed with grated fresh coconut, jaggery and cardamom", 210, 2.8, 38.0, 5.5, 2.0, 22.0, 25, 45, "piece", [
            {"description": "1 modak (45g)", "grams": 45},
            {"description": "2 modaks (90g)", "grams": 90},
        ], ["ukadiche modak", "steamed modak", "ganesh modak"], "Sweets"),
        F("modak-fried-sweet", "Fried modak", "Sweets", "Crispy wheat flour dumplings stuffed with sweet coconut and jaggery, deep fried", 360, 4.5, 48.0, 17.0, 2.5, 24.0, 45, 40, "piece", [
            {"description": "1 fried modak (40g)", "grams": 40},
        ], ["fried modak", "talaniche modak"], "Sweets"),
        F("shrikhand-kesar-elaichi", "Kesar elaichi shrikhand", "Sweets", "Hung curd whipped with saffron, green cardamom powder and sugar", 270, 7.5, 38.0, 9.5, None, 35.0, 60, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
            {"description": "1/2 cup (120g)", "grams": 120},
        ], ["shrikhand", "kesar shrikhand", "matha"], "Sweets", image_key="curd"),
        F("amrakhand-mango-shrikhand", "Amrakhand (Mango shrikhand)", "Sweets", "Strained hung yogurt whipped with ripe Alphonso mango pulp and sugar", 240, 6.0, 36.0, 8.2, 0.5, 32.0, 50, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["amrakhand", "mango yogurt sweet"], "Sweets", image_key="mango"),
        F("puran-poli-traditional", "Puran poli with pure ghee", "Bread", "Whole wheat flatbread stuffed with sweet cooked chana dal, jaggery and nutmeg, topped with ghee", 285, 6.5, 52.0, 6.0, 3.8, 24.0, 65, 80, "piece", [
            {"description": "1 poli (80g)", "grams": 80},
            {"description": "2 polis (160g)", "grams": 160},
        ], ["puran poli", "vedmi", "sweet roti"], "Maharashtrian", image_key="roti"),
        F("bombil-rava-fry", "Bombil rava fry (Bombay duck)", "Meat", "Bombay duck fish fillets marinated in red chili paste and crisp semolina fried", 205, 17.5, 12.0, 9.8, 0.8, 0.2, 420, 120, "piece (2 fillets)", [
            {"description": "2 pieces (120g)", "grams": 120},
        ], ["bombil fry", "bombay duck fry"], "Seafood"),
        F("surmai-rava-fry", "Surmai rava fry (Kingfish)", "Meat", "Kingfish steak marinated with malvani spices, coated with rava and pan fried", 215, 21.0, 8.0, 11.0, 0.5, 0.0, 390, 130, "steak", [
            {"description": "1 fish steak (130g)", "grams": 130},
        ], ["surmai fry", "kingfish fry", "rava fish fry"], "Seafood"),
        F("kothimbir-wadi-tawa-fry", "Tawa-fried kothimbir vadi", "Snacks", "Shallow pan-fried crisp coriander and besan fritters with mustard and sesame seeds", 195, 7.0, 21.0, 9.5, 3.8, 1.5, 350, 80, "portion (4 vadis)", [
            {"description": "4 pieces (80g)", "grams": 80},
        ], ["tawa fried kothimbir vadi", "crispy kothimbir vadi"], "Maharashtrian"),
        F("alu-vadi-crispy-fried", "Crispy fried alu vadi / patra", "Snacks", "Deep-fried crispy colocasia pinwheels", 240, 5.8, 26.0, 13.0, 3.2, 4.5, 380, 80, "portion (4 slices)", [
            {"description": "4 slices (80g)", "grams": 80},
        ], ["fried patra", "fried alu vadi"], "Maharashtrian"),
        F("sabudana-vada-crispy", "Sabudana vada (Tapioca pearl fritter)", "Snacks", "Deep-fried crisp patties of soaked sabudana, mashed potatoes and crushed roasted peanuts", 310, 4.0, 42.0, 14.5, 2.0, 2.0, 290, 60, "vada", [
            {"description": "1 vada (60g)", "grams": 60},
            {"description": "2 vadas (120g)", "grams": 120},
        ], ["sabudana vada", "sago vada", "upvas vada"], "Fasting"),
        F("batata-poha-aloo", "Batata poha (Potato poha)", "Breakfast", "Flattened rice tempered with diced potatoes, mustard seeds, turmeric, peanuts and fresh coriander", 180, 3.5, 32.0, 4.5, 2.0, 1.5, 290, 150, "katori", [
            {"description": "1 medium bowl (150g)", "grams": 150},
            {"description": "1 large plate (220g)", "grams": 220},
        ], ["batata poha", "aloo poha", "flattened rice with potatoes"], "Maharashtrian", image_key="potato"),
        F("dadpe-pohe-coconut", "Dadpe pohe (Raw seasoned poha)", "Breakfast", "Thin poha seasoned with fresh coconut, onions, raw peanuts, green chilies and lemon juice", 165, 3.2, 28.0, 4.5, 2.2, 1.8, 240, 120, "bowl", [
            {"description": "1 bowl (120g)", "grams": 120},
        ], ["dadpe pohe", "dadpe poha"], "Maharashtrian"),
        F("sheera-sooji-halwa", "Rava sheera / Sooji halwa (Ghee)", "Sweets", "Semolina slow roasted in pure cow ghee, cooked with milk, sugar, cardamom and cashews", 320, 4.5, 48.0, 12.8, 1.2, 28.0, 35, 100, "katori", [
            {"description": "1 small katori (80g)", "grams": 80},
            {"description": "1 medium katori (120g)", "grams": 120},
        ], ["sheera", "sooji halwa", "rava kesari"], "Sweets"),
        F("shankarpali-sweet-crisp", "Sweet shankarpali", "Snacks", "Diamond-shaped crisp fried tea-time snack made of maida, ghee and sugar", 460, 6.0, 64.0, 20.5, 1.5, 26.0, 80, 40, "handful", [
            {"description": "1 small handful (30g)", "grams": 30},
            {"description": "1 cup (60g)", "grams": 60},
        ], ["shankarpali", "shakarpara", "sweet diamonds"], "Traditional Snacks"),
        F("chivda-poha-thin", "Thin poha chivda", "Snacks", "Roasted thin flattened rice tossed with peanuts, dry coconut slices, curry leaves and mild spices", 430, 7.5, 62.0, 17.5, 4.2, 3.5, 480, 35, "serving", [
            {"description": "1 small bowl (35g)", "grams": 35},
            {"description": "1 cup (60g)", "grams": 60},
        ], ["poha chivda", "patla poha chivda"], "Traditional Snacks"),
        F("chivda-cornflakes-spiced", "Cornflakes chivda", "Snacks", "Crispy roasted cornflakes tossed with roasted peanuts, cashews, raisins and chaat spices", 445, 6.5, 66.0, 18.0, 3.5, 6.5, 520, 35, "serving", [
            {"description": "1 small cup (35g)", "grams": 35},
        ], ["cornflakes chivda", "corn chivda"], "Traditional Snacks"),
    ])

    # =========================================================================
    # NORTH INDIAN CURRIES, DALS & SPECIALTY BREADS
    # =========================================================================
    items.extend([
        F("amritsari-kulcha-stuffed", "Amritsari stuffed potato kulcha", "Bread", "Flaky layered tandoor baked leavened bread stuffed with spiced mashed potatoes and pomegranate seeds", 275, 6.5, 46.0, 7.5, 3.0, 1.5, 450, 140, "piece", [
            {"description": "1 kulcha (140g)", "grams": 140},
        ], ["amritsari kulcha", "aloo kulcha"], "North Indian Breads", image_key="bread"),
        F("chole-bhature-combo", "Bhatura (Deep fried leavened bread)", "Bread", "Golden fluffy deep-fried leavened fermented bread", 345, 7.5, 48.0, 14.0, 1.8, 1.5, 380, 90, "piece", [
            {"description": "1 large bhatura (90g)", "grams": 90},
            {"description": "2 bhaturas (180g)", "grams": 180},
        ], ["bhatura", "bhatoora", "chole bhature"], "North Indian Breads", image_key="bread"),
        F("dal-makhani-butter-cream", "Dal makhani (Slow-cooked black lentils)", "Curries", "Whole black urad dal and kidney beans slow-simmered overnight with butter, cream and tomatoes", 145, 5.5, 14.5, 7.5, 4.0, 1.5, 380, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["dal makhani", "maa ki dal", "black lentil curry"], "North Indian", image_key="dal"),
        F("rajma-masala-curry", "Rajma masala (Red kidney bean curry)", "Curries", "Tender red kidney beans cooked in a rich onion-tomato masala gravy with ginger and garam masala", 130, 6.5, 18.0, 3.8, 5.2, 1.8, 360, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 large bowl (250g)", "grams": 250},
        ], ["rajma", "rajma chawal", "kidney bean curry"], "North Indian", image_key="dal"),
        F("shahi-paneer-curry", "Shahi paneer", "Curries", "Soft paneer cubes in a luxurious cashew, fresh cream, tomato and saffron gravy", 195, 8.5, 8.0, 14.5, 1.2, 3.5, 420, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 restaurant bowl (220g)", "grams": 220},
        ], ["shahi paneer", "royal paneer"], "North Indian", image_key="paneer"),
        F("matar-paneer-curry", "Matar paneer", "Curries", "Paneer cubes and tender green peas cooked in a spiced cumin-tomato gravy", 165, 8.0, 9.5, 10.5, 2.5, 2.5, 380, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["mutter paneer", "matar paneer"], "North Indian", image_key="paneer"),
        F("kadai-paneer-bellpepper", "Kadai paneer", "Curries", "Paneer cubes tossed with crisp bell peppers, onions and freshly pounded coriander-chili kadai masala", 185, 9.0, 7.5, 13.0, 2.0, 2.0, 410, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["kadai paneer", "karahi paneer"], "North Indian", image_key="paneer"),
        F("palak-paneer-spinach", "Palak paneer", "Curries", "Fresh cottage cheese cubes in a mildly spiced pureed spinach gravy with garlic", 145, 8.5, 5.0, 10.2, 2.8, 1.2, 360, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["palak paneer", "spinach paneer"], "North Indian", image_key="paneer"),
        F("paneer-butter-masala-restaurant", "Paneer butter masala", "Curries", "Paneer in a velvety smooth tomato, butter and cashew makhani gravy seasoned with kasuri methi", 210, 8.5, 9.5, 16.0, 1.5, 4.0, 440, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["paneer makhani", "paneer butter masala", "butter paneer"], "North Indian", image_key="paneer"),
        F("aloo-gobi-adraki", "Aloo gobi (Cauliflower & potato)", "Vegetables", "Tender cauliflower florets and diced potatoes sautéed with cumin, turmeric, coriander and ginger", 125, 2.8, 16.5, 5.5, 3.2, 2.2, 320, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["aloo gobi", "alu gobi", "spiced cauliflower potato"], "North Indian", image_key="potato"),
        F("kurkuri-bhindi-crispy", "Kurkuri bhindi (Crispy spiced okra)", "Vegetables", "Thinly sliced okra tossed in spiced gram flour and flash-fried crisp", 210, 4.2, 18.0, 14.0, 4.5, 2.0, 340, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["kurkuri bhindi", "crispy okra", "fried bhindi"], "North Indian"),
        F("baingan-bharta-smoked", "Baingan bharta (Smoky roasted eggplant)", "Vegetables", "Charcoal roasted mashed eggplant cooked with green peas, onions, tomatoes and green chilies", 95, 2.0, 10.5, 5.0, 3.5, 3.0, 290, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["baingan bharta", "eggplant mash", "vange bharit"], "North Indian"),
        F("sarson-ka-saag-mustard", "Sarson ka saag (Mustard greens)", "Vegetables", "Slow-cooked pureed mustard and bathua greens tempered with pure ghee, garlic and ginger", 90, 3.5, 8.0, 5.2, 3.8, 1.5, 310, 160, "katori", [
            {"description": "1 katori (160g)", "grams": 160},
        ], ["sarson saag", "mustard greens curry"], "North Indian", image_key="spinach"),
        F("makki-di-roti-cornmeal", "Makki di roti (Cornmeal flatbread)", "Bread", "Unleavened yellow cornmeal flatbread cooked on tawa with a dab of white butter", 230, 4.8, 42.0, 5.5, 4.5, 0.8, 90, 60, "roti", [
            {"description": "1 small roti (50g)", "grams": 50},
            {"description": "1 standard roti (65g)", "grams": 65},
        ], ["makki roti", "corn roti", "punjabi corn bread"], "North Indian Breads", image_key="roti"),
        F("missi-roti-besan", "Missi roti (Spiced besan roti)", "Bread", "Flatbread made from whole wheat and chickpea flour spiced with ajwain, onions and green chili", 240, 7.5, 42.0, 4.8, 5.2, 1.2, 180, 55, "roti", [
            {"description": "1 roti (55g)", "grams": 55},
            {"description": "2 rotis (110g)", "grams": 110},
        ], ["missi roti", "besan roti"], "North Indian Breads", image_key="roti"),
        F("rumali-roti-thin", "Rumali roti", "Bread", "Ultra-thin, soft, handkerchief-like flatbread tossed in the air and baked on an inverted wok", 255, 7.8, 52.0, 2.0, 2.0, 1.0, 240, 65, "piece", [
            {"description": "1 rumali roti (65g)", "grams": 65},
        ], ["rumali roti", "roomali roti", "handkerchief bread"], "North Indian Breads", image_key="roti"),
        F("tandoori-roti-plain", "Tandoori roti (Plain)", "Bread", "Whole wheat bread stuck to the curved wall of a clay tandoor oven and baked dry", 245, 8.2, 48.0, 2.2, 6.0, 1.0, 160, 50, "roti", [
            {"description": "1 tandoori roti (50g)", "grams": 50},
            {"description": "2 tandoori rotis (100g)", "grams": 100},
        ], ["tandoori roti", "plain tandoori roti"], "North Indian Breads", image_key="roti"),
        F("laccha-naan-layered", "Layered laccha naan", "Bread", "Flaky layered tandoor baked leavened naan brushed with melted butter", 320, 8.2, 47.0, 11.5, 2.0, 2.5, 420, 95, "piece", [
            {"description": "1 naan (95g)", "grams": 95},
        ], ["laccha naan", "layered naan"], "North Indian Breads", image_key="bread"),
        F("garlic-naan-tandoori", "Garlic naan", "Bread", "Tandoor baked refined flour leavened bread brushed with garlic butter and fresh cilantro", 295, 7.8, 48.0, 8.5, 2.0, 2.5, 420, 90, "piece", [
            {"description": "1 naan (90g)", "grams": 90},
        ], ["garlic naan", "tandoori garlic naan"], "North Indian Breads", image_key="bread"),
        F("butter-naan-layered", "Butter naan", "Bread", "Teardrop-shaped soft leavened white bread glazed with melted dairy butter", 310, 8.0, 48.0, 10.0, 2.0, 2.5, 410, 90, "piece", [
            {"description": "1 butter naan (90g)", "grams": 90},
        ], ["butter naan", "naan"], "North Indian Breads", image_key="bread"),
        F("laccha-paratha-tandoori", "Tandoori laccha paratha", "Bread", "Multi-layered spiraled whole wheat paratha baked crispy in the tandoor", 315, 6.8, 46.0, 12.0, 4.0, 1.2, 310, 80, "piece", [
            {"description": "1 paratha (80g)", "grams": 80},
        ], ["laccha paratha", "layered paratha"], "North Indian Breads", image_key="roti"),
    ])

    # =========================================================================
    # SOUTH INDIAN SPECIALTIES
    # =========================================================================
    items.extend([
        F("uttapam-onion-topped", "Onion uttapam", "Breakfast", "Thick fermented rice and urad dal pancake topped with finely chopped onions and curry leaves", 165, 4.5, 30.0, 3.2, 2.4, 2.0, 280, 140, "piece", [
            {"description": "1 uttapam (140g)", "grams": 140},
        ], ["onion uttapam", "oothappam"], "South Indian Breakfast", image_key="dosa"),
        F("uttapam-tomato-onion", "Tomato onion uttapam", "Breakfast", "Thick pancake topped with diced juicy tomatoes, onions and green chilies", 158, 4.2, 29.0, 3.0, 2.5, 2.8, 270, 150, "piece", [
            {"description": "1 uttapam (150g)", "grams": 150},
        ], ["tomato uttapam", "tomato onion oothappam"], "South Indian Breakfast", image_key="dosa"),
        F("pongal-ven-ghee", "Ven pongal (Ghee pongal)", "Breakfast", "Comforting rice and yellow moong dal cooked soft and tempered with ghee, black pepper, cumin and cashews", 175, 4.5, 26.0, 6.2, 1.8, 0.4, 260, 180, "bowl", [
            {"description": "1 cup / small bowl (150g)", "grams": 150},
            {"description": "1 medium serving (200g)", "grams": 200},
        ], ["ven pongal", "khara pongal", "ghee pongal"], "South Indian Breakfast", image_key="rice"),
        F("pongal-sakkarai-sweet", "Sweet pongal (Sakkarai pongal)", "Sweets", "Rice and moong dal simmered with dark jaggery, pure ghee, cardamom, cashews and raisins", 255, 3.8, 48.0, 6.0, 1.5, 34.0, 40, 120, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
            {"description": "1 medium bowl (150g)", "grams": 150},
        ], ["sakkarai pongal", "sweet pongal", "chakkara pongal"], "Sweets", image_key="rice"),
        F("upma-rava-sooji", "Rava upma (Sooji upma)", "Breakfast", "Roasted semolina cooked with mustard seeds, green chilies, ginger, curry leaves and roasted peanuts", 160, 3.8, 26.5, 4.5, 1.8, 1.2, 270, 150, "bowl", [
            {"description": "1 medium bowl (150g)", "grams": 150},
            {"description": "1 large serving (220g)", "grams": 220},
        ], ["rava upma", "sooji upma", "uppittu"], "South Indian Breakfast"),
        F("upma-vermicelli-semiya", "Semiya upma (Vermicelli upma)", "Breakfast", "Roasted wheat vermicelli cooked with vegetables, mustard seeds and curry leaves", 155, 3.6, 27.0, 3.8, 1.8, 1.2, 260, 150, "bowl", [
            {"description": "1 bowl (150g)", "grams": 150},
        ], ["semiya upma", "vermicelli upma", "sevai upma"], "South Indian Breakfast"),
        F("lemon-rice-chitranna", "Lemon rice (Chitranna)", "Grains", "Steamed rice tossed with turmeric, mustard seeds, curry leaves, roasted peanuts and fresh lemon juice", 168, 3.2, 30.0, 4.2, 1.2, 0.8, 240, 180, "bowl", [
            {"description": "1 medium bowl (180g)", "grams": 180},
            {"description": "1 large plate (250g)", "grams": 250},
        ], ["lemon rice", "chitranna", "elamichai sadam"], "South Indian", image_key="rice"),
        F("tamarind-rice-puliyodharai", "Tamarind rice (Puliyodharai)", "Grains", "Rice tossed with tangy spiced tamarind pulp, sesame oil, roasted chana dal and peanuts", 185, 3.5, 32.0, 5.0, 1.8, 1.8, 320, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["puliyodharai", "pulihora", "tamarind rice"], "South Indian", image_key="rice"),
        F("curd-rice-thayir-sadam", "Curd rice (Thayir sadam)", "Grains", "Soft mashed rice blended with fresh curd and tempered with mustard seeds, curry leaves and ginger", 135, 3.8, 20.0, 4.2, 0.8, 2.5, 210, 200, "bowl", [
            {"description": "1 medium bowl (200g)", "grams": 200},
            {"description": "1 large bowl (300g)", "grams": 300},
        ], ["curd rice", "thayir sadam", "daddojanam", "dahi bhat"], "South Indian", image_key="rice"),
        F("rasam-tomato-pepper", "Tomato pepper rasam", "Soups", "Tangy and peppery south Indian tamarind broth infused with crushed black pepper, cumin and tomatoes", 45, 1.2, 7.5, 1.2, 0.8, 1.5, 310, 150, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
            {"description": "1 cup (200ml)", "grams": 200},
        ], ["rasam", "tomato rasam", "saaru"], "South Indian", image_key="tomato"),
        F("rasam-mysore-style", "Mysore rasam", "Soups", "Aromatic lentil and tomato rasam spiced with freshly roasted coriander seeds, coconut and red chilies", 60, 2.0, 8.5, 2.0, 1.2, 1.8, 340, 150, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
        ], ["mysore rasam", "kalyana rasam"], "South Indian"),
        F("sambar-drumstick-shallot", "Drumstick and shallot sambar", "Curries", "Toor dal cooked with drumsticks, pearl onions, tamarind and freshly roasted sambar powder", 85, 3.8, 13.0, 2.0, 3.0, 2.5, 340, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 large bowl (250g)", "grams": 250},
        ], ["sambar", "murungakkai sambar", "south indian sambar"], "South Indian", image_key="dal"),
        F("avial-kerala-vegetables", "Kerala avial (Mixed vegetables in coconut)", "Curries", "Assorted vegetables simmered in coconut-cumin paste and yogurt, finished with coconut oil and curry leaves", 115, 2.5, 9.5, 7.5, 3.5, 2.8, 220, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["avial", "aviyal", "kerala avial"], "South Indian"),
        F("cabbage-thoran-kerala", "Cabbage thoran", "Vegetables", "Shredded cabbage stir-fried with freshly grated coconut, green chilies, mustard seeds and curry leaves", 78, 2.2, 7.5, 4.5, 2.8, 2.5, 210, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["cabbage thoran", "kerala cabbage poriyal"], "South Indian"),
        F("beans-thoran-kerala", "Beans thoran (Green beans with coconut)", "Vegetables", "Finely chopped french beans sautéed with grated coconut, mustard seeds and shallots", 85, 2.8, 8.5, 4.5, 3.2, 2.0, 190, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["beans thoran", "green beans poriyal"], "South Indian"),
        F("appam-kerala-rice", "Kerala appam (Palappam)", "Breakfast", "Fermented rice batter pancake with a soft thick spongy center and thin crispy lacy edges", 145, 2.2, 28.0, 2.5, 1.2, 3.0, 110, 65, "piece", [
            {"description": "1 appam (65g)", "grams": 65},
            {"description": "2 appams (130g)", "grams": 130},
        ], ["appam", "palappam", "kerala appam"], "South Indian Breakfast"),
        F("vegetable-stew-kerala", "Kerala vegetable stew", "Curries", "Carrots, potatoes and green beans simmered in delicate spiced coconut milk with ginger and black pepper", 125, 2.2, 11.0, 8.2, 2.5, 3.5, 240, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["veg stew", "kerala stew", "ishtew"], "South Indian"),
        F("mutton-stew-kerala", "Kerala mutton stew", "Curries", "Tender mutton and potatoes gently simmered in mild coconut milk with whole spices", 185, 14.5, 6.0, 12.0, 1.2, 1.8, 330, 200, "katori", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["mutton stew", "kerala mutton stew", "meat stew"], "South Indian"),
        F("idiyappam-string-hoppers", "Idiyappam (String hoppers)", "Breakfast", "Delicate steamed rice flour vermicelli nests served with coconut milk or spicy curry", 120, 2.0, 26.5, 0.5, 1.0, 0.2, 45, 75, "piece (2 nests)", [
            {"description": "2 nests (75g)", "grams": 75},
            {"description": "3 nests (110g)", "grams": 110},
        ], ["idiyappam", "string hoppers", "noolappam"], "South Indian Breakfast"),
        F("kuzhi-paniyaram-savory", "Kuzhi paniyaram (Savory)", "Breakfast", "Crispy on the outside, fluffy inside fermented batter dumplings tempered with onions and mustard", 175, 4.5, 30.0, 4.2, 2.0, 1.5, 290, 120, "portion (4 pieces)", [
            {"description": "4 pieces (120g)", "grams": 120},
        ], ["paniyaram", "kuzhi paniyaram", "paddu"], "South Indian Breakfast"),
        F("medu-vada-crispy", "Crispy medu vada", "Breakfast", "Doughnut-shaped deep-fried crisp fritter made of seasoned black gram batter with pepper and curry leaves", 270, 7.8, 28.0, 14.5, 3.5, 0.5, 360, 50, "piece", [
            {"description": "1 medu vada (50g)", "grams": 50},
            {"description": "2 medu vadas (100g)", "grams": 100},
        ], ["medu vada", "urad dal vada", "sambar vada"], "South Indian Breakfast"),
        F("pesarattu-green-gram", "Pesarattu (Whole moong dosa)", "Breakfast", "Nutritious thin green crepe made from ground whole green moong dal and ginger", 168, 8.5, 26.0, 3.2, 4.5, 0.8, 220, 100, "dosa", [
            {"description": "1 pesarattu (100g)", "grams": 100},
        ], ["pesarattu", "moong dal dosa", "andhra dosa"], "South Indian Breakfast", image_key="dosa"),
        F("parotta-malabar-flaky", "Malabar parotta", "Bread", "Flaky, multi-layered spiral flatbread made with maida and ghee, beaten and griddled", 330, 6.5, 48.0, 13.0, 1.5, 1.2, 340, 90, "piece", [
            {"description": "1 parotta (90g)", "grams": 90},
            {"description": "2 parottas (180g)", "grams": 180},
        ], ["malabar parotta", "kerala parotta", "layered parotta"], "South Indian Breads", image_key="bread"),
        F("kozhi-curry-kerala", "Kerala chicken roast curry (Nadan Kozhi)", "Curries", "Chicken pieces slow-cooked with roasted coconut paste, fennel and shallots", 195, 16.5, 5.0, 12.5, 1.8, 1.5, 420, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["kerala chicken curry", "kozhi curry", "nadan chicken"], "South Indian", image_key="chicken_breast"),
        F("payasam-semiya-vermicelli", "Semiya payasam (Vermicelli kheer)", "Sweets", "Roasted vermicelli simmered in sweetened whole milk flavored with green cardamom and ghee-roasted nuts", 185, 4.0, 30.0, 5.5, 0.8, 22.0, 65, 150, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
        ], ["semiya payasam", "vermicelli kheer", "seviyan kheer"], "Sweets"),
        F("ada-pradhaman-kerala", "Ada pradhaman", "Sweets", "Traditional Kerala festive dessert made of steamed rice flakes simmered in rich jaggery and coconut milk", 215, 2.5, 38.0, 6.5, 1.0, 28.0, 45, 150, "katori", [
            {"description": "1 katori (150ml)", "grams": 150},
        ], ["ada pradhaman", "palada pradhaman"], "Sweets"),
    ])

    # =========================================================================
    # REFRESHING BEVERAGES
    # =========================================================================
    items.extend([
        F("nimbu-pani-salted", "Nimbu pani (Salted lime water)", "Beverages", "Freshly squeezed lime juice in water with black salt and roasted cumin powder", 12, 0.3, 2.8, 0.0, 0.2, 0.5, 220, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["nimbu pani", "salted lemonade", "lemon water"], "Beverages"),
        F("shikanji-masala", "Masala shikanji (Spiced lemonade)", "Beverages", "Lemon juice with mint leaves, cumin, black salt, pepper and a dash of sugar", 42, 0.4, 10.5, 0.1, 0.3, 9.5, 180, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["shikanji", "masala lemonade", "shikanjvi"], "Beverages"),
        F("kokum-sharbat-sweet", "Kokum sharbat (Sweet & tangy)", "Beverages", "Cooling wild mangosteen (kokum) nectar with sugar, roasted cumin and black salt", 55, 0.2, 14.0, 0.0, 0.2, 13.5, 90, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["kokum sharbat", "kokum juice"], "Beverages"),
        F("aam-panna-raw-mango", "Aam panna (Raw mango drink)", "Beverages", "Refreshing green summer cooler made of roasted raw mango pulp, jaggery, mint and black salt", 65, 0.4, 16.5, 0.1, 0.5, 15.0, 110, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["aam panna", "kairi panna", "green mango drink"], "Beverages", image_key="mango"),
        F("sugarcane-juice-fresh", "Fresh sugarcane juice with ginger & lime", "Beverages", "Fresh cold-pressed natural sugarcane juice with a hint of fresh ginger and lime", 75, 0.2, 19.0, 0.0, 0.0, 18.0, 20, 250, "glass", [
            {"description": "1 small glass (200ml)", "grams": 200},
            {"description": "1 standard glass (250ml)", "grams": 250},
        ], ["ganna juice", "sugarcane juice", "cane juice"], "Beverages"),
        F("thandai-traditional-spiced", "Traditional thandai (Spiced milk)", "Beverages", "Chilled milk flavored with crushed almonds, fennel seeds, black peppercorns, cardamom and saffron", 145, 4.5, 18.0, 6.5, 1.2, 16.0, 65, 200, "glass", [
            {"description": "1 glass (200ml)", "grams": 200},
        ], ["thandai", "holi thandai", "badaam thandai"], "Beverages", image_key="milk"),
        F("jaljeera-water-drink", "Jaljeera (Spiced cumin cooler)", "Beverages", "Chilled digestive drink of cumin, dried mango powder, tamarind, fresh mint and boondi", 22, 0.5, 5.0, 0.2, 0.5, 1.2, 340, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["jaljeera", "cumin drink"], "Beverages"),
        F("masala-chaas-buttermilk", "Masala chaas (Spiced buttermilk)", "Beverages", "Churned low-fat curd blended with cold water, roasted cumin, ginger, green chilies and fresh coriander", 30, 1.8, 2.5, 1.2, 0.2, 2.0, 190, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
            {"description": "1 large mug (350ml)", "grams": 350},
        ], ["chaas", "masala buttermilk", "taak", "mattha"], "Beverages", image_key="curd"),
        F("sweet-lassi-punjabi", "Punjabi sweet lassi", "Beverages", "Rich thick yogurt churned with sugar, cardamom and topped with a spoonful of fresh cream / malai", 115, 3.5, 18.5, 3.2, None, 17.0, 55, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
            {"description": "1 large tall glass (350ml)", "grams": 350},
        ], ["sweet lassi", "punjabi lassi", "dahi lassi"], "Beverages", image_key="curd"),
        F("mango-lassi-alphonso", "Alphonso mango lassi", "Beverages", "Smooth creamy blend of thick curd and sweet ripe Alphonso mango pulp flavored with cardamom", 125, 3.2, 21.0, 3.0, 0.5, 19.5, 50, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["mango lassi", "aam lassi"], "Beverages", image_key="mango"),
        F("masala-chai-ginger-cardamom", "Indian masala chai with milk", "Beverages", "Black tea simmered with full milk, freshly crushed ginger root, cardamom and sugar", 65, 2.2, 9.0, 2.4, None, 8.0, 35, 150, "cup", [
            {"description": "1 cutting cup (100ml)", "grams": 100},
            {"description": "1 standard teacup (150ml)", "grams": 150},
            {"description": "1 mug (250ml)", "grams": 250},
        ], ["masala chai", "adrak elaichi chai", "tea with milk"], "Beverages", image_key="tea"),
        F("filter-coffee-south-indian", "South Indian filter coffee", "Beverages", "Fresh brewed dark coffee-chicory decoction poured with steaming frothy whole milk and sugar", 75, 2.5, 9.5, 2.8, None, 8.5, 38, 150, "davarah-tumbler", [
            {"description": "1 traditional tumbler (150ml)", "grams": 150},
        ], ["filter coffee", "kaapi", "south indian coffee"], "Beverages", image_key="coffee"),
        F("coconut-water-fresh-tender", "Fresh tender coconut water", "Beverages", "Pure natural isotonic water tapped directly from fresh green coconut", 19, 0.7, 3.7, 0.2, 1.1, 2.6, 105, 240, "cup / shell", [
            {"description": "1 coconut shell (240ml)", "grams": 240},
            {"description": "1 glass (200ml)", "grams": 200},
        ], ["coconut water", "nariyal pani", "tender coconut"], "Beverages"),
        F("turmeric-latte-haldi-doodh", "Haldi doodh (Golden turmeric milk)", "Beverages", "Warm milk infused with pure turmeric root, black pepper, cardamom and honey", 78, 3.2, 8.5, 3.5, 0.2, 7.5, 42, 200, "cup", [
            {"description": "1 cup (200ml)", "grams": 200},
        ], ["haldi doodh", "turmeric milk", "golden milk"], "Beverages", image_key="milk"),
    ])

    # =========================================================================
    # TRADITIONAL INDIAN MITHAI / SWEETS
    # =========================================================================
    items.extend([
        F("gulab-jamun-khoya", "Gulab jamun (Khoya)", "Sweets", "Deep-fried milk solid balls soaked in fragrant rose-cardamom sugar syrup", 325, 4.5, 52.0, 11.5, 0.5, 45.0, 48, 50, "piece", [
            {"description": "1 jamun (50g)", "grams": 50},
            {"description": "2 jamuns (100g)", "grams": 100},
        ], ["gulab jamun", "jamun", "kala jamun"], "Sweets"),
        F("rasgulla-bengali-chenna", "Bengali rasgulla", "Sweets", "Soft spongy balls of fresh cow milk chenna cooked in hot light sugar syrup", 185, 4.0, 38.0, 2.0, None, 35.0, 30, 50, "piece", [
            {"description": "1 rasgulla (50g)", "grams": 50},
            {"description": "2 rasgullas (100g)", "grams": 100},
        ], ["rasgulla", "roshogolla", "chenna sweet"], "Sweets"),
        F("rasmalai-saffron-chenna", "Kesar rasmalai", "Sweets", "Flattened spongy chenna patties soaked in thick clotted milk flavored with saffron and pistachios", 220, 6.5, 26.0, 10.2, 0.5, 22.0, 52, 75, "piece with milk", [
            {"description": "1 piece with ras (75g)", "grams": 75},
            {"description": "2 pieces with ras (150g)", "grams": 150},
        ], ["rasmalai", "rossomalai", "saffron rasmalai"], "Sweets"),
        F("kaju-katli-cashew", "Kaju katli (Kaju barfi)", "Sweets", "Diamond-shaped rich confection made from cashew nut paste and fine sugar", 440, 9.8, 56.0, 20.0, 1.8, 48.0, 12, 18, "piece", [
            {"description": "1 piece (18g)", "grams": 18},
            {"description": "2 pieces (36g)", "grams": 36},
        ], ["kaju katli", "kaju barfi", "cashew sweet"], "Sweets"),
        F("besan-laddu-ghee", "Besan laddu (Pure ghee)", "Sweets", "Gram flour slow roasted in desi ghee and rolled with boora sugar and chopped almonds", 475, 8.5, 56.0, 24.5, 3.2, 42.0, 35, 40, "laddu", [
            {"description": "1 laddu (40g)", "grams": 40},
            {"description": "2 laddus (80g)", "grams": 80},
        ], ["besan laddu", "besan ke laddu", "magas"], "Sweets"),
        F("motichoor-laddu-boondi", "Motichoor laddu", "Sweets", "Melt-in-mouth sweet spheres made from tiny fried gram flour pearls soaked in saffron syrup", 395, 4.2, 62.0, 15.0, 1.2, 52.0, 42, 45, "laddu", [
            {"description": "1 laddu (45g)", "grams": 45},
            {"description": "2 laddus (90g)", "grams": 90},
        ], ["motichoor laddu", "boondi laddu", "motichur"], "Sweets"),
        F("gajar-ka-halwa-carrot", "Gajar ka halwa (Carrot pudding)", "Sweets", "Red carrots slow cooked in whole milk with khoya, pure ghee, green cardamom and cashews", 245, 4.5, 32.0, 11.2, 2.5, 26.0, 68, 120, "katori", [
            {"description": "1 small katori (80g)", "grams": 80},
            {"description": "1 standard bowl (120g)", "grams": 120},
        ], ["gajar halwa", "carrot halwa", "gajrela"], "Sweets", image_key="carrot"),
        F("moong-dal-halwa-rich", "Moong dal halwa (Rich ghee)", "Sweets", "Yellow moong lentils ground and roasted slowly in generous cow ghee, finished with milk and sugar", 380, 7.5, 48.0, 18.0, 2.8, 36.0, 45, 100, "katori", [
            {"description": "1 katori (100g)", "grams": 100},
        ], ["moong dal halwa", "moong halwa"], "Sweets", image_key="dal"),
        F("kheer-chawal-rice", "Rice kheer (Chawal kheer)", "Sweets", "Fragrant basmati rice simmered in whole milk with sugar, saffron, raisins and sliced almonds", 165, 4.2, 26.0, 5.0, 0.5, 18.0, 62, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["kheer", "chawal ki kheer", "rice pudding"], "Sweets", image_key="rice"),
        F("mysore-pak-ghee-sweet", "Traditional ghee Mysore pak", "Sweets", "Porous, melt-in-mouth confection made of roasted gram flour, pure ghee and boiling sugar syrup", 520, 5.5, 52.0, 32.5, 1.8, 45.0, 30, 35, "piece", [
            {"description": "1 piece (35g)", "grams": 35},
        ], ["mysore pak", "ghee mysore pak"], "Sweets"),
        F("sandesh-bengali-chenna", "Bengali sandesh", "Sweets", "Delicate cardamom and pistachio flavored fudge prepared from freshly curdled milk paneer", 290, 8.5, 42.0, 9.8, 0.4, 36.0, 45, 35, "piece", [
            {"description": "1 piece (35g)", "grams": 35},
            {"description": "2 pieces (70g)", "grams": 70},
        ], ["sandesh", "shondesh", "bengali sweet"], "Sweets"),
        F("jalebi-crispy-saffron", "Crispy saffron jalebi", "Sweets", "Crispy fried fermented flour swirls dipped in cardamom and saffron-infused sugar syrup", 345, 2.8, 68.0, 7.5, 0.8, 55.0, 38, 50, "portion (2 pieces)", [
            {"description": "2 small jalebis (50g)", "grams": 50},
            {"description": "100g jalebi portion", "grams": 100},
        ], ["jalebi", "crispy jalebi", "jilapi"], "Sweets"),
        F("basundi-thick-milk", "Basundi (Rich cardamom condensed milk)", "Sweets", "Whole milk slow-reduced to half its volume, sweetened and flavored with saffron, cardamom and charoli", 215, 6.5, 28.0, 8.8, 0.4, 25.0, 70, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["basundi", "rabri", "thick sweet milk"], "Sweets", image_key="milk"),
    ])

    return items

print("Catalogue part 11 loaded.")
