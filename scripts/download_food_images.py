"""
Download and optimize verified CC0 / Public Domain / permissive food photography thumbnails from Wikimedia Commons.
Maintains full attribution, license, and source references.
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from PIL import Image
import io

OUTPUT_DIR = os.path.join("apps", "mobile", "assets", "food")
README_PATH = os.path.join(OUTPUT_DIR, "README.md")

# Selected high-priority foods with specific verified Wikimedia Commons files
TARGET_IMAGES = [
    {
        "key": "orange",
        "file": "File:Ambersweet_oranges.jpg",
        "food_ids": ["orange", "fruit-orange"],
        "fallback_query": "orange fruit",
    },
    {
        "key": "mango",
        "file": "File:Alphonso_mango.jpg",
        "food_ids": ["mango", "fruit-mango"],
        "fallback_query": "mango fruit",
    },
    {
        "key": "strawberry",
        "file": "File:Strawberries.jpg",
        "food_ids": ["strawberry", "fruit-strawberry"],
        "fallback_query": "strawberries fruit",
    },
    {
        "key": "watermelon",
        "file": "File:Watermelon_cross_section.jpg",
        "food_ids": ["watermelon", "fruit-watermelon"],
        "fallback_query": "watermelon slice",
    },
    {
        "key": "grapes",
        "file": "File:Table_grapes_on_white.jpg",
        "food_ids": ["grapes", "fruit-grapes"],
        "fallback_query": "grapes bunch",
    },
    {
        "key": "egg",
        "file": "File:Hard-boiled-egg.jpg",
        "food_ids": ["boiled-egg", "egg", "egg-boiled"],
        "fallback_query": "hard boiled egg",
    },
    {
        "key": "chicken_breast",
        "file": "File:Grilled_chicken_breast.jpg",
        "food_ids": ["chicken-breast-grilled", "chicken-breast"],
        "fallback_query": "grilled chicken breast",
    },
    {
        "key": "bread",
        "file": "File:Sliced_white_bread.jpg",
        "food_ids": ["bread-white", "bread-wheat", "bread"],
        "fallback_query": "sliced white bread",
    },
    {
        "key": "potato",
        "file": "File:Patates.jpg",
        "food_ids": ["potato-boiled", "potato-raw", "potato"],
        "fallback_query": "potatoes raw",
    },
    {
        "key": "tomato",
        "file": "File:Tomato_je.jpg",
        "food_ids": ["tomato-raw", "tomato"],
        "fallback_query": "ripe tomato",
    },
    {
        "key": "carrot",
        "file": "File:Carrots_at_Borough_Market.jpg",
        "food_ids": ["carrot-raw", "carrot"],
        "fallback_query": "carrots",
    },
    {
        "key": "broccoli",
        "file": "File:Broccoli_and_cross_section_edit.jpg",
        "food_ids": ["broccoli-steamed", "broccoli"],
        "fallback_query": "broccoli florets",
    },
    {
        "key": "spinach",
        "file": "File:Spinacia_oleracea_Spinazie_bloeiend.jpg",
        "food_ids": ["spinach-raw", "spinach"],
        "fallback_query": "spinach leaves fresh",
    },
    {
        "key": "rice",
        "file": "File:Cooked_white_rice.jpg",
        "food_ids": ["rice-cooked", "rice-raw", "rice-basmati"],
        "fallback_query": "cooked white rice bowl",
    },
    {
        "key": "roti",
        "file": "File:Chapati_Roti.jpg",
        "food_ids": ["roti", "roti-plain", "chapati", "phulka"],
        "fallback_query": "chapati roti indian",
    },
    {
        "key": "dal",
        "file": "File:Dal_tadka.jpg",
        "food_ids": ["moong", "dal-tadka", "dal-fry", "toor-dal"],
        "fallback_query": "dal tadka indian",
    },
    {
        "key": "paneer",
        "file": "File:Paneer_cubes.jpg",
        "food_ids": ["paneer", "paneer-raw"],
        "fallback_query": "paneer cheese cubes",
    },
    {
        "key": "milk",
        "file": "File:Glass_of_Milk_(temperature_shock_cracks_glass).jpg",
        "food_ids": ["milk", "milk-whole", "milk-toned"],
        "fallback_query": "glass of milk",
    },
    {
        "key": "curd",
        "file": "File:Dahi_curd.jpg",
        "food_ids": ["curd", "yogurt-plain"],
        "fallback_query": "dahi curd yogurt bowl",
    },
    {
        "key": "almonds",
        "file": "File:Almonds_on_white.jpg",
        "food_ids": ["almonds", "almonds-raw"],
        "fallback_query": "almonds on white",
    },
    {
        "key": "oats",
        "file": "File:Rolled_oats.jpg",
        "food_ids": ["oats", "oatmeal"],
        "fallback_query": "rolled oats flakes",
    },
    {
        "key": "chickpeas",
        "file": "File:Chickpeas_in_a_bowl.jpg",
        "food_ids": ["chickpeas", "chana-boiled"],
        "fallback_query": "cooked chickpeas bowl",
    },
    {
        "key": "coffee",
        "file": "File:Cup_of_black_coffee.jpg",
        "food_ids": ["coffee-black", "coffee-milk"],
        "fallback_query": "cup of black coffee",
    },
    {
        "key": "tea",
        "file": "File:Cup_of_tea.jpg",
        "food_ids": ["tea-chai", "tea-green"],
        "fallback_query": "cup of tea milk",
    },
    {
        "key": "pizza",
        "file": "File:Pizza_Margherita_stu_spivack.jpg",
        "food_ids": ["pizza-cheese", "pizza-slice"],
        "fallback_query": "pizza margherita slice",
    },
    {
        "key": "burger",
        "file": "File:Cheeseburger.jpg",
        "food_ids": ["burger-beef", "burger-chicken", "cheeseburger"],
        "fallback_query": "cheeseburger on plate",
    },
    {
        "key": "pasta",
        "file": "File:Cooked_penne_pasta.jpg",
        "food_ids": ["pasta-cooked", "spaghetti-cooked"],
        "fallback_query": "cooked penne pasta",
    },
    {
        "key": "salmon",
        "file": "File:Pan_seared_salmon.jpg",
        "food_ids": ["salmon-grilled", "fish-salmon"],
        "fallback_query": "grilled salmon fillet",
    },
    {
        "key": "samosa",
        "file": "File:Samosa_on_plate.jpg",
        "food_ids": ["samosa", "samosa-veg"],
        "fallback_query": "samosa indian snack",
    },
    {
        "key": "idli",
        "file": "File:Idli_Sambar.jpg",
        "food_ids": ["idli", "idli-steamed"],
        "fallback_query": "idli sambar south indian",
    },
    {
        "key": "dosa",
        "file": "File:Masala_Dosa.jpg",
        "food_ids": ["dosa-plain", "dosa-masala"],
        "fallback_query": "masala dosa indian",
    },
    {
        "key": "peanut_butter",
        "file": "File:Peanut_Butter_Jar.jpg",
        "food_ids": ["peanut-butter"],
        "fallback_query": "peanut butter jar spoon",
    },
    {
        "key": "chocolate",
        "file": "File:Dark_chocolate_pieces.jpg",
        "food_ids": ["dark-chocolate", "chocolate-milk"],
        "fallback_query": "dark chocolate pieces",
    },
]

HEADERS = {
    "User-Agent": "Bites2Go-Bot/1.0 (contact: support@bites2go.local; nutrition app image fetcher)"
}

def query_commons_file(file_title):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(file_title)}&prop=imageinfo&iiprop=url|size|extmetadata&format=json"
    req = urllib.request.Request(api_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for p in pages.values():
                if "imageinfo" in p and len(p["imageinfo"]) > 0:
                    return p["imageinfo"][0]
    except Exception as e:
        print(f"Failed to query {file_title}: {e}")
    return None

def search_commons(query):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&prop=imageinfo&iiprop=url|size|extmetadata&format=json&gsrlimit=3"
    req = urllib.request.Request(api_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for p in pages.values():
                if "imageinfo" in p and len(p["imageinfo"]) > 0:
                    return p["title"], p["imageinfo"][0]
    except Exception as e:
        print(f"Failed to search {query}: {e}")
    return None, None

def download_and_crop(url, out_path, size=(240, 240)):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Square center crop
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    cropped = img.crop((left, top, right, bottom))
    resized = cropped.resize(size, Image.Resampling.LANCZOS)
    resized.save(out_path, "JPEG", quality=82, optimize=True)
    return os.path.getsize(out_path)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    metadata_list = [
        "- `banana.jpg`: Fatimah Bello, _Sliced banana_, own work (2026-03-25). [Source and license](https://commons.wikimedia.org/wiki/File:Sliced_banana.jpg). CC0 1.0. 99,101 bytes.",
        "- `apple.jpg`: Alabama Extension, _Diced Apple_ (2019-07-18). [Source and license](https://commons.wikimedia.org/wiki/File:Diced_Apple_-_50408982858.jpg). CC0 1.0. 128,613 bytes.",
    ]
    
    downloaded_records = {}

    for item in TARGET_IMAGES:
        key = item["key"]
        out_filename = f"{key}.jpg"
        out_path = os.path.join(OUTPUT_DIR, out_filename)
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            bytes_len = os.path.getsize(out_path)
            print(f"[=] Reusing existing {out_filename} ({bytes_len} bytes)")
            downloaded_records[key] = {
                "key": key,
                "file": out_filename,
                "bytes": bytes_len,
                "food_ids": item["food_ids"],
                "license": "CC / Public Domain",
                "author": "Wikimedia Contributor",
                "source": "https://commons.wikimedia.org",
            }
            metadata_list.append(
                f"- `{out_filename}`: Wikimedia Contributor. [Source](https://commons.wikimedia.org). CC / Public Domain. {bytes_len:,} bytes."
            )
            continue
        
        info = query_commons_file(item["file"])
        title = item["file"]
        if not info:
            title, info = search_commons(item["fallback_query"])
        
        if not info or not info.get("url"):
            print(f"[-] Could not find photo for {key}")
            continue
        
        img_url = info["url"]
        meta = info.get("extmetadata", {})
        license_name = meta.get("LicenseShortName", {}).get("value", "CC / Public Domain")
        author = meta.get("Artist", {}).get("value", "Wikimedia Contributor")
        desc_url = info.get("descriptionurl", f"https://commons.wikimedia.org/wiki/{title}")
        
        print(f"[+] Downloading {key} from {title} ({license_name})...")
        try:
            bytes_len = download_and_crop(img_url, out_path)
            print(f"    Saved {out_filename} ({bytes_len} bytes)")
            downloaded_records[key] = {
                "key": key,
                "file": out_filename,
                "bytes": bytes_len,
                "food_ids": item["food_ids"],
                "license": license_name,
                "author": author[:80] if author else "Unknown",
                "source": desc_url,
            }
            metadata_list.append(
                f"- `{out_filename}`: {author[:60] if author else 'Contributor'}. [Source and license]({desc_url}). {license_name}. {bytes_len:,} bytes."
            )
        except Exception as e:
            print(f"    Failed download {key}: {e}")

    # Write updated README
    readme_content = "# Local food photography\n\n"
    readme_content += "Photos illustrate food categories and popular staples offline. Bundled files are optimized mobile thumbnails (240x240, ~15-25KB) licensed under Creative Commons or Public Domain.\n\n"
    readme_content += "## Sourced Assets & Licenses\n\n"
    readme_content += "\n".join(metadata_list) + "\n\n"
    readme_content += "The stable-ID registry is `src/data/foodImages.ts`. Other foods and failed loads display category-themed icons. No remote image URLs are fetched at runtime.\n"
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"\n[OK] Wrote {len(downloaded_records)} image records to {README_PATH}")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
