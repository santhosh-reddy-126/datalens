import { Link } from 'react-router-dom';
import { Star, TrendingUp, ExternalLink } from 'lucide-react';
import './ProductCard.css';

export default function ProductCard({ product }) {
  return (
    <Link
      to={`/product/${product.product_id}`}
      className="product-card glass-card fade-in"
      id={`product-card-${product.product_id}`}
    >
      <div className="product-card-image">
        {product.imageUrl ? (
          <img src={product.imageUrl} alt={product.title} />
        ) : (
          <div className="product-card-placeholder">
            <TrendingUp size={32} />
          </div>
        )}
      </div>

      <div className="product-card-body">
        <h3 className="product-card-title">{product.title || 'Untitled Product'}</h3>

        <div className="product-card-meta">
          {product.price != null && (
            <span className="product-price">
              ₹{product.price.toLocaleString('en-IN')}
            </span>
          )}
          {product.rating != null && (
            <span className="product-rating">
              <Star size={12} fill="var(--warning)" stroke="var(--warning)" />
              {product.rating}
            </span>
          )}
        </div>

        <div className="product-card-footer">
          <span className="badge badge-accent">View Details</span>
          <ExternalLink size={14} className="card-link-icon" />
        </div>
      </div>
    </Link>
  );
}
