import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "products_amazon (2).csv"))
df["name_lower"] = df["name"].str.lower().fillna("")

vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
mat = vec.fit_transform(df["name_lower"])

print(f"[ShopMind] Loaded {len(df)} products across {df['category'].nunique()} categories.")

# Maps every NLP product_type → dataset category name
CAT_MAP = {
    # backpacks
    "backpack": "backpack", "college bag": "backpack", "school bag": "backpack",
    "hiking backpack": "backpack", "travel backpack": "backpack",
    "anti theft backpack": "backpack", "kids bag": "backpack",
    "bag": "backpack",
    # other bags
    "laptop bag": "laptop_bag",
    "gym bag": "duffel_bag", "duffel bag": "duffel_bag",
    "messenger bag": "messenger_bag", "crossbody bag": "messenger_bag", "sling bag": "messenger_bag",
    "tote bag": "travel_tote", "tote": "travel_tote",
    "luggage": "luggage", "suitcase": "luggage",
    "womens handbag": "womens_handbag", "handbag": "womens_handbag", "purse": "womens_handbag",
    "wallet": "mens_accessories",
    # headphones
    "headphones": "headphones", "wireless earbuds": "headphones",
    "noise cancelling headphones": "headphones", "gaming headset": "headphones",
    # phone / laptop
    "phone": "phone", "laptop": "laptop",
    # watches
    "watch": "mens_watch", "smartwatch": "mens_watch",
    "womens watch": "womens_watch",
    # shoes
    "shoes": "mens_shoes", "sneakers": "mens_shoes",
    "running shoes": "mens_shoes", "formal shoes": "mens_shoes",
    "womens shoes": "womens_shoes",
    # clothing
    "mens clothing": "mens_clothing", "shirt": "mens_clothing",
    "jeans": "mens_clothing",
    "womens clothing": "womens_clothing", "womens dress": "womens_clothing",
    # beauty — ALL map to beauty
    "beauty": "beauty", "face wash": "beauty", "sunscreen": "beauty",
    "moisturizer": "beauty", "serum": "beauty", "makeup brush": "beauty",
    "lipstick": "beauty", "foundation": "beauty", "mascara": "beauty",
    "perfume": "beauty", "shampoo": "beauty", "conditioner": "beauty",
    "nail polish": "beauty",
    # accessories
    "sunglasses": "mens_accessories", "belt": "mens_accessories",
    "cap": "mens_accessories",
    # sports/outdoor
    "sports": "sports", "yoga mat": "sports", "protein": "sports",
    "outdoor": "outdoor",
    # group maps
    "footwear": ["mens_shoes", "womens_shoes"],
    "clothing": ["mens_clothing", "womens_clothing"],
}

ALL_CATS = list(df["category"].unique())


def resolve_categories(product_type):
    if not product_type:
        return []
    pt = product_type.lower().strip()
    val = CAT_MAP.get(pt)
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val]
    # fuzzy
    for cat in ALL_CATS:
        if pt in cat.lower() or cat.lower().replace("_", " ") in pt:
            return [cat]
    return []


def get_budget_usd(b):
    if not b:
        return None
    b = float(b)
    return b / 83.0 if b > 200 else b


def format_product(row, score):
    return {
        "id": int(row["id"]),
        "name": str(row["name"]),
        "category": str(row["category"]),
        "price": round(float(row["price"]), 2),
        "rating": float(row["rating"]),
        "reviews": int(row["reviews"]) if not pd.isna(row["reviews"]) else 0,
        "asin": str(row["asin"]),
        "url": str(row["url"]),
        "image": str(row["image"]),
        "isBestSeller": bool(row["isBestSeller"]) if not pd.isna(row["isBestSeller"]) else False,
        "boughtInLastMonth": int(row["boughtInLastMonth"]) if not pd.isna(row["boughtInLastMonth"]) else 0,
        "score": round(float(score), 3)
    }


def get_recommendations(session, limit=4, seed_product=None):
    try:
        budget_usd = get_budget_usd(session.get("budget")) if not seed_product else None

        if seed_product:
            allowed_cats = [seed_product.get("category")]
            query = seed_product.get("name", "")
        else:
            parts = []
            pt = session.get("product_type", "")
            if pt:
                parts.append(pt)
            if session.get("usage"):
                parts.append(session["usage"])
            if session.get("style"):
                parts.append(session["style"])
            if session.get("attributes"):
                parts.extend(session["attributes"])
            query = " ".join(parts) if parts else "popular"
            allowed_cats = resolve_categories(pt)

        query_vec = vec.transform([query.lower()])
        scores = cosine_similarity(query_vec, mat).flatten()
        top_indices = scores.argsort()[::-1]

        def passes(row, check_budget=True):
            if allowed_cats and row["category"] not in allowed_cats:
                return False
            if check_budget and budget_usd and float(row["price"]) > budget_usd:
                return False
            return True

        results = []
        for idx in top_indices:
            if passes(df.iloc[idx], check_budget=True):
                results.append(format_product(df.iloc[idx], scores[idx]))
            if len(results) >= limit:
                break

        if len(results) < limit:
            seen = {r["id"] for r in results}
            for idx in top_indices:
                row = df.iloc[idx]
                if int(row["id"]) not in seen and passes(row, check_budget=False):
                    results.append(format_product(row, scores[idx]))
                if len(results) >= limit:
                    break

        return results
    except Exception as e:
        print(f"[ShopMind] Error: {e}")
        import traceback; traceback.print_exc()
        return []