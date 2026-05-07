import React, { useState } from "react";

export default function ProductCard({ product, onLike }) {
  const [liked, setLiked] = useState(false);
  const [imgError, setImgError] = useState(false);

  const handleLike = () => {
    setLiked(true);
    onLike(product);
  };

  const truncate = (str, n) =>
    str && str.length > n ? str.slice(0, n) + "..." : str;

  const formatCategory = (cat) =>
    cat.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div className="product-card">
      {/* Image */}
      <div className="product-img-wrap">
        {product.image && !imgError ? (
          <img
            src={product.image}
            alt={product.name}
            className="product-img"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="product-img-placeholder">🛍️</div>
        )}
        {product.isBestSeller && (
          <div className="best-seller-badge">Best Seller</div>
        )}
      </div>

      {/* Info */}
      <div className="product-info">
        <div className="product-category">{formatCategory(product.category)}</div>
        <div className="product-name">{truncate(product.name, 75)}</div>

        <div className="product-meta">
          <div className="product-price">₹{(product.price * 83).toFixed(0)}</div>
          <div className="product-rating">
            ★ {product.rating}
            <span className="review-count">({product.reviews?.toLocaleString()})</span>
          </div>
        </div>

        {product.boughtInLastMonth > 0 && (
          <div className="bought-badge">
            🔥 {product.boughtInLastMonth.toLocaleString()}+ bought last month
          </div>
        )}

        {/* Buttons */}
        <div className="product-actions">
          <button
            className={`like-btn ${liked ? "liked" : ""}`}
            onClick={handleLike}
            disabled={liked}
          >
            {liked ? "❤️ Liked" : "♡ Like"}
          </button>
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="noreferrer"
              className="view-btn"
            >
              🛒 Amazon
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
