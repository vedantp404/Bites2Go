"""
Catalogue data part 1: Indian staples, flatbreads, dals, sabzis, breakfast, chaat, dairy, meats (Groups 1-8).
"""

from scripts.build_full_database import F

def get_part1():
    items = []

    # =========================================================================
    # GROUP 1: GRAINS, RICE, PULAO, BIRYANI, KHICHDI & FLOURS (~60 items)
    # =========================================================================
    items.extend([
        F("rice-brown-cooked", "Cooked brown rice", "Grains", "Cooked, boiled", 112, 2.6, 23.5, 0.9, 1.8, 0.2, 1, 150, "bowl", [
            {"description": "1 small katori (100g)", "grams": 100},
            {"description": "1 medium bowl (150g)", "grams": 150},
        ], ["brown rice", "cooked brown rice"], "Rice", image_key="rice"),
        F("rice-brown-raw", "Uncooked brown rice", "Grains", "Uncooked, dry", 362, 7.5, 76.0, 2.7, 3.4, 0.7, 7, 50, "cup portion", None, ["brown rice raw", "dry brown rice"], "Rice"),
        F("rice-basmati-cooked", "Cooked Basmati rice", "Grains", "Cooked, steamed", 130, 3.0, 28.0, 0.4, 0.4, 0.1, 1, 150, "bowl", [
            {"description": "1 medium bowl (150g)", "grams": 150},
            {"description": "1 cup (180g)", "grams": 180},
        ], ["basmati rice", "steamed basmati"], "Rice", image_key="rice"),
        F("rice-basmati-raw", "Uncooked Basmati rice", "Grains", "Uncooked, dry", 355, 8.5, 78.0, 0.6, 1.0, 0.1, 3, 50, "cup portion", None, ["raw basmati", "dry basmati"], "Rice"),
        F("rice-sona-masoori-cooked", "Cooked Sona Masoori rice", "Grains", "Cooked, boiled", 140, 3.0, 30.0, 0.5, 0.5, 0.1, 1, 150, "bowl", None, ["sona masoori", "south indian rice"], "Rice", image_key="rice"),
        F("rice-red-cooked", "Cooked red rice", "Grains", "Cooked, boiled", 115, 2.8, 24.0, 0.8, 2.0, 0.2, 2, 150, "bowl", None, ["red rice", "matta rice"], "Rice"),
        F("jeera-rice", "Jeera rice", "Grains", "Cooked with cumin and ghee", 170, 3.0, 32.0, 3.5, 0.8, 0.2, 180, 150, "bowl", [
            {"description": "1 medium bowl (150g)", "grams": 150},
            {"description": "1 large serving (220g)", "grams": 220},
        ], ["cumin rice", "zeera rice"], "Rice Dishes", image_key="rice"),
        F("veg-pulao", "Vegetable pulao", "Grains", "Cooked with mixed vegetables and spices", 165, 3.5, 30.0, 3.5, 2.0, 1.2, 210, 200, "plate", [
            {"description": "1 small bowl (150g)", "grams": 150},
            {"description": "1 standard plate (200g)", "grams": 200},
        ], ["pulao", "veg pilaf", "matar pulao"], "Rice Dishes"),
        F("veg-biryani", "Vegetable biryani", "Grains", "Cooked with basmati rice, vegetables and ghee", 180, 4.0, 32.0, 4.5, 2.2, 1.5, 280, 250, "plate", [
            {"description": "1 standard serving (250g)", "grams": 250},
            {"description": "1 full plate (350g)", "grams": 350},
        ], ["dum biryani", "vegetable biryani"], "Rice Dishes"),
        F("chicken-biryani", "Chicken biryani", "Grains", "Cooked with basmati rice, chicken and spices", 210, 12.0, 25.0, 6.8, 1.2, 0.8, 320, 300, "plate", [
            {"description": "1 medium serving (250g)", "grams": 250},
            {"description": "1 standard plate with chicken (350g)", "grams": 350},
        ], ["dum chicken biryani", "hyderabadi chicken biryani"], "Rice Dishes"),
        F("mutton-biryani", "Mutton biryani", "Grains", "Cooked with basmati rice, goat meat and ghee", 240, 14.0, 24.0, 10.0, 1.0, 0.6, 340, 300, "plate", [
            {"description": "1 plate (350g)", "grams": 350},
        ], ["lamb biryani", "gosht biryani"], "Rice Dishes"),
        F("egg-biryani", "Egg biryani", "Grains", "Cooked with basmati rice and boiled eggs", 195, 8.0, 26.0, 6.5, 1.2, 0.8, 290, 280, "plate", [
            {"description": "1 plate with 2 eggs (300g)", "grams": 300},
        ], ["anda biryani"], "Rice Dishes"),
        F("moong-khichdi", "Moong dal khichdi", "Grains", "Cooked with rice, yellow moong and mild ghee", 140, 5.5, 24.0, 2.5, 2.5, 0.5, 180, 200, "bowl", [
            {"description": "1 medium bowl (200g)", "grams": 200},
            {"description": "1 full plate (300g)", "grams": 300},
        ], ["khichdi", "dal khichdi", "yellow khichdi"], "Khichdi"),
        F("palak-khichdi", "Palak khichdi", "Grains", "Cooked with spinach puree, rice and moong dal", 135, 5.0, 23.0, 2.5, 3.0, 0.8, 190, 200, "bowl", None, ["spinach khichdi"], "Khichdi"),
        F("curd-rice", "Curd rice", "Grains", "Cooked rice mixed with dahi, mustard seed tadka", 145, 4.0, 22.0, 4.5, 0.8, 2.5, 160, 200, "bowl", [
            {"description": "1 medium bowl (200g)", "grams": 200},
        ], ["thayir sadam", "dahi bhat", "daddojanam"], "Rice Dishes"),
        F("lemon-rice", "Lemon rice", "Grains", "Cooked rice tempered with turmeric, peanuts, lemon", 175, 3.2, 32.0, 4.2, 1.0, 0.5, 220, 180, "bowl", None, ["chitranna", "nimbu chawal"], "Rice Dishes"),
        F("tamarind-rice", "Tamarind rice", "Grains", "Cooked rice tempered with tamarind pulp and sesame", 185, 3.5, 34.0, 4.5, 1.5, 1.2, 240, 180, "bowl", None, ["puliyodharai", "pulihora"], "Rice Dishes"),
        F("veg-fried-rice", "Vegetable fried rice", "Grains", "Wok-tossed rice with vegetables and light soy", 175, 4.0, 31.0, 4.2, 1.8, 1.0, 310, 200, "plate", [
            {"description": "1 plate (250g)", "grams": 250},
        ], ["fried rice", "chinese fried rice"], "Rice Dishes", image_key="rice"),
        F("egg-fried-rice", "Egg fried rice", "Grains", "Wok-tossed rice with scrambled egg and scallions", 190, 7.5, 28.0, 5.5, 1.2, 0.8, 330, 220, "plate", None, ["egg rice"], "Rice Dishes"),
        F("chicken-fried-rice", "Chicken fried rice", "Grains", "Wok-tossed rice with chicken cubes and soy", 205, 11.0, 27.0, 6.0, 1.2, 0.8, 340, 240, "plate", None, ["chicken rice"], "Rice Dishes"),
        F("schezwan-fried-rice", "Schezwan fried rice", "Grains", "Spicy wok-tossed rice with schezwan sauce", 185, 4.0, 32.0, 4.8, 1.5, 1.5, 380, 200, "plate", None, ["spicy fried rice"], "Rice Dishes"),
        F("wheat-atta", "Whole wheat flour (Atta)", "Grains", "Raw, stone-ground", 340, 12.0, 71.0, 1.8, 10.5, 1.5, 3, 50, "serving", [
            {"description": "1 cup atta (120g)", "grams": 120},
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["gehu atta", "chakki atta"], "Flours"),
        F("multigrain-atta", "Multigrain flour", "Grains", "Raw, composite flour with millets and soya", 345, 13.5, 68.0, 2.5, 11.5, 1.8, 5, 50, "serving", None, ["multigrain atta"], "Flours"),
        F("jowar-flour", "Jowar flour (Sorghum)", "Grains", "Raw, ground", 349, 10.4, 72.6, 1.9, 9.7, 1.0, 4, 50, "serving", None, ["sorghum flour", "jowar pitha"], "Flours"),
        F("bajra-flour", "Bajra flour (Pearl millet)", "Grains", "Raw, ground", 361, 11.6, 67.5, 5.0, 11.5, 1.2, 5, 50, "serving", None, ["pearl millet flour", "sajje"], "Flours"),
        F("ragi-flour", "Ragi flour (Finger millet)", "Grains", "Raw, ground", 328, 7.3, 72.0, 1.3, 11.5, 0.8, 6, 50, "serving", None, ["finger millet flour", "nachni pitha"], "Flours"),
        F("besan-flour", "Besan (Gram flour)", "Grains", "Raw, ground chana dal", 387, 22.4, 57.8, 6.7, 10.8, 2.5, 8, 30, "serving", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1/2 cup (60g)", "grams": 60},
        ], ["gram flour", "chickpea flour", "kadale hittu"], "Flours"),
        F("maida-flour", "Maida (Refined wheat flour)", "Grains", "Raw, refined", 364, 10.3, 76.3, 0.9, 2.7, 0.3, 2, 50, "serving", None, ["refined flour", "white flour"], "Flours"),
        F("suji-rava", "Suji / Rava (Semolina)", "Grains", "Raw, granulated wheat", 360, 12.7, 72.8, 1.0, 3.9, 0.5, 3, 50, "serving", None, ["semolina", "rawa", "sooji"], "Flours"),
        F("makki-atta", "Makki ka atta (Corn flour)", "Grains", "Raw, ground yellow maize", 365, 9.0, 74.0, 3.8, 7.0, 1.0, 4, 50, "serving", None, ["maize flour", "corn flour"], "Flours"),
        F("rice-flour", "Rice flour", "Grains", "Raw, finely milled white rice", 366, 6.0, 80.0, 1.4, 2.4, 0.2, 3, 50, "serving", None, ["chawal ka atta", "tandlache peeth"], "Flours"),
        F("kanda-poha", "Kanda poha", "Breakfast", "Flattened rice sautéed with onions, peanuts, mustard seeds", 180, 3.5, 32.0, 4.5, 2.0, 1.5, 220, 150, "plate", [
            {"description": "1 small katori (100g)", "grams": 100},
            {"description": "1 medium plate (150g)", "grams": 150},
            {"description": "1 large plate (220g)", "grams": 220},
        ], ["poha", "onion poha", "kande pohe"], "Poha"),
        F("batata-poha", "Batata poha", "Breakfast", "Flattened rice sautéed with diced potatoes and turmeric", 190, 3.2, 35.0, 4.5, 2.2, 1.2, 230, 160, "plate", None, ["aloo poha", "potato poha"], "Poha"),
        F("dalia-khichdi", "Vegetable dalia", "Breakfast", "Broken wheat cooked with vegetables and mild cumin", 120, 4.5, 22.0, 1.8, 4.0, 1.0, 170, 180, "bowl", [
            {"description": "1 medium bowl (180g)", "grams": 180},
        ], ["broken wheat", "dalia porridge", "lapsi"], "Porridge"),
        F("rava-upma", "Rava upma", "Breakfast", "Semolina porridge tempered with ginger, mustard seeds, curry leaves", 170, 4.0, 28.0, 4.8, 2.0, 0.8, 210, 160, "bowl", [
            {"description": "1 medium bowl (160g)", "grams": 160},
        ], ["sooji upma", "uppittu", "sanja"], "Upma"),
        F("semiya-upma", "Semiya upma (Vermicelli)", "Breakfast", "Wheat vermicelli cooked with vegetables and mustard tadka", 165, 3.8, 29.0, 4.2, 1.8, 0.8, 220, 160, "bowl", None, ["vermicelli upma"], "Upma"),
        F("oats-upma", "Vegetable oats upma", "Breakfast", "Rolled oats cooked with chopped carrots, peas and spices", 145, 4.8, 24.0, 3.8, 3.5, 1.0, 190, 160, "bowl", None, ["savory oats"], "Upma", image_key="oats"),
        F("sabudana-khichdi", "Sabudana khichdi", "Breakfast", "Tapioca pearls tossed with roasted peanuts, cumin, green chili", 240, 4.0, 42.0, 7.5, 1.8, 1.2, 180, 150, "plate", [
            {"description": "1 standard bowl (150g)", "grams": 150},
        ], ["tapioca khichdi", "sago khichdi"], "Fasting Foods"),
        F("sabudana-vada", "Sabudana vada", "Snacks", "Deep-fried tapioca pearl and potato fritters with peanuts", 310, 4.5, 44.0, 13.5, 2.2, 1.0, 240, 90, "serving (2 vadas)", [
            {"description": "1 vada (45g)", "grams": 45},
            {"description": "2 vadas (90g)", "grams": 90},
        ], ["sago vada"], "Fasting Foods"),
        F("thalipeeth", "Thalipeeth", "Breakfast", "Multi-grain roasted flatbread with onions, coriander and spices", 230, 6.5, 36.0, 6.8, 5.0, 1.2, 220, 100, "piece", [
            {"description": "1 piece (100g)", "grams": 100},
            {"description": "2 pieces (200g)", "grams": 200},
        ], ["bhajani thalipeeth", "maharashtrian thalipeeth"], "Breads"),
        F("oats-porridge-milk", "Oats porridge with milk", "Breakfast", "Rolled oats simmered in toned milk", 110, 4.5, 16.0, 2.8, 2.0, 4.2, 45, 200, "bowl", [
            {"description": "1 medium bowl (200g)", "grams": 200},
        ], ["oatmeal with milk"], "Cereals", image_key="oats"),
        F("cornflakes-milk", "Cornflakes with milk", "Breakfast", "Cornflakes served in cold milk", 125, 4.2, 21.0, 2.5, 1.0, 7.5, 140, 200, "bowl", None, ["corn flakes"], "Cereals"),
        F("muesli-milk", "Muesli with milk", "Breakfast", "Toasted grain and fruit muesli with milk", 155, 5.8, 24.0, 4.0, 3.0, 9.0, 110, 220, "bowl", None, ["swiss muesli"], "Cereals"),
        F("quinoa-cooked", "Cooked quinoa", "Grains", "Boiled with water", 120, 4.4, 21.3, 1.9, 2.8, 0.9, 7, 150, "bowl", [
            {"description": "1 cup (185g)", "grams": 185},
            {"description": "1/2 cup (92g)", "grams": 92},
        ], ["quinoa", "boiled quinoa"], "Grains"),
    ])

    # =========================================================================
    # GROUP 2: INDIAN FLATBREADS & ROTIS (~45 items)
    # =========================================================================
    items.extend([
        F("roti-butter", "Butter roti", "Bread", "Cooked on tawa, brushed with butter", 280, 7.5, 46.0, 7.5, 5.5, 1.5, 160, 40, "piece", [
            {"description": "1 butter roti (40g)", "grams": 40},
            {"description": "2 butter rotis (80g)", "grams": 80},
        ], ["butter chapati", "makkhan roti"], "Indian Flatbreads", image_key="roti"),
        F("roti-ghee", "Ghee roti", "Bread", "Cooked on tawa, brushed with desi cow ghee", 295, 7.5, 46.0, 9.0, 5.5, 1.5, 120, 40, "piece", [
            {"description": "1 ghee chapati (40g)", "grams": 40},
            {"description": "2 ghee chapatis (80g)", "grams": 80},
        ], ["ghee chapati", "tupatli poli"], "Indian Flatbreads", image_key="roti"),
        F("phulka", "Phulka (Puffed dry roti)", "Bread", "Cooked on flame without oil", 240, 8.5, 48.0, 2.0, 6.0, 1.4, 110, 30, "piece", [
            {"description": "1 small phulka (30g)", "grams": 30},
            {"description": "2 phulkas (60g)", "grams": 60},
            {"description": "3 phulkas (90g)", "grams": 90},
        ], ["phulka roti", "dry roti"], "Indian Flatbreads", image_key="roti"),
        F("jowar-bhakri", "Jowar bhakri", "Bread", "Hand-flattened sorghum bread roasted on tawa", 220, 6.5, 46.0, 1.2, 6.2, 0.8, 15, 80, "piece", [
            {"description": "1 bhakri (80g)", "grams": 80},
            {"description": "1/2 bhakri (40g)", "grams": 40},
        ], ["sorghum bhakri", "jowar roti", "jowar rotti"], "Bhakri"),
        F("bajra-bhakri", "Bajra bhakri", "Bread", "Pearl millet flatbread roasted on tawa", 235, 7.5, 44.0, 3.2, 7.5, 1.0, 18, 85, "piece", [
            {"description": "1 bhakri (85g)", "grams": 85},
        ], ["pearl millet bhakri", "bajre ki roti"], "Bhakri"),
        F("ragi-roti", "Ragi roti", "Bread", "Finger millet flatbread with cumin, onions and chili", 215, 5.0, 46.0, 1.0, 7.2, 0.6, 20, 75, "piece", [
            {"description": "1 ragi roti (75g)", "grams": 75},
        ], ["nachni roti", "finger millet roti"], "Bhakri"),
        F("tandoori-roti", "Tandoori roti", "Bread", "Whole wheat bread baked in clay tandoor", 245, 8.0, 48.0, 2.5, 5.8, 1.2, 140, 45, "piece", [
            {"description": "1 tandoori roti (45g)", "grams": 45},
            {"description": "2 tandoori rotis (90g)", "grams": 90},
        ], ["tandoori chapati"], "Indian Flatbreads", image_key="roti"),
        F("tandoori-roti-butter", "Tandoori butter roti", "Bread", "Baked in tandoor, brushed with butter", 275, 7.5, 46.0, 7.0, 5.5, 1.2, 180, 50, "piece", None, ["butter tandoori roti"], "Indian Flatbreads", image_key="roti"),
        F("naan-plain", "Plain naan", "Bread", "Refined flour leavened flatbread baked in tandoor", 285, 8.5, 50.0, 5.5, 2.5, 2.0, 320, 90, "piece", [
            {"description": "1 piece (90g)", "grams": 90},
        ], ["naan", "tandoori naan"], "Naan"),
        F("naan-butter", "Butter naan", "Bread", "Tandoor-baked naan coated with melted butter", 330, 8.0, 48.0, 11.5, 2.4, 2.0, 360, 100, "piece", [
            {"description": "1 butter naan (100g)", "grams": 100},
        ], ["makkhan naan"], "Naan"),
        F("naan-garlic", "Garlic naan", "Bread", "Tandoor naan topped with minced garlic and butter", 310, 8.2, 49.0, 9.0, 2.6, 2.2, 340, 100, "piece", [
            {"description": "1 garlic naan (100g)", "grams": 100},
        ], ["lasooni naan"], "Naan"),
        F("rumali-roti", "Rumali roti", "Bread", "Thin handkerchief-style soft flatbread cooked on inverted kadai", 270, 7.5, 52.0, 3.5, 2.5, 1.5, 180, 60, "piece", [
            {"description": "1 rumali roti (60g)", "grams": 60},
        ], ["roomali roti", "manda roti"], "Indian Flatbreads"),
        F("paratha-plain", "Plain paratha", "Bread", "Shallow-fried layered whole wheat flatbread", 320, 6.5, 45.0, 13.0, 4.5, 1.2, 220, 65, "piece", [
            {"description": "1 paratha (65g)", "grams": 65},
            {"description": "2 parathas (130g)", "grams": 130},
        ], ["tawa paratha", "plain paratha"], "Parathas"),
        F("paratha-aloo", "Aloo paratha", "Bread", "Whole wheat flatbread stuffed with spiced potato mash", 260, 5.5, 38.0, 9.8, 4.0, 1.2, 280, 110, "piece", [
            {"description": "1 medium aloo paratha (110g)", "grams": 110},
            {"description": "1 large dhaba paratha (160g)", "grams": 160},
        ], ["potato paratha", "alu paratha"], "Parathas"),
        F("paratha-gobi", "Gobi paratha", "Bread", "Whole wheat bread stuffed with grated spiced cauliflower", 230, 5.8, 34.0, 8.2, 4.5, 1.5, 260, 110, "piece", None, ["cauliflower paratha"], "Parathas"),
        F("paratha-paneer", "Paneer paratha", "Bread", "Whole wheat bread stuffed with grated spiced paneer", 295, 9.5, 35.0, 13.0, 3.8, 1.8, 290, 120, "piece", [
            {"description": "1 paneer paratha (120g)", "grams": 120},
        ], ["cottage cheese paratha"], "Parathas"),
        F("paratha-mooli", "Mooli paratha", "Bread", "Whole wheat flatbread stuffed with grated white radish", 225, 5.2, 33.0, 8.0, 4.2, 1.5, 270, 110, "piece", None, ["radish paratha"], "Parathas"),
        F("paratha-laccha", "Laccha paratha", "Bread", "Multi-layered flaky whole wheat bread shallow-fried with ghee", 350, 6.0, 44.0, 16.5, 3.5, 1.0, 240, 80, "piece", [
            {"description": "1 laccha paratha (80g)", "grams": 80},
        ], ["layered paratha", "flaky paratha"], "Parathas"),
        F("thepla-methi", "Methi thepla", "Bread", "Spiced whole wheat and fenugreek leaf flatbread", 275, 7.2, 40.0, 9.5, 5.5, 1.5, 260, 45, "piece", [
            {"description": "1 thepla (45g)", "grams": 45},
            {"description": "2 theplas (90g)", "grams": 90},
            {"description": "3 theplas (135g)", "grams": 135},
        ], ["fenugreek thepla", "gujarati thepla"], "Thepla"),
        F("kulcha-plain", "Plain kulcha", "Bread", "Mildly leavened refined flour bread baked on tawa", 275, 7.5, 52.0, 3.8, 2.5, 2.0, 310, 80, "piece", [
            {"description": "1 kulcha (80g)", "grams": 80},
        ], ["tandoori kulcha"], "Kulcha"),
        F("kulcha-amritsari", "Amritsari kulcha", "Bread", "Crispy stuffed potato-onion leavened bread with butter", 310, 7.0, 46.0, 11.0, 3.2, 2.0, 380, 130, "piece", [
            {"description": "1 amritsari kulcha (130g)", "grams": 130},
        ], ["stuffed kulcha"], "Kulcha"),
        F("puri", "Puri (Poori)", "Bread", "Deep-fried unleavened whole wheat puffed bread", 390, 7.0, 48.0, 19.5, 4.0, 1.0, 160, 30, "piece", [
            {"description": "1 puri (30g)", "grams": 30},
            {"description": "3 puris (90g)", "grams": 90},
            {"description": "4 puris (120g)", "grams": 120},
        ], ["fried poori", "deep fried bread"], "Puris"),
        F("bhatura", "Bhatura", "Bread", "Deep-fried leavened maida bread served with chole", 380, 7.5, 50.0, 17.0, 2.5, 2.0, 320, 80, "piece", [
            {"description": "1 bhatura (80g)", "grams": 80},
            {"description": "2 bhaturas (160g)", "grams": 160},
        ], ["chole bhature bread", "bhature"], "Puris"),
        F("luchi", "Luchi", "Bread", "Deep-fried refined flour Bengali puffed bread", 410, 6.5, 49.0, 21.0, 2.0, 0.8, 140, 25, "piece", None, ["bengali luchi"], "Puris"),
    ])

    # =========================================================================
    # GROUP 3: DALS, LEGUMES & PULSES (~65 items)
    # =========================================================================
    items.extend([
        F("dal-tadka", "Yellow Dal Tadka", "Pulses", "Boiled yellow toor/moong dal with ghee, garlic, cumin tadka", 135, 6.5, 18.0, 4.2, 3.8, 1.2, 240, 180, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 restaurant bowl (220g)", "grams": 220},
        ], ["yellow dal", "dal tadka", "arhar dal tadka"], "Dals", image_key="dal"),
        F("dal-fry", "Dal Fry", "Pulses", "Thick cooked lentils tossed with sautéed onions, tomatoes, coriander", 145, 6.2, 18.0, 5.5, 3.5, 1.8, 260, 180, "katori", None, ["dal fry restaurant style"], "Dals", image_key="dal"),
        F("dal-makhani", "Dal Makhani", "Pulses", "Slow-cooked black urad lentils and kidney beans with butter, cream", 180, 5.8, 16.0, 10.5, 4.5, 1.5, 310, 200, "bowl", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["maa ki dal", "black dal", "creamy dal"], "Dals"),
        F("toor-dal-cooked", "Toor dal (Boiled plain)", "Pulses", "Cooked split pigeon peas boiled with water and salt", 118, 7.2, 19.5, 1.2, 4.2, 0.8, 120, 150, "katori", None, ["arhar dal", "tuvar dal boiled"], "Dals"),
        F("toor-dal-raw", "Toor dal (Raw dry)", "Pulses", "Raw split pigeon peas", 343, 22.0, 62.7, 1.5, 15.0, 2.5, 17, 40, "serving", None, ["raw arhar dal", "uncooked toor dal"], "Raw Pulses"),
        F("masoor-dal-cooked", "Cooked Masoor dal (Red lentil)", "Pulses", "Cooked split red lentils with mild turmeric", 116, 9.0, 20.0, 0.4, 3.8, 0.9, 110, 150, "katori", None, ["red lentil dal", "lal masoor"], "Dals"),
        F("masoor-dal-raw", "Masoor dal (Raw dry)", "Pulses", "Raw split red lentils", 352, 24.6, 63.0, 1.1, 10.7, 2.0, 6, 40, "serving", None, ["uncooked red lentils", "raw masoor"], "Raw Pulses"),
        F("urad-dal-cooked", "Cooked Urad dal", "Pulses", "Split black gram cooked with ginger and cumin", 125, 8.0, 21.0, 0.8, 4.5, 0.5, 130, 150, "katori", None, ["white urad dal", "dhuli urad"], "Dals"),
        F("chana-dal-cooked", "Cooked Chana dal", "Pulses", "Cooked Bengal gram split dal with tadka", 140, 8.5, 22.0, 2.0, 5.5, 1.0, 160, 150, "katori", None, ["bengal gram dal", "chana dal"], "Dals"),
        F("chana-dal-raw", "Chana dal (Raw dry)", "Pulses", "Raw split Bengal gram", 370, 21.0, 60.0, 5.6, 15.0, 2.5, 25, 40, "serving", None, ["raw bengal gram", "uncooked chana dal"], "Raw Pulses"),
        F("panchmel-dal", "Panchmel dal (Panchratna)", "Pulses", "Five lentils (toor, moong, chana, masoor, urad) simmered with spices", 130, 7.5, 19.0, 2.8, 4.2, 1.0, 210, 180, "katori", None, ["panchratna dal", "rajasthani dal"], "Dals"),
        F("sambar", "Vegetable Sambar", "Pulses", "Toor dal cooked with drumstick, pumpkin, tamarind, sambar masala", 95, 3.8, 14.0, 2.5, 2.8, 2.2, 290, 200, "bowl", [
            {"description": "1 small katori (120g)", "grams": 120},
            {"description": "1 medium bowl (200g)", "grams": 200},
        ], ["south indian sambar", "sambar soup"], "South Indian", image_key="dal"),
        F("rasam", "Tomato Rasam", "Pulses", "Light spiced lentil and tamarind soup with black pepper, cumin", 45, 1.5, 7.5, 1.0, 1.0, 1.5, 280, 180, "cup", [
            {"description": "1 cup (180g)", "grams": 180},
        ], ["pepper rasam", "saaru", "tomato charu"], "South Indian"),
        F("punjabi-kadhi-pakora", "Punjabi Kadhi Pakora", "Curries", "Sour curd and besan gravy with fried onion-gram flour pakoras", 145, 4.5, 13.0, 8.2, 2.0, 2.5, 340, 200, "bowl", [
            {"description": "1 bowl with 2 pakoras (200g)", "grams": 200},
        ], ["kadhi pakora", "punjabi kadhi"], "Kadhi"),
        F("gujarati-kadhi", "Gujarati Kadhi", "Curries", "Sweet and tangy light curd and besan soup tempered with cinnamon", 85, 2.5, 11.0, 3.2, 0.5, 5.5, 260, 180, "katori", None, ["sweet kadhi"], "Kadhi"),
        F("varan", "Maharashtrian Varan", "Pulses", "Simple boiled toor dal tempered with ghee, cumin and asafoetida", 115, 6.8, 19.0, 1.5, 4.0, 0.8, 140, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["varan bhaat dal", "god varan"], "Dals"),
        F("amti", "Maharashtrian Katachi Amti", "Pulses", "Tangy, spicy dal made with chana dal extract, goda masala, kokum", 125, 6.0, 18.0, 3.2, 3.5, 2.8, 270, 160, "katori", None, ["katachi amti", "marathi amti"], "Dals"),
        F("chole-masala", "Chole Masala (Chickpea curry)", "Pulses", "White chickpeas simmered in spicy onion-tomato gravy", 165, 6.8, 22.0, 5.8, 5.2, 2.5, 340, 200, "bowl", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (220g)", "grams": 220},
        ], ["punjabi chole", "chana masala"], "Legumes", image_key="chickpeas"),
        F("pindi-chana", "Pindi Chana (Dry chickpeas)", "Pulses", "Dark spiced dry chickpeas cooked with anardana and amchur", 175, 7.5, 24.0, 5.5, 5.8, 1.8, 320, 180, "katori", None, ["rawalpindi chana"], "Legumes"),
        F("rajma-masala", "Rajma Masala (Kidney bean curry)", "Pulses", "Red kidney beans cooked in tomato, ginger, garlic onion gravy", 155, 7.5, 21.0, 4.8, 5.8, 2.2, 320, 200, "bowl", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl with gravy (220g)", "grams": 220},
        ], ["rajma chawal curry", "punjabi rajma"], "Legumes"),
        F("rajma-boiled", "Boiled Kidney beans (Plain)", "Pulses", "Boiled red kidney beans with light salt", 127, 8.7, 22.8, 0.5, 6.4, 0.3, 110, 150, "cup", None, ["boiled rajma", "red beans plain"], "Legumes"),
        F("kala-chana-curry", "Kala Chana Curry", "Pulses", "Brown chickpeas cooked in light spiced thin gravy (tari)", 160, 8.0, 22.0, 4.5, 6.5, 1.5, 280, 180, "katori", None, ["black chickpea curry", "tariwale chane"], "Legumes"),
        F("kala-chana-sukha", "Sukha Kala Chana", "Pulses", "Dry boiled brown chickpeas tossed with cumin, amchur and coriander", 185, 9.5, 26.0, 4.8, 7.2, 1.2, 240, 120, "katori", None, ["ashtami chana", "prasad chana"], "Legumes"),
        F("lobia-curry", "Lobia Curry (Black-eyed peas)", "Pulses", "Black-eyed peas cooked in onion-tomato gravy", 145, 7.2, 21.0, 3.8, 5.5, 1.8, 290, 180, "katori", None, ["chawli curry", "black eyed bean masala"], "Legumes"),
        F("matki-usal", "Matki Usal (Moth bean curry)", "Pulses", "Sprouted moth beans cooked with mustard, curry leaves, coconut", 150, 7.0, 19.0, 5.2, 5.2, 2.0, 260, 160, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["moth bean usal", "sprout curry"], "Maharashtrian"),
        F("moong-sprouts-boiled", "Boiled Sprouted Moong", "Pulses", "Lightly steamed sprouted mung beans with salt and turmeric", 95, 6.8, 17.0, 0.3, 4.0, 1.8, 80, 120, "cup", [
            {"description": "1 cup (150g)", "grams": 150},
        ], ["steamed sprouts", "boiled mung"], "Sprouts"),
        F("moong-sprouts-raw", "Raw Sprouted Moong", "Pulses", "Fresh uncooked sprouted mung beans", 105, 7.5, 19.0, 0.2, 4.5, 2.0, 15, 100, "cup", None, ["raw sprouts", "mung sprouts"], "Sprouts"),
        F("ragda", "Ragda (White peas curry)", "Pulses", "Mashed dried white peas cooked with turmeric and cumin", 140, 6.8, 22.0, 3.2, 5.0, 1.8, 260, 180, "bowl", None, ["ragda pattice base", "safed vatana curry"], "Legumes"),
    ])

    # =========================================================================
    # GROUP 4: VEGETARIAN CURRIES, SABZIS & GRAVIES (~90 items)
    # =========================================================================
    items.extend([
        F("paneer-butter-masala", "Paneer Butter Masala", "Curries", "Paneer cubes in creamy tomato cashew butter gravy", 220, 7.5, 10.0, 18.0, 1.8, 4.5, 340, 200, "bowl", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 restaurant bowl (220g)", "grams": 220},
        ], ["paneer makhani", "butter paneer"], "Paneer Dishes", image_key="paneer"),
        F("palak-paneer", "Palak Paneer", "Curries", "Paneer cubes in vibrant spiced spinach puree", 160, 8.5, 6.0, 11.5, 2.8, 1.8, 280, 200, "bowl", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["spinach paneer"], "Paneer Dishes", image_key="paneer"),
        F("matar-paneer", "Matar Paneer", "Curries", "Paneer and green peas cooked in spiced tomato onion gravy", 175, 8.0, 11.0, 10.5, 2.5, 3.0, 290, 200, "bowl", None, ["peas paneer curry"], "Paneer Dishes", image_key="paneer"),
        F("kadai-paneer", "Kadai Paneer", "Curries", "Paneer, bell peppers, onions cooked in freshly ground coriander-chili spice", 195, 8.2, 8.5, 14.5, 2.2, 2.8, 310, 200, "bowl", None, ["karahi paneer"], "Paneer Dishes", image_key="paneer"),
        F("shahi-paneer", "Shahi Paneer", "Curries", "Royal paneer curry in rich white cashew, yogurt and melon seed gravy", 235, 7.0, 9.0, 19.5, 1.5, 4.0, 320, 200, "bowl", None, ["mughlai paneer"], "Paneer Dishes", image_key="paneer"),
        F("paneer-bhurji", "Paneer Bhurji", "Curries", "Scrambled paneer sautéed with onions, tomatoes, green chilies", 240, 14.0, 5.0, 18.5, 1.2, 2.2, 310, 150, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
            {"description": "1 plate (180g)", "grams": 180},
        ], ["scrambled cottage cheese"], "Paneer Dishes", image_key="paneer"),
        F("paneer-tikka", "Paneer Tikka (Tandoori)", "Snacks", "Marinated paneer, capsicum, onion cubes grilled in tandoor", 220, 13.5, 7.0, 15.5, 1.8, 2.5, 340, 150, "serving (6 cubes)", [
            {"description": "6 cubes (150g)", "grams": 150},
        ], ["tandoori paneer tikka", "grilled paneer"], "Paneer Dishes", image_key="paneer"),
        F("malai-kofta", "Malai Kofta", "Curries", "Fried paneer and potato dumplings in rich creamy cashew tomato gravy", 255, 5.5, 18.0, 18.5, 2.2, 5.0, 360, 200, "bowl", None, ["paneer kofta curry"], "Curries"),
        F("aloo-gobi", "Aloo Gobi (Dry sabzi)", "Curries", "Potatoes and cauliflower florets sautéed with turmeric, ginger, cumin", 115, 2.5, 14.0, 5.5, 3.2, 2.2, 240, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
            {"description": "1 cup (180g)", "grams": 180},
        ], ["potato cauliflower", "alu gobi"], "Dry Sabzi"),
        F("bhindi-masala", "Bhindi Masala (Okra sabzi)", "Curries", "Sliced okra sautéed with onions, amchur and garam masala", 110, 2.8, 11.5, 6.0, 3.5, 2.0, 210, 140, "katori", [
            {"description": "1 katori (140g)", "grams": 140},
        ], ["okra sabzi", "ladyfinger curry"], "Dry Sabzi"),
        F("baingan-bharta", "Baingan Bharta", "Curries", "Smoked roasted eggplant mashed and cooked with garlic, onions, tomatoes", 105, 2.2, 9.0, 6.8, 3.8, 2.8, 230, 160, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["roasted eggplant mash", "vange bharit"], "Dry Sabzi"),
        F("aloo-matar", "Aloo Matar (Curry)", "Curries", "Potatoes and green peas in light tomato onion gravy", 125, 3.2, 18.0, 4.5, 3.0, 2.5, 260, 180, "katori", None, ["potato peas curry"], "Curries"),
        F("aloo-methi", "Aloo Methi", "Curries", "Diced potatoes cooked with fresh bitter fenugreek leaves", 120, 3.0, 15.0, 5.5, 3.2, 1.2, 220, 140, "katori", None, ["potato fenugreek"], "Dry Sabzi"),
        F("jeera-aloo", "Jeera Aloo", "Curries", "Boiled potatoes tempered with toasted cumin seeds, green chili, lemon", 130, 2.2, 19.0, 5.2, 2.2, 1.0, 240, 140, "katori", None, ["cumin potatoes"], "Dry Sabzi", image_key="potato"),
        F("cabbage-peas-sabzi", "Cabbage Peas Sabzi (Patta Gobi)", "Curries", "Shredded cabbage and green peas tempered with mustard and turmeric", 85, 2.5, 9.5, 4.2, 2.8, 3.0, 190, 140, "katori", None, ["patta gobhi", "kobi bhaji"], "Dry Sabzi"),
        F("lauki-sabzi", "Lauki Sabzi (Bottle gourd)", "Curries", "Bottle gourd cubes simmered with cumin, green chilies and light ghee", 70, 1.5, 7.5, 3.8, 2.0, 2.5, 170, 150, "katori", None, ["dudhi sabzi", "ghiya sabzi"], "Dry Sabzi"),
        F("torai-sabzi", "Torai Sabzi (Ridge gourd)", "Curries", "Ridge gourd cooked with onions, turmeric and mild spices", 65, 1.2, 7.0, 3.5, 2.2, 2.2, 160, 150, "katori", None, ["turai", "dodka bhaji"], "Dry Sabzi"),
        F("karela-sabzi", "Karela Sabzi (Bitter gourd)", "Curries", "Sliced bitter gourd sautéed with onions, jaggery and amchur", 95, 2.0, 10.5, 5.0, 3.2, 3.5, 210, 120, "katori", None, ["bitter melon sabzi"], "Dry Sabzi"),
        F("pav-bhaji", "Pav Bhaji (Bhaji only)", "Curries", "Mashed spiced vegetables (potato, peas, tomato, cauliflower) with butter", 155, 3.8, 16.0, 8.5, 3.5, 3.2, 380, 200, "bowl", [
            {"description": "1 bowl bhaji (200g)", "grams": 200},
        ], ["bombay pav bhaji", "bhaji curry"], "Street Food"),
        F("misal-tarri", "Misal (Usal + spicy rassa)", "Curries", "Sprouted moth beans in fiery thin gravy with ginger, garlic, coconut", 160, 6.5, 16.0, 8.0, 4.2, 1.8, 420, 220, "bowl", [
            {"description": "1 bowl misal curry (220g)", "grams": 220},
        ], ["puneri misal", "kolhapuri misal"], "Maharashtrian"),
        F("pithla", "Pithla (Besan curry)", "Curries", "Thick gram flour slurry cooked with garlic, onions, mustard seeds", 140, 6.2, 14.0, 6.5, 3.0, 1.5, 290, 150, "katori", [
            {"description": "1 katori (150g)", "grams": 150},
        ], ["zunka", "besan pithla", "pithla bhakri curry"], "Maharashtrian"),
        F("veg-korma", "Vegetable Korma", "Curries", "Mixed vegetables simmered in coconut cashew poppy seed gravy", 145, 3.2, 12.0, 9.5, 3.0, 3.2, 260, 200, "bowl", None, ["kurma", "navratan korma"], "Curries"),
        F("sarson-ka-saag", "Sarson ka Saag", "Curries", "Slow-cooked mustard greens, spinach, bathua with makki atta and white butter", 125, 4.2, 8.5, 8.0, 4.5, 1.8, 270, 200, "bowl", [
            {"description": "1 bowl saag (200g)", "grams": 200},
        ], ["mustard greens saag", "punjabi saag"], "Curries"),
        F("dum-aloo", "Dum Aloo (Kashmiri / Banarasi)", "Curries", "Baby potatoes simmered in rich spiced fennel yogurt or tomato gravy", 160, 2.8, 20.0, 7.8, 2.5, 2.2, 310, 180, "katori", None, ["kashmiri dum aloo"], "Curries", image_key="potato"),
        F("methi-malai-matar", "Methi Malai Matar", "Curries", "Fenugreek leaves and green peas in smooth creamy cashew gravy", 190, 4.5, 13.0, 13.5, 3.2, 3.8, 280, 180, "bowl", None, ["creamy methi peas"], "Curries"),
        F("shevga-bhaji", "Shevga Bhaji (Drumstick curry)", "Curries", "Drumsticks cooked in spiced coconut onion Maharashtrian masala", 115, 3.5, 12.0, 5.8, 4.0, 2.0, 260, 160, "katori", None, ["drumstick curry", "sahjan ki sabzi"], "Maharashtrian"),
    ])

    return items

print("Catalogue part 1 loaded.")
