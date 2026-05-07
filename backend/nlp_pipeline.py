import re
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.download('punkt_tab', quiet=True)
except:
    pass

INTENT_PATTERNS = {
    "greeting":      r"\b(hi|hello|hey|namaste|good morning|good evening|start|help me)\b",
    "confusion":     r"\b(confused|too many|overwhelming|simplify|narrow|less options|fewer|don't know|no idea|help me choose|can't decide)\b",
    "like":          r"\b(i like|love this|this is good|similar to|more like this|liked|favorite|want this|show more like)\b",
    "refine":        r"\b(under|below|within|change|update|instead|different|more options|also|refine|filter)\b",
    "product_search":r"\b(want|need|looking for|find|show|get|buy|suggest|recommend|search|give me|can you find)\b",
}

# Ordered specific → generic. FIRST match wins.
PRODUCT_TYPES = [
    # Specific bag types
    ("college bag",       r"\b(college bag|college backpack|school bag|school backpack|student bag|campus bag|university bag)\b"),
    ("laptop bag",        r"\b(laptop bag|laptop backpack|laptop sleeve|laptop case|computer bag|laptop pouch)\b"),
    ("gym bag",           r"\b(gym bag|sports bag|duffel bag|duffle bag|duffel|duffle)\b"),
    ("anti theft backpack", r"\b(anti.?theft backpack|anti.?theft bag|security backpack)\b"),
    ("hiking backpack",   r"\b(hiking backpack|trekking bag|hiking bag|trail backpack|outdoor backpack)\b"),
    ("travel backpack",   r"\b(travel backpack|travel bag|carry on backpack)\b"),
    ("messenger bag",     r"\b(messenger bag|sling bag|crossbody bag|cross body bag)\b"),
    ("tote bag",          r"\b(tote bag|tote|shopping bag|grocery bag)\b"),
    ("luggage",           r"\b(luggage|suitcase|trolley bag|luggage set|travel suitcase|carry on luggage)\b"),
    ("womens handbag",    r"\b(women.?s? (handbag|purse|clutch)|handbag|clutch purse)\b"),
    ("backpack",          r"\b(backpack|rucksack|daypack|knapsack)\b"),
    ("wallet",            r"\b(wallet|billfold|card holder|card wallet|money clip)\b"),
    ("bag",               r"\b(bag|purse)\b"),
    # Headphones specific
    ("noise cancelling headphones", r"\b(noise cancell?ing|anc headphones|noise cancell?ation)\b"),
    ("wireless earbuds",  r"\b(wireless earbuds|tws|true wireless|bluetooth earbuds)\b"),
    ("gaming headset",    r"\b(gaming headset|gaming headphones|game headset)\b"),
    ("headphones",        r"\b(headphones?|headset|earphones?|earbuds?|neckband|airpods?|in.?ear|over.?ear)\b"),
    # Phone
    ("phone",             r"\b(phone|mobile|smartphone|android|iphone|cellphone)\b"),
    # Laptop
    ("laptop",            r"\b(laptop|notebook|macbook|chromebook)\b"),
    # Watches
    ("smartwatch",        r"\b(smartwatch|smart watch|fitness tracker|fitness watch|fitness band)\b"),
    ("womens watch",      r"\b(women.?s? watch|ladies watch|girl.?s? watch)\b"),
    ("watch",             r"\b(watch|wristwatch|timepiece|analog watch)\b"),
    # Shoes specific
    ("formal shoes",      r"\b(formal shoes|dress shoes|oxford shoes|office shoes|leather shoes)\b"),
    ("running shoes",     r"\b(running shoes?|jogging shoes?|marathon shoes?|sport shoes?|sports shoes?)\b"),
    ("womens shoes",      r"\b(women.?s? shoes?|ladies shoes?|heels?|stiletto|sandals?|flats?|wedges?)\b"),
    ("sneakers",          r"\b(sneakers?|trainers?|kicks|casual shoes?|canvas shoes?)\b"),
    ("shoes",             r"\b(shoes?|footwear|boots?|loafers?|moccasins?)\b"),
    # Clothing specific
    ("womens dress",      r"\b(dress|gown|frock|maxi dress|midi dress|mini dress)\b"),
    ("womens clothing",   r"\b(women.?s? (clothing|clothes|top|blouse|skirt|leggings|kurti|saree|kurta))\b"),
    ("mens clothing",     r"\b(men.?s? (clothing|clothes|shirt|t.?shirt|jacket|jeans|hoodie|trouser|polo|blazer))\b"),
    ("shirt",             r"\b(shirt|t.?shirt|polo|tee|top|blouse|henley)\b"),
    ("jeans",             r"\b(jeans|denim|chinos|pants|trousers)\b"),
    # Beauty specific — most specific first
    ("face wash",         r"\b(face wash|facial cleanser|face cleanser|face scrub|face foam)\b"),
    ("sunscreen",         r"\b(sunscreen|spf|sun protection|sunblock)\b"),
    ("moisturizer",       r"\b(moisturizer|face cream|face lotion|hydrating cream|day cream|night cream)\b"),
    ("serum",             r"\b(serum|face serum|vitamin c serum|hyaluronic acid)\b"),
    ("makeup brush",      r"\b(makeup brush|make.?up brush|cosmetic brush|foundation brush|beauty brush|blush brush|eyeshadow brush|brush set)\b"),
    ("lipstick",          r"\b(lipstick|lip color|lip gloss|lip balm|lip liner|lip stick)\b"),
    ("foundation",        r"\b(foundation|bb cream|cc cream|tinted moisturizer)\b"),
    ("mascara",           r"\b(mascara|lash|eyelash)\b"),
    ("perfume",           r"\b(perfume|cologne|fragrance|eau de toilette|body mist)\b"),
    ("shampoo",           r"\b(shampoo|hair wash|hair cleanser)\b"),
    ("conditioner",       r"\b(conditioner|hair conditioner|hair mask|hair treatment)\b"),
    ("nail polish",       r"\b(nail polish|nail color|nail art|nail gel|manicure)\b"),
    ("sunglasses",        r"\b(sunglasses?|shades|sunnies|eyewear|goggles)\b"),
    ("beauty",            r"\b(beauty|makeup|cosmetics|skincare|skin care|haircare|hair care|grooming)\b"),
    # Sports specific
    ("yoga mat",          r"\b(yoga mat|yoga block|yoga strap|yoga gear|yoga equipment)\b"),
    ("protein",           r"\b(protein|whey|creatine|supplements?|pre.?workout)\b"),
    ("sports",            r"\b(sports?|fitness|gym|workout|exercise|athletic)\b"),
    ("outdoor",           r"\b(outdoor|camping|hiking|trekking|cycling|adventure|kayak|fishing)\b"),
    # Accessories
    ("sunglasses",        r"\b(sunglasses?|shades|polarized glasses)\b"),
    ("belt",              r"\b(belt|leather belt|waist belt)\b"),
    ("cap",               r"\b(cap|hat|baseball cap|snapback|beanie)\b"),
]

USAGE_KEYWORDS = {
    "college":  r"\b(college|university|campus|student|school)\b",
    "office":   r"\b(office|work|professional|formal|business|corporate)\b",
    "travel":   r"\b(travel|trip|journey|flight|vacation|holiday)\b",
    "gym":      r"\b(gym|workout|fitness|exercise|training|sport)\b",
    "daily":    r"\b(daily|everyday|casual|regular|all day)\b",
    "gifting":  r"\b(gift|gifting|present|birthday|anniversary|wedding)\b",
    "outdoor":  r"\b(outdoor|camping|hiking|trekking)\b",
    "party":    r"\b(party|night out|evening|occasion|event)\b",
}

STYLE_KEYWORDS = {
    "stylish":  r"\b(stylish|trendy|fashionable|cool|aesthetic|chic|modern|fancy|designer)\b",
    "casual":   r"\b(casual|simple|basic|everyday|relaxed)\b",
    "formal":   r"\b(formal|professional|elegant|classy|sophisticated)\b",
    "premium":  r"\b(premium|luxury|branded|high.?end|expensive|high quality)\b",
    "sporty":   r"\b(sporty|athletic|sport|active|performance)\b",
    "cute":     r"\b(cute|adorable|sweet|girly|pretty)\b",
    "soft":     r"\b(soft|gentle|smooth|delicate|silky)\b",
    "vintage":  r"\b(vintage|retro|classic|old school|boho)\b",
}

ATTRIBUTE_KEYWORDS = {
    "waterproof":        r"\b(waterproof|water.?resistant|water.?proof|weatherproof)\b",
    "wireless":          r"\b(wireless|bluetooth|cordless|wifi)\b",
    "lightweight":       r"\b(lightweight|light.?weight|portable|compact|ultralight)\b",
    "noise-cancelling":  r"\b(noise.?cancell?ing|anc|noise.?cancell?ation)\b",
    "slim":              r"\b(slim|thin|sleek|minimal|slimline)\b",
    "large":             r"\b(large|big|spacious|roomy|xl|extra large|oversized)\b",
    "small":             r"\b(small|mini|compact|tiny|micro|petite)\b",
    "usb charging":      r"\b(usb|charging port|usb port|power bank)\b",
    "anti-theft":        r"\b(anti.?theft|secure|lockable|rfid)\b",
    "long battery":      r"\b(long battery|battery life|long lasting|all day battery)\b",
}


def clean_text(text):
    return text.lower().strip()


def extract_budget(text):
    patterns = [
        r"(?:under|below|within|less than|upto|up to|max|around|approx)\s*(?:\$|rs\.?|inr|₹)?\s*(\d+(?:,\d+)?(?:k)?)",
        r"(?:\$|rs\.?|inr|₹)\s*(\d+(?:,\d+)?(?:k)?)",
        r"(\d+(?:,\d+)?(?:k)?)\s*(?:\$|rs\.?|inr|₹|rupees?|dollars?|usd|bucks?)",
        r"budget\s*(?:of|is|=|:)?\s*(?:\$|rs\.?|inr|₹)?\s*(\d+(?:,\d+)?(?:k)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(",", "")
            if value_str.lower().endswith("k"):
                return int(value_str[:-1]) * 1000
            return int(value_str)
    return None


def detect_intent(text):
    text_lower = clean_text(text)
    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, text_lower):
            return intent
    for _, pattern in PRODUCT_TYPES:
        if re.search(pattern, text_lower):
            return "product_search"
    return "unknown"


def extract_entities(text):
    text_lower = clean_text(text)
    entities = {"product_type": None, "usage": None, "style": None, "attributes": [], "budget": None}

    for product, pattern in PRODUCT_TYPES:
        if re.search(pattern, text_lower):
            entities["product_type"] = product
            break

    for usage, pattern in USAGE_KEYWORDS.items():
        if re.search(pattern, text_lower):
            entities["usage"] = usage
            break

    for style, pattern in STYLE_KEYWORDS.items():
        if re.search(pattern, text_lower):
            entities["style"] = style
            break

    for attr, pattern in ATTRIBUTE_KEYWORDS.items():
        if re.search(pattern, text_lower):
            entities["attributes"].append(attr)

    entities["budget"] = extract_budget(text_lower)
    return entities


def process_message(message):
    intent = detect_intent(message)
    entities = extract_entities(message)
    return intent, entities