"""
Catalogue data part 7: Global Asian Dishes, Soups, International Salads, Mediterranean, Mexican (~180 items).
"""

from scripts.build_full_database import F

def get_part7():
    items = []

    # =========================================================================
    # ASIAN & INDO-CHINESE MAINS (~50 items)
    # =========================================================================
    items.extend([
        F("pad-thai-chicken", "Chicken Pad Thai", "Fast Food", "Stir-fried rice noodles with chicken, bean sprouts, crushed peanuts, tamarind", 195, 11.5, 26.0, 5.2, 1.8, 4.5, 420, 250, "plate", [
            {"description": "1 plate (250g)", "grams": 250},
        ], ["pad thai", "thai noodles"], "Asian"),
        F("pad-thai-veg", "Vegetable Pad Thai with Tofu", "Fast Food", "Stir-fried rice noodles with pressed tofu, vegetables, peanuts", 175, 7.5, 27.0, 4.5, 2.2, 4.5, 380, 240, "plate", [
            {"description": "1 plate (240g)", "grams": 240},
        ], ["veg pad thai", "tofu pad thai"], "Asian"),
        F("lo-mein-chicken", "Chicken Lo Mein", "Fast Food", "Egg noodles tossed with chicken breast strips, bok choy, soy sauce", 180, 11.0, 24.0, 4.8, 1.8, 2.5, 440, 220, "plate", [
            {"description": "1 plate (220g)", "grams": 220},
        ], ["chicken lo mein"], "Asian"),
        F("lo-mein-veg", "Vegetable Lo Mein", "Fast Food", "Egg noodles tossed with cabbage, carrots, snow peas and light sesame soy", 155, 4.8, 26.0, 3.8, 2.2, 2.5, 390, 200, "plate", None, ["veg lo mein"], "Asian"),
        F("singapore-noodles", "Singapore Rice Noodles", "Fast Food", "Thin vermicelli noodles stir-fried with curry powder, bell peppers, scallions", 165, 4.5, 28.0, 4.2, 2.0, 2.0, 420, 220, "plate", None, ["curry rice vermicelli"], "Asian"),
        F("chicken-teriyaki-bowl", "Chicken Teriyaki with Rice", "Fast Food", "Grilled chicken thigh glazed with sweet teriyaki sauce over steamed white rice", 175, 12.0, 24.0, 3.5, 0.8, 6.5, 410, 300, "bowl", [
            {"description": "1 teriyaki bowl (300g)", "grams": 300},
        ], ["teriyaki chicken bowl", "chicken teriyaki"], "Asian"),
        F("beef-and-broccoli", "Beef and Broccoli Stir-fry", "Fast Food", "Flank steak slices sautéed with fresh broccoli in brown garlic ginger sauce", 145, 13.5, 8.5, 6.8, 2.2, 3.2, 480, 220, "serving", [
            {"description": "1 serving (220g)", "grams": 220},
        ], ["chinese beef and broccoli"], "Asian"),
        F("kung-pao-chicken", "Kung Pao Chicken", "Fast Food", "Diced chicken breast stir-fried with peanuts, dried red chilies, szechuan sauce", 185, 14.5, 10.0, 10.0, 2.0, 4.0, 460, 220, "serving", [
            {"description": "1 serving (220g)", "grams": 220},
        ], ["gong bao chicken"], "Asian"),
        F("orange-chicken-crispy", "Orange Chicken (Crispy)", "Fast Food", "Crispy battered chicken nuggets tossed in sweet tangy orange glaze", 260, 12.0, 28.0, 11.5, 1.0, 16.0, 520, 200, "serving", [
            {"description": "1 serving (200g)", "grams": 200},
        ], ["panda orange chicken"], "Asian"),
        F("sweet-and-sour-chicken", "Sweet and Sour Chicken", "Fast Food", "Crispy chicken pieces with pineapple, bell peppers in bright sweet-sour sauce", 215, 11.0, 26.0, 7.8, 1.2, 14.0, 380, 220, "serving", None, ["sweet sour chicken"], "Asian"),
        F("mapo-tofu", "Mapo Tofu (Szechuan)", "Curries", "Silken tofu cubes and minced meat in fiery fermented black bean chili oil sauce", 155, 9.5, 6.5, 10.5, 1.5, 1.8, 440, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["szechuan mapo tofu", "spicy tofu"], "Asian"),
        F("edamame-steamed", "Steamed Edamame (In pods)", "Snacks", "Immature green soybeans steamed in pods with sea salt", 122, 11.9, 8.9, 5.2, 5.2, 2.2, 240, 100, "serving (pods)", [
            {"description": "1 cup in pods (155g)", "grams": 155},
        ], ["steamed soybeans", "edamame pods"], "Asian"),
        F("gyoza-chicken", "Chicken Gyoza / Potstickers (Pan fried)", "Snacks", "Pan-fried Japanese dumplings filled with ground chicken and cabbage", 210, 10.5, 24.0, 8.0, 1.5, 1.8, 440, 90, "serving (4 dumplings)", [
            {"description": "4 dumplings (90g)", "grams": 90},
            {"description": "6 dumplings (135g)", "grams": 135},
        ], ["potstickers", "chicken dumplings"], "Asian"),
        F("gyoza-veg", "Vegetable Dumplings / Momos (Steamed)", "Snacks", "Steamed wheat flour momos stuffed with finely shredded cabbage, carrots, onion", 155, 4.5, 28.0, 2.8, 2.0, 2.2, 320, 100, "serving (5 momos)", [
            {"description": "5 steamed momos (100g)", "grams": 100},
            {"description": "8 steamed momos (160g)", "grams": 160},
        ], ["veg momos", "steamed dim sum"], "Asian"),
        F("chicken-momos-steamed", "Chicken Momos (Steamed)", "Snacks", "Steamed Tibetan dumplings filled with spiced ground chicken and coriander", 175, 11.0, 23.0, 4.5, 1.2, 1.5, 360, 100, "serving (5 momos)", [
            {"description": "5 steamed momos (100g)", "grams": 100},
        ], ["steamed chicken momos"], "Asian"),
        F("manchurian-veg-dry", "Vegetable Manchurian (Dry)", "Snacks", "Crisp fried vegetable balls tossed with ginger, garlic, green chilies, soy", 195, 4.2, 22.0, 10.2, 2.8, 3.5, 490, 150, "plate", [
            {"description": "1 plate (150g)", "grams": 150},
        ], ["veg manchurian dry", "gobi manchurian"], "Indo-Chinese"),
        F("manchurian-veg-gravy", "Vegetable Manchurian (Gravy)", "Curries", "Fried vegetable balls simmered in thick tangy garlic-soy sauce", 155, 3.5, 19.0, 7.5, 2.5, 3.8, 460, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["manchurian gravy"], "Indo-Chinese"),
        F("paneer-chilli-dry", "Chilli Paneer (Dry)", "Snacks", "Crispy paneer cubes tossed with capsicum, onion, dark soy, green chilies", 240, 11.5, 14.0, 15.5, 1.8, 3.5, 480, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["chilli paneer dry"], "Indo-Chinese", image_key="paneer"),
        F("chicken-chilli-dry", "Chilli Chicken (Dry)", "Snacks", "Boneless chicken cubes stir-fried with green chilies, bell peppers, garlic soy", 215, 20.5, 11.0, 9.8, 1.2, 2.5, 510, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["chilli chicken dry", "indo chinese chilli chicken"], "Indo-Chinese"),
        F("honey-chilli-potato", "Honey Chilli Potato", "Snacks", "Crispy deep-fried potato fingers glazed in sweet-spicy honey sesame sauce", 260, 2.8, 42.0, 9.5, 2.5, 12.0, 380, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["chilli potato"], "Indo-Chinese", image_key="potato"),
    ])

    # =========================================================================
    # SOUPS & SALADS (~40 items)
    # =========================================================================
    items.extend([
        F("soup-miso-tofu", "Miso Soup with Tofu & Seaweed", "Soups", "Traditional Japanese fermented soybean paste broth with diced silken tofu", 35, 2.5, 3.8, 1.2, 0.8, 1.2, 490, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["miso soup", "japanese soup"], "Soups"),
        F("soup-tom-yum", "Tom Yum Soup (Shrimp)", "Soups", "Spicy and sour Thai lemongrass broth with shrimp, lime leaves, galangal", 55, 5.5, 4.5, 1.8, 0.8, 2.2, 540, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["tom yum goong", "thai sour soup"], "Soups"),
        F("soup-hot-and-sour-veg", "Hot and Sour Soup (Vegetable)", "Soups", "Peppery and tangy soup with mushrooms, bamboo shoots, tofu, vinegar", 48, 2.2, 6.8, 1.5, 1.2, 1.5, 460, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["hot and sour soup"], "Soups"),
        F("soup-sweet-corn-veg", "Sweet Corn Vegetable Soup", "Soups", "Creamy sweet corn kernels with diced carrots, beans in mild broth", 58, 1.8, 11.5, 0.8, 1.5, 4.2, 380, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["sweet corn soup", "corn soup"], "Soups"),
        F("soup-manchow-veg", "Vegetable Manchow Soup", "Soups", "Dark spicy garlic coriander soup served with crispy fried noodles on top", 65, 2.0, 9.8, 2.2, 1.4, 1.8, 480, 240, "bowl", [
            {"description": "1 bowl with noodles (240ml)", "grams": 240},
        ], ["manchow soup"], "Soups"),
        F("soup-tomato-basil", "Tomato Basil Soup", "Soups", "Pureed ripe plum tomatoes simmered with fresh basil, light cream", 68, 1.5, 10.2, 2.6, 1.8, 6.5, 420, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["tomato soup", "creamy tomato soup"], "Soups", image_key="tomato"),
        F("soup-minestrone", "Minestrone Soup", "Soups", "Hearty Italian vegetable soup with beans, diced tomatoes, zucchini, pasta", 58, 2.8, 9.5, 1.0, 2.2, 2.8, 410, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["italian minestrone"], "Soups"),
        F("soup-chicken-noodle", "Chicken Noodle Soup", "Soups", "Clear chicken broth with pulled chicken breast, egg noodles, celery, carrots", 62, 5.2, 6.8, 1.5, 0.8, 1.0, 480, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["chicken soup with noodles"], "Soups"),
        F("soup-lentil-middle-east", "Middle Eastern Lentil Soup (Shorba)", "Soups", "Pureed red lentils simmered with cumin, carrots, onions, lemon juice", 75, 4.2, 12.0, 1.4, 3.2, 1.8, 380, 240, "bowl", [
            {"description": "1 bowl (240ml)", "grams": 240},
        ], ["red lentil shorba", "arabic lentil soup"], "Soups"),
        F("salad-greek-feta", "Greek Salad with Feta", "Salads", "Crisp cucumbers, ripe tomatoes, red onion, kalamata olives, block of feta cheese, oregano", 115, 3.5, 4.8, 9.2, 1.5, 3.0, 340, 180, "bowl", [
            {"description": "1 bowl (180g)", "grams": 180},
        ], ["greek salad", "feta salad"], "Salads"),
        F("salad-caprese", "Caprese Salad (Tomato Mozzarella)", "Salads", "Thick slices of ripe tomato and fresh mozzarella drizzled with olive oil and basil", 160, 9.5, 3.5, 12.0, 1.0, 2.8, 210, 160, "plate", [
            {"description": "1 plate (160g)", "grams": 160},
        ], ["insalata caprese", "tomato mozzarella"], "Salads", image_key="tomato"),
        F("salad-cobb", "Cobb Salad with Chicken & Egg", "Salads", "Iceberg lettuce, hard-boiled egg, grilled chicken breast, bacon bits, tomato, blue cheese", 175, 14.0, 3.5, 11.5, 1.5, 2.0, 420, 220, "bowl", [
            {"description": "1 large bowl (220g)", "grams": 220},
        ], ["cobb salad"], "Salads"),
        F("salad-kachumber", "Indian Kachumber Salad", "Salads", "Diced cucumbers, tomatoes, red onions tossed with lemon juice, chaat masala, cilantro", 28, 1.0, 5.5, 0.2, 1.4, 2.8, 120, 120, "katori", [
            {"description": "1 katori (120g)", "grams": 120},
        ], ["kachumber", "cucumber tomato onion salad"], "Salads"),
    ])

    # =========================================================================
    # MEDITERRANEAN & MEXICAN (~40 items)
    # =========================================================================
    items.extend([
        F("falafel-balls", "Falafel (Fried chickpea balls)", "Snacks", "Ground soaked chickpeas with herbs and spices, shaped into patties and deep-fried", 330, 13.0, 31.0, 17.5, 5.5, 2.2, 290, 50, "serving (3 pieces)", [
            {"description": "3 falafels (50g)", "grams": 50},
            {"description": "6 falafels (100g)", "grams": 100},
        ], ["falafel", "chickpea fritter"], "Mediterranean"),
        F("falafel-wrap", "Falafel Wrap with Hummus & Tahini", "Fast Food", "Pita bread wrapped with crisp falafels, hummus, lettuce, pickled turnips, tahini", 215, 7.8, 28.0, 8.5, 3.8, 2.8, 440, 220, "wrap", [
            {"description": "1 wrap (220g)", "grams": 220},
        ], ["falafel sandwich", "pita wrap"], "Mediterranean"),
        F("hummus-classic", "Classic Hummus (Chickpea Tahini dip)", "Condiments", "Cooked chickpeas blended with tahini, olive oil, garlic, lemon juice", 166, 7.9, 14.3, 9.6, 6.0, 0.3, 379, 30, "2 tablespoons", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1/2 cup (120g)", "grams": 120},
        ], ["hummus dip", "chickpea spread"], "Mediterranean"),
        F("baba-ganoush", "Baba Ganoush (Eggplant dip)", "Condiments", "Smoked roasted eggplant blended with tahini, garlic, lemon juice and olive oil", 130, 3.2, 9.5, 9.0, 4.0, 2.2, 310, 50, "serving", [
            {"description": "1/4 cup (60g)", "grams": 60},
        ], ["mutabbal", "eggplant dip"], "Mediterranean"),
        F("tabbouleh-salad", "Tabbouleh Salad", "Salads", "Finely chopped fresh parsley, mint, tomatoes, bulgur wheat, olive oil and lemon", 115, 2.5, 11.0, 7.2, 3.2, 2.2, 190, 150, "bowl", [
            {"description": "1 bowl (150g)", "grams": 150},
        ], ["tabouli", "parsley bulgur salad"], "Mediterranean"),
        F("chicken-shawarma-plate", "Chicken Shawarma Plate", "Fast Food", "Thinly sliced spiced rotisserie chicken served with rice, garlic sauce, pickles", 195, 16.5, 14.0, 8.5, 1.5, 1.8, 460, 280, "plate", [
            {"description": "1 full platter (300g)", "grams": 300},
        ], ["shawarma platter"], "Mediterranean"),
        F("chicken-shawarma-wrap", "Chicken Shawarma Wrap", "Fast Food", "Shaved roasted chicken in pita bread with toum garlic sauce, french fries, pickles", 225, 14.0, 24.0, 8.8, 1.8, 2.2, 510, 200, "wrap", [
            {"description": "1 wrap (200g)", "grams": 200},
        ], ["shawarma sandwich"], "Mediterranean"),
        F("quesadilla-cheese", "Cheese Quesadilla (Flour tortilla)", "Fast Food", "Toasted flour tortilla folded over melted cheddar and Monterey Jack cheese", 310, 13.5, 28.0, 16.5, 2.0, 1.5, 610, 130, "quesadilla", [
            {"description": "1 quesadilla (130g)", "grams": 130},
        ], ["cheese quesadilla"], "Mexican"),
        F("quesadilla-chicken", "Chicken Quesadilla", "Fast Food", "Grilled chicken strips and melted cheese folded in crisp toasted flour tortilla", 265, 16.5, 24.0, 11.5, 1.8, 1.5, 580, 160, "quesadilla", [
            {"description": "1 quesadilla (160g)", "grams": 160},
        ], ["chicken cheese quesadilla"], "Mexican"),
        F("guacamole-fresh", "Fresh Guacamole", "Condiments", "Mashed ripe avocado with diced tomatoes, onions, jalapeños, lime juice, cilantro", 155, 1.8, 8.5, 14.0, 5.8, 1.2, 290, 45, "serving (3 tbsp)", [
            {"description": "3 tbsp (45g)", "grams": 45},
            {"description": "1/2 cup (115g)", "grams": 115},
        ], ["guac", "avocado dip"], "Mexican"),
        F("pico-de-gallo", "Pico de Gallo (Fresh Salsa)", "Condiments", "Chopped fresh tomatoes, white onions, jalapeños, cilantro, lime juice", 25, 1.0, 5.2, 0.2, 1.5, 3.0, 210, 30, "serving (2 tbsp)", [
            {"description": "2 tbsp (30g)", "grams": 30},
            {"description": "1/2 cup (100g)", "grams": 100},
        ], ["fresh salsa", "salsa fresca"], "Mexican", image_key="tomato"),
        F("tortilla-chips-salted", "Tortilla Chips (Corn, salted)", "Snacks", "Crisp triangular fried yellow corn tortilla chips", 488, 7.0, 65.5, 23.4, 5.2, 0.8, 420, 28, "serving (approx 12 chips)", [
            {"description": "1 oz / 12 chips (28g)", "grams": 28},
            {"description": "Bowl (60g)", "grams": 60},
        ], ["nacho chips", "corn tortilla chips"], "Snacks"),
        F("nachos-with-cheese", "Nachos with Melted Cheese", "Fast Food", "Corn tortilla chips smothered in warm melted cheddar cheese sauce", 345, 8.5, 42.0, 16.5, 3.2, 2.5, 640, 150, "plate", [
            {"description": "1 plate (150g)", "grams": 150},
        ], ["nachos cheese", "stadium nachos"], "Mexican"),
    ])

    return items

print("Catalogue part 7 loaded.")
