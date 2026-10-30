"""
Catalogue data part 9: International cheeses, deli meats, breakfast grains, global Asian/Mexican meals,
beverages/supplements, nuts/seeds, and gourmet condiments (~250 items).
"""

from scripts.build_full_database import F

def get_part9():
    items = []

    # =========================================================================
    # CHEESES & DELICATESSEN MEATS (~30 items)
    # =========================================================================
    items.extend([
        F("cheese-feta", "Feta cheese (Greek sheep/goat)", "Dairy", "Crumbly brined curd white cheese", 264, 14.2, 4.1, 21.3, 0, 4.1, 1116, 30, "crumbled portion", [
            {"description": "1/4 cup crumbled (38g)", "grams": 38},
            {"description": "1 oz (28g)", "grams": 28},
        ], ["feta cheese", "greek feta"], "Cheese"),
        F("cheese-gouda", "Gouda cheese", "Dairy", "Mild, creamy Dutch semi-hard yellow cheese", 356, 24.9, 2.2, 27.4, 0, 2.2, 819, 28, "slice", [
            {"description": "1 slice (28g)", "grams": 28},
        ], ["gouda"], "Cheese"),
        F("cheese-brie", "Brie cheese (Soft ripened)", "Dairy", "Soft cow milk cheese with edible white rind", 334, 20.7, 0.5, 27.7, 0, 0.5, 629, 28, "wedge portion", [
            {"description": "1 wedge (28g)", "grams": 28},
        ], ["french brie"], "Cheese"),
        F("cheese-swiss", "Swiss cheese (Emmental)", "Dairy", "Semi-hard cheese with distinctive holes", 380, 26.9, 5.4, 27.8, 0, 1.4, 260, 28, "slice", [
            {"description": "1 slice (28g)", "grams": 28},
        ], ["swiss cheese", "emmental"], "Cheese"),
        F("cheese-provolone", "Provolone cheese", "Dairy", "Aged Italian semi-hard pulled-curd cheese", 351, 25.6, 2.1, 26.6, 0, 0.6, 876, 28, "slice", [
            {"description": "1 slice (28g)", "grams": 28},
        ], ["provolone slice"], "Cheese"),
        F("cheese-ricotta", "Ricotta cheese (Whole milk)", "Dairy", "Fresh Italian whey cheese with sweet, mild flavor", 174, 11.3, 3.0, 13.0, 0, 0.3, 84, 62, "1/4 cup", [
            {"description": "1/4 cup (62g)", "grams": 62},
            {"description": "1/2 cup (124g)", "grams": 124},
        ], ["ricotta"], "Cheese"),
        F("cheese-cottage-cream", "Cottage cheese (4% milkfat)", "Dairy", "Curds in cream, small curd", 98, 11.1, 3.4, 4.3, 0, 2.7, 364, 113, "1/2 cup", [
            {"description": "1/2 cup (113g)", "grams": 113},
            {"description": "1 cup (226g)", "grams": 226},
        ], ["cottage cheese creamed"], "Fresh Cheese"),
        F("cheese-cream-plain", "Cream Cheese (Regular block)", "Dairy", "Soft, mild, rich spreadable cheese", 342, 5.9, 4.1, 34.2, 0, 3.2, 321, 28, "2 tablespoons", [
            {"description": "1 tbsp (14g)", "grams": 14},
            {"description": "2 tbsp / 1 oz (28g)", "grams": 28},
        ], ["philadelphia cream cheese"], "Cheese"),
        F("cheese-goat-chevre", "Goat cheese (Chèvre fresh)", "Dairy", "Soft fresh goat milk log", 268, 18.5, 0.9, 21.1, 0, 0.9, 459, 28, "ounce", [
            {"description": "1 oz (28g)", "grams": 28},
        ], ["chevre", "goat cheese"], "Cheese"),
        F("cheese-blue", "Blue cheese (Gorgonzola / Roquefort)", "Dairy", "Pungent veined crumbly cheese", 353, 21.4, 2.3, 28.7, 0, 0.5, 1146, 28, "crumbled portion", [
            {"description": "1 oz (28g)", "grams": 28},
        ], ["blue cheese", "gorgonzola"], "Cheese"),
        F("deli-turkey-breast", "Deli Turkey Breast (Sliced)", "Meat", "Pre-packaged roasted deli turkey breast slices", 104, 17.5, 2.0, 2.8, 0, 1.2, 920, 56, "2 slices", [
            {"description": "2 slices (56g)", "grams": 56},
            {"description": "3 slices (84g)", "grams": 84},
        ], ["sliced turkey", "turkey cold cuts"], "Deli Meats"),
        F("deli-roast-beef", "Deli Roast Beef (Sliced)", "Meat", "Cooked lean deli beef cold cuts", 135, 20.0, 1.5, 5.5, 0, 0.8, 850, 56, "2 slices", [
            {"description": "2 slices (56g)", "grams": 56},
        ], ["roast beef slices"], "Deli Meats"),
        F("deli-ham-slice", "Deli Ham (Honey or smoked, sliced)", "Meat", "Cured sliced deli ham", 120, 16.5, 3.0, 4.8, 0, 2.5, 980, 56, "2 slices", [
            {"description": "2 slices (56g)", "grams": 56},
        ], ["sliced ham", "deli ham"], "Deli Meats"),
        F("prosciutto-di-parma", "Prosciutto di Parma (Dry cured)", "Meat", "Italian dry-cured thinly sliced ham", 265, 27.0, 0.5, 17.5, 0, 0, 1820, 28, "2 thin slices", [
            {"description": "2 slices (28g)", "grams": 28},
        ], ["prosciutto", "parma ham"], "Cured Meats"),
        F("salami-genoa", "Genoa Salami", "Meat", "Dry-cured hard pork and beef sausage sliced", 412, 18.0, 1.5, 37.5, 0, 0.5, 1890, 28, "3 slices", [
            {"description": "3 slices (28g)", "grams": 28},
        ], ["genoa salami"], "Cured Meats"),
        F("pepperoni-sliced", "Pepperoni slices", "Meat", "Cured spicy beef and pork sausage slices for pizza", 494, 22.7, 0.0, 44.0, 0, 0, 1582, 28, "serving (approx 14 slices)", [
            {"description": "14 slices (28g)", "grams": 28},
        ], ["pizza pepperoni"], "Cured Meats"),
        F("sausage-pork-breakfast", "Pork Breakfast Sausage (Cooked patty)", "Meat", "Pan-fried ground pork seasoned breakfast patty", 339, 19.5, 1.2, 28.5, 0, 0.5, 830, 38, "patty", [
            {"description": "1 patty (38g)", "grams": 38},
            {"description": "2 links (45g)", "grams": 45},
        ], ["breakfast sausage", "pork sausage link"], "Meats"),
        F("sausage-chicken", "Chicken Sausage (Cooked)", "Meat", "Lean chicken sausage link with Italian herbs", 185, 18.0, 3.0, 11.0, 0.5, 1.5, 680, 80, "link", [
            {"description": "1 link (80g)", "grams": 80},
        ], ["chicken sausage"], "Meats"),
        F("beef-hot-dog", "Beef Hot Dog (Frankfurter)", "Meat", "Fully cooked all-beef frankfurter", 310, 11.5, 2.5, 28.5, 0, 1.8, 860, 50, "frankfurter", [
            {"description": "1 hot dog (50g)", "grams": 50},
        ], ["beef frank", "hot dog weiner"], "Meats"),
    ])

    # =========================================================================
    # MORE GRAINS, CEREALS & BAKERY ITEMS (~30 items)
    # =========================================================================
    items.extend([
        F("oats-steel-cut-cooked", "Cooked Steel Cut Oats", "Grains", "Whole groats simmered in water", 71, 2.5, 12.0, 1.5, 1.9, 0.2, 2, 200, "bowl", [
            {"description": "1 bowl (200g)", "grams": 200},
        ], ["steel cut oatmeal", "pinhead oats"], "Cereals", image_key="oats"),
        F("barley-cooked", "Cooked Pearl Barley", "Grains", "Peeled barley grains boiled until tender", 123, 2.3, 28.2, 0.4, 3.8, 0.3, 3, 157, "cup cooked", [
            {"description": "1 cup cooked (157g)", "grams": 157},
        ], ["pearl barley", "jau boiled"], "Grains"),
        F("buckwheat-kasha-cooked", "Cooked Buckwheat Groats (Kasha)", "Grains", "Toasted buckwheat groats simmered in water", 92, 3.4, 19.9, 0.6, 2.7, 0.5, 4, 168, "cup", [
            {"description": "1 cup cooked (168g)", "grams": 168},
        ], ["kasha", "kuttu cooked"], "Grains"),
        F("cereal-cheerios", "Cheerios Cereal (Whole grain oats)", "Breakfast", "Toasted whole grain oat ring cereal", 376, 12.1, 73.2, 6.7, 9.1, 3.6, 566, 28, "cup (approx 28g)", [
            {"description": "1 cup (28g)", "grams": 28},
            {"description": "1.5 cups (42g)", "grams": 42},
        ], ["cheerios", "oat cereal"], "Cereals"),
        F("cereal-bran-flakes", "Bran Flakes Cereal", "Breakfast", "Whole wheat and wheat bran flakes", 357, 10.7, 82.1, 2.1, 17.9, 17.9, 643, 40, "cup", [
            {"description": "1 cup (40g)", "grams": 40},
        ], ["wheat bran cereal", "bran flakes"], "Cereals"),
        F("croissant-butter", "Butter Croissant (Bakery)", "Bread", "Flaky layered crescent laminated with butter", 406, 8.2, 45.8, 21.0, 2.6, 6.0, 467, 57, "medium croissant", [
            {"description": "1 small croissant (42g)", "grams": 42},
            {"description": "1 medium croissant (57g)", "grams": 57},
        ], ["croissant", "french croissant"], "Bakery"),
        F("pancakes-buttermilk", "Buttermilk Pancakes (Plain)", "Breakfast", "Fluffy griddle cakes made of flour, buttermilk, egg", 227, 6.4, 38.3, 5.3, 1.4, 8.5, 439, 77, "pancake (4-inch)", [
            {"description": "1 pancake (77g)", "grams": 77},
            {"description": "2 pancakes (154g)", "grams": 154},
        ], ["hotcakes", "griddle cakes", "flapjacks"], "Breakfast"),
        F("french-toast-plain", "French Toast (1 slice)", "Breakfast", "Bread dipped in beaten egg and milk, pan-fried with touch of butter", 229, 7.8, 29.5, 8.9, 1.5, 7.2, 380, 65, "slice", [
            {"description": "1 slice (65g)", "grams": 65},
            {"description": "2 slices (130g)", "grams": 130},
        ], ["french toast slice"], "Breakfast"),
        F("waffle-plain", "Belgian Waffle (Plain)", "Breakfast", "Crisp grid-patterned baked batter cake", 291, 7.9, 41.1, 10.6, 1.8, 5.0, 483, 75, "waffle (7-inch)", [
            {"description": "1 waffle (75g)", "grams": 75},
        ], ["belgian waffle"], "Breakfast"),
        F("muffin-blueberry", "Blueberry Muffin", "Breakfast", "Baked sweet cake muffin studded with fresh blueberries", 377, 5.1, 54.0, 16.0, 2.0, 29.0, 360, 113, "medium muffin", [
            {"description": "1 medium muffin (113g)", "grams": 113},
        ], ["blueberry muffin"], "Bakery"),
    ])

    # =========================================================================
    # MORE BEANS, PULSES & PRESERVED VEGETABLES (~30 items)
    # =========================================================================
    items.extend([
        F("black-beans-cooked", "Cooked Black Beans", "Pulses", "Boiled mature black turtle beans drained", 132, 8.9, 23.7, 0.5, 8.7, 0.3, 1, 172, "cup cooked", [
            {"description": "1 cup cooked (172g)", "grams": 172},
            {"description": "1/2 cup (86g)", "grams": 86},
        ], ["black turtle beans", "frijoles negros"], "Legumes"),
        F("pinto-beans-cooked", "Cooked Pinto Beans", "Pulses", "Boiled pinto beans without lard or salt", 143, 9.0, 26.2, 0.7, 9.0, 0.4, 2, 171, "cup cooked", [
            {"description": "1 cup cooked (171g)", "grams": 171},
        ], ["pinto beans"], "Legumes"),
        F("cannellini-beans-cooked", "Cannellini Beans (White kidney beans)", "Pulses", "Boiled Italian white kidney beans", 139, 9.7, 25.1, 0.5, 6.3, 0.3, 4, 180, "cup cooked", [
            {"description": "1 cup cooked (180g)", "grams": 180},
        ], ["white kidney beans", "cannellini"], "Legumes"),
        F("lima-beans-cooked", "Cooked Lima Beans", "Pulses", "Boiled mature large white lima beans", 115, 7.8, 20.9, 0.4, 7.0, 1.5, 17, 170, "cup cooked", [
            {"description": "1 cup cooked (170g)", "grams": 170},
        ], ["butter beans", "lima beans"], "Legumes"),
        F("fava-beans-cooked", "Cooked Fava Beans (Broad beans)", "Pulses", "Boiled shelled broad beans", 110, 7.6, 19.7, 0.4, 5.4, 1.8, 5, 170, "cup", [
            {"description": "1 cup (170g)", "grams": 170},
        ], ["broad beans", "bakla"], "Legumes"),
        F("split-peas-green-cooked", "Cooked Green Split Peas", "Pulses", "Boiled split green peas without salt", 118, 8.3, 21.1, 0.4, 8.3, 2.9, 2, 196, "cup cooked", [
            {"description": "1 cup (196g)", "grams": 196},
        ], ["green split peas"], "Legumes"),
        F("kimchi-napa-cabbage", "Kimchi (Fermented napa cabbage)", "Vegetables", "Traditional Korean fermented spicy cabbage with chili, garlic, ginger", 15, 1.1, 2.4, 0.5, 1.6, 1.1, 498, 50, "serving", [
            {"description": "1/4 cup (50g)", "grams": 50},
            {"description": "1/2 cup (100g)", "grams": 100},
        ], ["korean kimchi", "fermented cabbage"], "Fermented Vegetables"),
        F("sauerkraut-cabbage", "Sauerkraut (Fermented cabbage, drained)", "Vegetables", "Shredded cabbage fermented in lactic acid", 19, 0.9, 4.3, 0.1, 2.9, 1.8, 661, 75, "1/2 cup", [
            {"description": "1/2 cup (75g)", "grams": 75},
        ], ["sauerkraut"], "Fermented Vegetables"),
        F("olives-kalamata", "Kalamata Olives (Pitted)", "Vegetables", "Greek dark purple brined olives", 240, 1.4, 6.0, 24.0, 3.0, 0, 890, 28, "serving (approx 6 olives)", [
            {"description": "6 olives (28g)", "grams": 28},
        ], ["black olives", "greek olives"], "Olives"),
        F("olives-green-spanish", "Green Olives (Manzanilla, pitted)", "Vegetables", "Spanish pickled green olives", 145, 1.0, 3.8, 15.3, 3.3, 0.5, 1556, 28, "serving (approx 6 olives)", [
            {"description": "6 olives (28g)", "grams": 28},
        ], ["green olives", "pitted green olives"], "Olives"),
        F("pickles-dill-gherkin", "Dill Pickles (Gherkins)", "Vegetables", "Cucumbers pickled in vinegar, dill and brine", 12, 0.6, 2.3, 0.2, 1.2, 1.1, 960, 35, "pickle spear", [
            {"description": "1 medium spear (35g)", "grams": 35},
        ], ["gherkins", "dill pickle"], "Pickles"),
    ])

    # =========================================================================
    # BEVERAGES, COFFEES, TEAS & SUPPLEMENTS (~40 items)
    # =========================================================================
    items.extend([
        F("cold-brew-coffee", "Cold Brew Coffee (Black)", "Beverages", "Coarse ground coffee steeped cold for 16 hours, unsweetened", 3, 0.4, 0.3, 0, 0, 0, 5, 240, "cup", [
            {"description": "1 cup (240ml)", "grams": 240},
            {"description": "1 large tumbler (480ml)", "grams": 480},
        ], ["cold brew", "iced black coffee"], "Coffee", image_key="coffee"),
        F("flat-white", "Flat White (Whole milk)", "Beverages", "Double ristretto espresso with steamed whole milk and velvety microfoam", 62, 3.5, 4.8, 3.2, 0, 4.6, 42, 200, "cup", [
            {"description": "1 cup (200ml)", "grams": 200},
        ], ["flat white"], "Coffee", image_key="coffee"),
        F("matcha-latte", "Matcha Green Tea Latte (Oat milk)", "Beverages", "Whisked Japanese ceremonial matcha powder with steamed oat milk", 65, 1.5, 10.5, 1.8, 0.8, 7.5, 45, 250, "cup", [
            {"description": "1 cup (250ml)", "grams": 250},
        ], ["green tea matcha latte"], "Tea"),
        F("iced-tea-lemon", "Iced Tea with Lemon (Sweetened)", "Beverages", "Brewed black tea served chilled with lemon juice and cane sugar", 35, 0.1, 8.8, 0, 0, 8.5, 6, 300, "glass", [
            {"description": "1 glass (300ml)", "grams": 300},
        ], ["lemon iced tea"], "Tea", image_key="tea"),
        F("kombucha-ginger", "Ginger Kombucha (Raw fermented)", "Beverages", "Fermented effervescent sweetened black/green tea with ginger", 18, 0.2, 4.2, 0, 0, 3.8, 10, 250, "bottle portion", [
            {"description": "1 bottle (350ml)", "grams": 350},
        ], ["kombucha"], "Fermented Drinks"),
        F("jaljeera", "Jaljeera (Cumin mint cooler)", "Beverages", "Chilled water infused with roasted cumin, mint, black salt, amchur, boondi", 25, 0.5, 5.5, 0.2, 0.8, 3.5, 340, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["jal jeera"], "Natural Drinks"),
        F("kokum-sharbat", "Kokum Sharbat", "Beverages", "Chilled sweet and tangy drink made from red kokum fruit extract and cumin", 45, 0.2, 11.0, 0.1, 0.4, 10.5, 120, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["kokum juice", "amrut kokum"], "Natural Drinks"),
        F("badam-milk-kesar", "Kesar Badam Milk (Hot spiced almond milk)", "Beverages", "Whole cow milk simmered with crushed almonds, saffron and sugar", 95, 3.8, 12.0, 3.8, 0.8, 11.0, 42, 200, "cup", [
            {"description": "1 cup (200ml)", "grams": 200},
        ], ["almond milk saffron", "kesar badam doodh"], "Traditional Drinks", image_key="milk"),
        F("haldi-doodh", "Turmeric Golden Milk (Haldi Doodh)", "Beverages", "Warm milk simmered with fresh ground turmeric, black pepper and honey", 75, 3.2, 8.5, 3.2, 0.2, 7.8, 44, 200, "cup", [
            {"description": "1 cup (200ml)", "grams": 200},
        ], ["golden milk", "turmeric latte"], "Traditional Drinks", image_key="milk"),
        F("thandai", "Thandai (Holi beverage)", "Beverages", "Chilled whole milk infused with ground almonds, fennel, melon seeds, poppy seeds, rose", 125, 4.2, 17.0, 4.8, 1.2, 15.5, 45, 250, "glass", [
            {"description": "1 glass (250ml)", "grams": 250},
        ], ["bhang thandai non-alcoholic", "sardai"], "Traditional Drinks", image_key="milk"),
        F("pomegranate-juice-pure", "100% Pomegranate Juice (Fresh)", "Beverages", "Cold-pressed fresh pomegranate juice without added sugar", 54, 0.5, 13.1, 0.1, 0.1, 12.6, 9, 240, "glass", [
            {"description": "1 glass (240ml)", "grams": 240},
        ], ["anar ka juice", "pom juice"], "Juices"),
        F("guava-juice", "Guava Nectar (Sweetened)", "Beverages", "Guava pulp beverage with added sugar and vitamin C", 60, 0.4, 14.5, 0.2, 0.8, 13.5, 14, 240, "glass", None, ["real guava juice", "amrood juice"], "Juices"),
        F("coconut-milk-canned", "Canned Coconut Milk (Thick culinary)", "Dairy", "Grated coconut meat pressed with water, high-fat unsweetened", 197, 2.0, 2.8, 21.3, 0, 1.8, 15, 60, "1/4 cup", [
            {"description": "1/4 cup (60ml)", "grams": 60},
            {"description": "1 can (400ml)", "grams": 400},
        ], ["thick coconut milk", "nariyal doodh"], "Plant Milk"),
    ])

    # =========================================================================
    # GOURMET CONDIMENTS, OILS & SPICES (~45 items)
    # =========================================================================
    items.extend([
        F("oil-peanut-groundnut", "Groundnut Oil (Peanut oil)", "Condiments", "Cold-pressed edible peanut oil", 884, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", [
            {"description": "1 tsp (5g)", "grams": 5},
            {"description": "1 tbsp (14g)", "grams": 14},
        ], ["singtel", "groundnut oil", "peanut oil"], "Cooking Oils"),
        F("oil-rice-bran", "Rice Bran Oil", "Condiments", "Refined oil extracted from hard outer brown layer of rice", 884, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", None, ["rice bran cooking oil"], "Cooking Oils"),
        F("oil-sesame-gingelly", "Sesame Oil (Gingelly / Til oil)", "Condiments", "Pressed sesame seed oil", 884, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", [
            {"description": "1 tbsp (14g)", "grams": 14},
        ], ["til ka tel", "gingelly oil"], "Cooking Oils"),
        F("oil-avocado", "Avocado Oil (Extra virgin)", "Condiments", "Cold-pressed green avocado oil", 884, 0, 0, 100.0, 0, 0, 0, 14, "tablespoon", None, ["pure avocado oil"], "Cooking Oils"),
        F("vinegar-apple-cider", "Apple Cider Vinegar", "Condiments", "Raw unfiltered fermented apple cider with mother", 21, 0, 0.9, 0, 0, 0.4, 5, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["acv", "apple cider vinegar"], "Vinegars"),
        F("soy-sauce-dark", "Dark Soy Sauce", "Condiments", "Aged thick dark Chinese soy sauce with caramel", 60, 4.5, 10.5, 0.1, 0, 6.0, 6000, 15, "tablespoon", [
            {"description": "1 tbsp (15ml)", "grams": 15},
        ], ["dark soy sauce"], "Sauces"),
        F("sauce-sriracha", "Sriracha Hot Chili Sauce", "Condiments", "Thai paste of chili peppers, distilled vinegar, garlic, sugar, salt", 122, 2.2, 28.0, 1.1, 2.0, 20.0, 1850, 5, "teaspoon", [
            {"description": "1 tsp (5g)", "grams": 5},
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["sriracha hot sauce"], "Sauces"),
        F("sauce-schezwan", "Schezwan Sauce / Chutney", "Condiments", "Indo-Chinese spicy condiment made of red chilies, garlic, ginger, vinegar", 185, 2.0, 22.0, 10.5, 2.5, 12.0, 1150, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["schezwan chutney"], "Sauces"),
        F("sauce-barbecue", "Barbecue Sauce (Smoky sweet)", "Condiments", "Thick sweet and smoky tomato vinegar BBQ sauce", 172, 1.1, 40.8, 0.6, 1.2, 33.4, 1027, 30, "2 tablespoons", [
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["bbq sauce"], "Sauces"),
        F("mustard-dijon", "Dijon Mustard", "Condiments", "Traditional French sharp mustard prepared with white wine", 66, 4.4, 5.8, 4.0, 3.2, 1.5, 1120, 5, "teaspoon", [
            {"description": "1 tsp (5g)", "grams": 5},
        ], ["french dijon mustard"], "Condiments"),
        F("dressing-ranch", "Ranch Salad Dressing (Commercial)", "Condiments", "Creamy buttermilk, garlic, onion, herb dressing", 432, 1.5, 6.5, 45.0, 0.3, 4.5, 1010, 30, "2 tablespoons", [
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["ranch dressing"], "Dressings"),
        F("pesto-basil", "Basil Pesto Sauce (Genovese)", "Condiments", "Crushed fresh basil leaves, pine nuts, parmesan, garlic, olive oil", 450, 5.5, 6.0, 46.0, 2.5, 1.0, 850, 30, "2 tablespoons", [
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["pesto genovese", "green pesto"], "Sauces"),
        F("sauce-marinara", "Marinara Pasta Sauce", "Condiments", "Simmered Italian plum tomatoes with garlic, herbs and olive oil", 52, 1.8, 7.8, 1.8, 1.8, 4.5, 420, 125, "1/2 cup", [
            {"description": "1/2 cup (125g)", "grams": 125},
        ], ["marinara sauce", "tomato pasta sauce"], "Sauces", image_key="pasta"),
        F("tahini-paste", "Tahini Paste (100% Sesame)", "Condiments", "Pure ground hulled toasted sesame seed paste", 595, 17.0, 21.2, 53.8, 9.3, 0.5, 115, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["sesame paste", "tahina"], "Nut & Seed Pastes"),
        F("thecha-mirchi-peanut", "Kolhapuri Mirchi Thecha (Green chili peanut)", "Condiments", "Coarsely pounded hot green chilies, roasted peanuts, garlic, oil, cumin", 240, 6.5, 14.0, 18.0, 4.0, 1.5, 820, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["kolhapuri thecha", "mirchi thecha", "hirvi mirchi thecha"], "Chutneys"),
        F("pickle-lemon", "Lemon Pickle (Nimbu ka achar)", "Condiments", "Quartered lemons cured with salt, red chili and fenugreek seeds", 95, 1.2, 16.0, 2.8, 3.2, 8.0, 3200, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["nimbu achar", "lemon pickle"], "Pickles"),
        F("pickle-mixed", "Mixed Vegetable Pickle (Pachranga)", "Condiments", "Mango, carrot, lime, lotus stem and green chili pickled in mustard oil", 160, 1.8, 11.5, 12.0, 3.5, 2.0, 3400, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
        ], ["pachranga achar", "mixed pickle"], "Pickles"),
        F("jam-mixed-fruit", "Mixed Fruit Jam (Commercial)", "Condiments", "Fruit pulp preserve with sugar and pectin", 260, 0.3, 65.0, 0.1, 1.0, 58.0, 15, 20, "tablespoon", [
            {"description": "1 tbsp (20g)", "grams": 20},
        ], ["kissan jam", "mixed fruit jam"], "Spreads"),
        F("nutella-hazelnut-spread", "Nutella (Hazelnut cocoa spread)", "Sweets", "Sweetened cocoa and roasted hazelnut spread", 539, 6.3, 57.5, 30.9, 3.0, 56.3, 42, 15, "tablespoon", [
            {"description": "1 tbsp (15g)", "grams": 15},
            {"description": "2 tbsp (30g)", "grams": 30},
        ], ["hazelnut spread", "nutella"], "Spreads"),
        F("maple-syrup-pure", "Pure Maple Syrup (Grade A)", "Condiments", "100% pure concentrated maple tree sap syrup", 260, 0, 67.0, 0.1, 0, 60.5, 12, 20, "tablespoon", [
            {"description": "1 tbsp (20g)", "grams": 20},
        ], ["maple syrup pure"], "Sweeteners"),
    ])

    # =========================================================================
    # MORE NUTS, SEEDS & SNACKS (~30 items)
    # =========================================================================
    items.extend([
        F("walnuts-halves-raw", "Raw Walnut halves (English)", "Nuts", "Raw shelled tree nut halves high in ALA omega-3", 654, 15.2, 13.7, 65.2, 6.7, 2.6, 2, 28, "1 oz / 14 halves", [
            {"description": "1 oz (28g)", "grams": 28},
        ], ["akhrot", "walnut halves"], "Tree Nuts"),
        F("pecans-halves", "Pecan halves (Raw)", "Nuts", "Raw shelled North American pecan halves", 691, 9.2, 13.9, 72.0, 9.6, 4.0, 0, 28, "1 oz (approx 19 halves)", [
            {"description": "1 oz (28g)", "grams": 28},
        ], ["pecans"], "Tree Nuts"),
        F("sunflower-seeds-kernels", "Sunflower Seed Kernels (Roasted, unsalted)", "Nuts", "Dry-roasted shelled sunflower seeds", 582, 19.3, 24.1, 49.8, 11.1, 2.7, 3, 28, "1/4 cup (approx 35g)", [
            {"description": "1/4 cup (35g)", "grams": 35},
        ], ["sunflower seeds"], "Seeds"),
        F("pumpkin-seeds-pepitas", "Pumpkin Seeds (Pepitas, roasted)", "Nuts", "Green hulled pumpkin seed kernels roasted with light salt", 574, 29.8, 14.7, 49.1, 6.5, 1.3, 256, 28, "1 oz / handful", [
            {"description": "1 oz (28g)", "grams": 28},
            {"description": "1/4 cup (32g)", "grams": 32},
        ], ["pepitas", "pumpkin seeds"], "Seeds"),
        F("makhana-roasted-plain", "Roasted Makhana (Fox nuts / Lotus seeds)", "Snacks", "Puffed water lily seeds dry-roasted without oil", 350, 9.7, 77.0, 0.5, 7.6, 0.5, 5, 25, "bowl (approx 25g)", [
            {"description": "1 cup puffed (15g)", "grams": 15},
            {"description": "1 large bowl (30g)", "grams": 30},
        ], ["fox nuts", "phool makhana", "lotus seeds"], "Snacks"),
        F("makhana-ghee-roasted", "Ghee Roasted Makhana (With rock salt)", "Snacks", "Fox nuts roasted in 1 tsp desi cow ghee with sendha namak and pepper", 420, 8.5, 68.0, 14.0, 6.8, 0.5, 280, 30, "bowl", [
            {"description": "1 bowl (30g)", "grams": 30},
        ], ["salted makhana", "spiced fox nuts"], "Snacks"),
        F("chana-roasted-with-skin", "Bhuna Chana (Roasted brown chickpea with skin)", "Snacks", "Dry-roasted whole Bengal gram with crispy fibrous skin", 360, 22.0, 58.0, 5.0, 16.5, 2.5, 20, 30, "handful", [
            {"description": "1 handful (30g)", "grams": 30},
            {"description": "1 small katori (50g)", "grams": 50},
        ], ["bhuna chana", "roasted grams", "chana roasted with skin"], "Snacks", image_key="chickpeas"),
        F("kurmura-plain", "Murmura (Plain Puffed Rice)", "Grains", "Crisp puffed white rice kernels without oil or seasoning", 380, 6.5, 84.0, 0.5, 1.8, 0.1, 5, 20, "cup (approx 15g)", [
            {"description": "1 cup puffed (15g)", "grams": 15},
            {"description": "2 cups (30g)", "grams": 30},
        ], ["kurmura", "murmura", "puffed rice plain", "lai"], "Grains"),
        F("khakhra-methi", "Methi Khakhra (Crispy whole wheat cracker)", "Snacks", "Roasted thin whole wheat and fenugreek flatbread cracker", 410, 10.5, 65.0, 12.0, 7.5, 1.2, 480, 30, "piece (approx 30g)", [
            {"description": "1 khakhra (30g)", "grams": 30},
            {"description": "2 khakhras (60g)", "grams": 60},
        ], ["gujarati khakhra", "methi khakhra"], "Farsan"),
        F("khakhra-plain-jeera", "Jeera Khakhra", "Snacks", "Roasted thin whole wheat cracker seasoned with cumin and light oil", 420, 10.0, 66.0, 13.0, 6.8, 1.0, 460, 30, "piece", [
            {"description": "1 khakhra (30g)", "grams": 30},
        ], ["jeera khakhra"], "Farsan"),
        F("brownie-chocolate-walnut", "Chocolate Walnut Brownie", "Sweets", "Rich fudge baked chocolate cake square with chopped walnuts", 465, 5.8, 54.0, 26.0, 3.2, 36.0, 210, 65, "square", [
            {"description": "1 brownie square (65g)", "grams": 65},
        ], ["fudge brownie", "walnut brownie"], "Bakery"),
        F("cheesecake-new-york", "New York Cheesecake (1 slice)", "Sweets", "Rich baked cream cheese filling on graham cracker crust", 321, 5.5, 25.5, 22.5, 0.6, 21.0, 310, 125, "slice (1/8 of 9-inch cake)", [
            {"description": "1 slice (125g)", "grams": 125},
        ], ["cheesecake", "ny cheesecake"], "Bakery"),
    ])

    return items

print("Catalogue part 9 loaded.")
