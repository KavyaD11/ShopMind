from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from recommender import get_recommendations
from nlp_pipeline import process_message

app = Flask(__name__)
app.secret_key = "shopmind_secret_key_2024"
CORS(app, supports_credentials=True)

sessions = {}

def get_session(sid):
    if sid not in sessions:
        sessions[sid] = {
            "product_type": None, "usage": None, "style": None,
            "attributes": [], "budget": None, "liked_items": [], "history": []
        }
    return sessions[sid]

RESPONSE_TEMPLATES = {
    "backpack":       "🎒 Here are the top backpacks I found for you!",
    "laptop_bag":     "💼 Here are the best laptop bags for you!",
    "duffel_bag":     "👜 Here are the top duffel bags for you!",
    "messenger_bag":  "📦 Here are the best messenger bags for you!",
    "travel_tote":    "🛍️ Here are the top tote bags for you!",
    "luggage":        "🧳 Here are the best luggage options for you!",
    "womens_handbag": "👜 Here are the top handbags for you!",
    "headphones":     "🎧 Here are the best headphones/earbuds for you!",
    "phone":          "📱 Here are the top phones for you!",
    "laptop":         "💻 Here are the best laptop accessories for you!",
    "mens_watch":     "⌚ Here are the top watches for you!",
    "womens_watch":   "⌚ Here are the top watches for you!",
    "mens_shoes":     "👟 Here are the best shoes for you!",
    "womens_shoes":   "👠 Here are the best shoes for you!",
    "mens_clothing":  "👔 Here are the top clothing options for you!",
    "womens_clothing":"👗 Here are the top clothing options for you!",
    "beauty":         "✨ Here are the best beauty products for you!",
    "sports":         "🏋️ Here are the top sports & fitness products for you!",
    "outdoor":        "🏕️ Here are the best outdoor products for you!",
    "mens_accessories":"💍 Here are the top accessories for you!",
    "womens_accessories":"💍 Here are the top accessories for you!",
}

def get_response_text(session, products):
    from recommender import resolve_categories, CAT_MAP
    pt = session.get("product_type", "")
    cats = resolve_categories(pt)
    cat = cats[0] if cats else ""
    base = RESPONSE_TEMPLATES.get(cat, "🛍️ Here are the best matches I found for you!")
    if not products:
        return f"😕 I couldn't find exact matches for **{pt}**. Try being more specific or reset the chat and try again!"
    return base

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    user_session = get_session(session_id)

    intent, entities = process_message(message)

    # Update session
    if entities.get("product_type"):
        user_session["product_type"] = entities["product_type"]
    if entities.get("usage"):
        user_session["usage"] = entities["usage"]
    if entities.get("style"):
        user_session["style"] = entities["style"]
    if entities.get("attributes"):
        user_session["attributes"] = list(set(user_session["attributes"] + entities["attributes"]))
    if entities.get("budget") is not None:
        user_session["budget"] = entities["budget"]

    user_session["history"].append({"role": "user", "message": message})
    products = []
    response_text = ""

    if intent == "greeting":
        response_text = "👋 Hey! I'm **ShopMind** — your AI shopping assistant.\n\nTell me what you're looking for! For example:\n- *'College backpack under ₹3000'*\n- *'Face wash for oily skin'*\n- *'Wireless earbuds under ₹2000'*\n- *'Women's handbag stylish'*"

    elif intent == "confusion":
        response_text = "No worries! Let me simplify — here are just **2 top picks** for you:"
        products = get_recommendations(user_session, limit=2)

    elif intent == "like":
        liked = data.get("liked_product")
        if liked:
            user_session["liked_items"].append(liked)
            short_name = liked['name'][:40] + "..."
            response_text = f"❤️ Great taste! Based on **{short_name}**, here are similar products:"
            products = get_recommendations(user_session, limit=4, seed_product=liked)
        else:
            response_text = "Here are more top picks for you!"
            products = get_recommendations(user_session, limit=4)

    elif intent in ("product_search", "refine"):
        if not user_session["product_type"]:
            response_text = "🤔 What are you looking for? Try something like:\n- *'College backpack'*\n- *'Face wash'*\n- *'Running shoes'*\n- *'Wireless earbuds'*"
        else:
            products = get_recommendations(user_session, limit=4)
            response_text = get_response_text(user_session, products)

    else:
        # Unknown — still try to search if we have product context
        if user_session.get("product_type"):
            products = get_recommendations(user_session, limit=4)
            response_text = get_response_text(user_session, products)
        else:
            response_text = "🤔 I didn't quite catch that. Try something like:\n- *'College backpack'*\n- *'Wireless earbuds under ₹2000'*\n- *'Moisturizer for dry skin'*"

    user_session["history"].append({"role": "bot", "message": response_text})

    # Display budget in INR for sidebar
    budget_display = None
    if user_session["budget"]:
        b = float(user_session["budget"])
        budget_display = int(b) if b <= 200 else int(b)  # keep as-is, frontend converts

    return jsonify({
        "session_id": session_id,
        "intent": intent,
        "entities": entities,
        "response": response_text,
        "products": products,
        "session_data": {
            "product_type": user_session["product_type"],
            "usage": user_session["usage"],
            "style": user_session["style"],
            "attributes": user_session["attributes"],
            "budget": user_session["budget"],
            "liked_items": [p["name"][:40] for p in user_session["liked_items"]]
        }
    })

@app.route("/reset", methods=["POST"])
def reset():
    data = request.json
    sid = data.get("session_id")
    if sid and sid in sessions:
        del sessions[sid]
    return jsonify({"status": "reset", "session_id": sid})

if __name__ == "__main__":
    app.run(debug=True, port=5000)