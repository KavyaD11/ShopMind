import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import ChatMessage from "./components/ChatMessage";
import ProductCard from "./components/ProductCard";
import SessionSidebar from "./components/SessionSidebar";

const SESSION_KEY = "shopmind_session_id";

const QUICK_CHIPS = [
  "Wireless earbuds under $50",
  "Women's handbag",
  "Men's running shoes",
  "Skincare beauty products",
  "Smartwatch for fitness",
  "Camping outdoor gear",
  "Men's watch under $100",
  "Laptop accessories",
];

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "bot",
      text: "👋 Hey! I'm **ShopMind** — your personal AI shopping assistant powered by real Amazon products.\n\nTell me what you're looking for! ",
      products: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem(SESSION_KEY) || null;
  });
  const [sessionData, setSessionData] = useState({});
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text, likedProduct = null) => {
    const userText = text || input.trim();
    if (!userText && !likedProduct) return;

    if (!likedProduct) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: "user", text: userText, products: [] },
      ]);
      setInput("");
    }
    setLoading(true);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: likedProduct ? "i like this" : userText,
          session_id: sessionId,
          liked_product: likedProduct || null,
        }),
      });

      const data = await res.json();
      setSessionId(data.session_id);
      localStorage.setItem(SESSION_KEY, data.session_id);
      setSessionData(data.session_data || {});

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          text: data.response,
          products: data.products || [],
          intent: data.intent,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          text: "⚠️ Couldn't connect to the server. Make sure Flask backend is running on port 5000.",
          products: [],
        },
      ]);
    }
    setLoading(false);
  };

  const handleLike = (product) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: "user",
        text: `❤️ I like **${product.name.slice(0, 50)}...**`,
        products: [],
      },
    ]);
    sendMessage("", product);
  };

  const resetChat = async () => {
    try {
      await fetch("/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch {}
    localStorage.removeItem(SESSION_KEY);
    setSessionId(null);
    setSessionData({});
    setMessages([
      {
        id: Date.now(),
        role: "bot",
        text: "👋 Hey! I'm **ShopMind** — your personal AI shopping assistant powered by real Amazon products.\n\nTell me what you're looking for!",
        products: [],
      },
    ]);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <div className="brand-icon">SM</div>
          <div>
            <h1 className="brand-name">ShopMind</h1>
            <span className="brand-tagline">AI Shopping Assistant • Real Amazon Products</span>
          </div>
        </div>
        <button className="reset-btn" onClick={resetChat}>↺ Reset Chat</button>
      </header>

      <div className="main-layout">
        <div className="chat-area">
          <div className="messages-container">
            {messages.map((msg) => (
              <div key={msg.id}>
                <ChatMessage message={msg} />
                {msg.products && msg.products.length > 0 && (
                  <div className="products-grid">
                    {msg.products.map((product) => (
                      <ProductCard key={product.id} product={product} onLike={handleLike} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="typing-indicator">
                <div className="dot" /><div className="dot" /><div className="dot" />
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chips-row">
            {QUICK_CHIPS.map((chip) => (
              <button key={chip} className="chip" onClick={() => sendMessage(chip)}>
                {chip}
              </button>
            ))}
          </div>

          <div className="input-area">
            <input
              type="text"
              className="chat-input"
              placeholder="Try: 'wireless earbuds' or 'women handbag'..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button className="send-btn" onClick={() => sendMessage()} disabled={loading || !input.trim()}>
              Send →
            </button>
          </div>
        </div>

        <SessionSidebar sessionData={sessionData} />
      </div>
    </div>
  );
}

export default App;