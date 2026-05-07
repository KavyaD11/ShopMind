# 🛍️ ShopMind — AI Shopping Assistant

A full-stack conversational recommendation engine for personalized e-commerce.
Built with Flask (Python) + React.js + TF-IDF cosine similarity.

---

## 📁 Folder Structure

```
ShopMind/
├── backend/
│   ├── app.py              ← Flask API server
│   ├── nlp_pipeline.py     ← Intent detection + entity extraction
│   ├── recommender.py      ← TF-IDF recommendation engine
│   ├── products.csv        ← Product dataset (replace with your Amazon data)
│   └── requirements.txt    ← Python dependencies
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          ← Main chat application
│   │   ├── App.css         ← All styles
│   │   ├── index.js        ← React entry point
│   │   └── components/
│   │       ├── ChatMessage.js    ← Chat bubbles
│   │       ├── ProductCard.js    ← Product recommendation cards
│   │       └── SessionSidebar.js ← Live preference sidebar
│   └── package.json
│
└── README.md
```

---

## 🚀 Setup Instructions

### Step 1 — Open in VS Code
```
File → Open Folder → Select the ShopMind folder
```

### Step 2 — Backend Setup
Open a new terminal in VS Code:
```bash
cd backend
pip install -r requirements.txt
python -m nltk.downloader punkt stopwords
python app.py
```
Backend runs at: **http://localhost:5000**

### Step 3 — Frontend Setup
Open another terminal:
```bash
cd frontend
npm install
npm start
```
Frontend opens at: **http://localhost:3000**

---

## 💬 Demo Queries to Try

1. `"I want a stylish college bag under 1500"`
2. `"Wireless headphones for gym under 2000"`
3. `"I am confused"` → reduces to 2 options
4. Click **Like** on any product → finds similar items
5. `"Slim wallet for office"`

---

## 📦 Using Your Own Amazon Dataset

Replace `backend/products.csv` with your dataset.
Required columns:
- `id` — unique number
- `name` — product name
- `category` — bag / wallet / headphones / mobile / shoes / watch
- `price` — price in INR (number)
- `rating` — float (e.g. 4.3)
- `usage` — college / office / travel / gym / daily
- `style` — casual / formal / stylish / premium
- `attributes` — space-separated keywords (waterproof wireless lightweight)
- `description` — short product description

---

## 🧠 How It Works

1. **NLP Pipeline** — Detects intent (search / confused / like / greeting) and extracts entities (product type, usage, style, budget, attributes) using regex + NLTK

2. **Session Memory** — Stores preferences per user session (product, budget, liked items) and combines them across turns

3. **Recommendation Engine** — TF-IDF vectorizes product descriptions. Cosine similarity finds the closest matching products to your query.

4. **Emotion-Aware Logic** — Confusion → 2 results. Like → similar products.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js |
| Backend | Python + Flask |
| NLP | NLTK + Regex |
| Recommendations | Scikit-learn TF-IDF + Cosine Similarity |
| Data | CSV (pandas) |

---

Built for the ShopMind AI Shopping Assistant project 🚀
