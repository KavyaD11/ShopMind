import React from "react";

// Very basic markdown renderer (bold, italic, newlines)
function renderMarkdown(text) {
  const lines = text.split("\n");
  return lines.map((line, i) => {
    // Bold: **text**
    let parts = line.split(/(\*\*[^*]+\*\*)/g);
    let rendered = parts.map((part, j) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={j}>{part.slice(2, -2)}</strong>;
      }
      // Italic: *text*
      let subparts = part.split(/(\*[^*]+\*)/g);
      return subparts.map((sp, k) => {
        if (sp.startsWith("*") && sp.endsWith("*") && sp.length > 2) {
          return <em key={k}>{sp.slice(1, -1)}</em>;
        }
        return sp;
      });
    });
    return (
      <span key={i}>
        {rendered}
        {i < lines.length - 1 && <br />}
      </span>
    );
  });
}

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`message-wrapper ${isUser ? "user" : "bot"}`}>
      <div className={`avatar ${isUser ? "user" : "bot"}`}>
        {isUser ? "👤" : "🛍️"}
      </div>
      <div>
        {!isUser && message.intent && message.intent !== "unknown" && (
          <div className="intent-badge">⚡ {message.intent}</div>
        )}
        <div className={`bubble ${isUser ? "user" : "bot"}`}>
          {renderMarkdown(message.text)}
        </div>
      </div>
    </div>
  );
}
