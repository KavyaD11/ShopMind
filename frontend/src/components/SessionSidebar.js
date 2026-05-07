import React from "react";

export default function SessionSidebar({ sessionData }) {
  const hasData =
    sessionData.product_type || sessionData.usage || sessionData.style ||
    (sessionData.attributes && sessionData.attributes.length > 0) || sessionData.budget;

  const formatCategory = (cat) =>
    cat ? cat.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()) : "";

  const formatBudget = (b) => {
    if (!b) return null;
    const num = parseFloat(b);
    // If > 200 it's rupees already, if <= 200 it's USD → convert
    const inr = num > 200 ? num : num * 83;
    return `₹${Math.round(inr).toLocaleString("en-IN")}`;
  };

  return (
    <div className="sidebar">
      <div>
        <div className="sidebar-title">
          <span className="pulse-dot" />
          Live Preferences
        </div>

        {!hasData ? (
          <div className="empty-state">
            Start chatting and I'll track your preferences here in real time! 👀
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {sessionData.product_type && (
              <div className="pref-section">
                <div className="pref-label">Looking for</div>
                <div className="pref-value">{formatCategory(sessionData.product_type)}</div>
              </div>
            )}
            {sessionData.usage && (
              <div className="pref-section">
                <div className="pref-label">Usage</div>
                <div className="pref-value" style={{ textTransform: "capitalize" }}>{sessionData.usage}</div>
              </div>
            )}
            {sessionData.style && (
              <div className="pref-section">
                <div className="pref-label">Style</div>
                <div className="pref-value" style={{ textTransform: "capitalize" }}>{sessionData.style}</div>
              </div>
            )}
            {sessionData.budget && formatBudget(sessionData.budget) && (
              <div className="pref-section">
                <div className="pref-label">Budget</div>
                <div className="pref-value highlight">{formatBudget(sessionData.budget)}</div>
              </div>
            )}
            {sessionData.attributes && sessionData.attributes.length > 0 && (
              <div className="pref-section">
                <div className="pref-label">Attributes</div>
                <div className="attr-tags">
                  {sessionData.attributes.map((a) => (
                    <span key={a} className="tag" style={{ color: "#6c63ff" }}>{a}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div>
        <div className="sidebar-title">❤️ Liked Items</div>
        {!sessionData.liked_items || sessionData.liked_items.length === 0 ? (
          <div className="empty-state">Like a product and I'll find similar ones!</div>
        ) : (
          <div className="liked-list">
            {sessionData.liked_items.map((name, i) => (
              <div key={i} className="liked-item">❤️ {name}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}