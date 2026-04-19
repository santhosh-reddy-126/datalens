import { useState, useEffect, useCallback } from 'react';
import { Package, TrendingUp, BarChart3, Plus, Frown } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import AddProductModal from '../components/AddProductModal';
import { fetchProducts, searchProducts } from '../services/api';
import './Dashboard.css';

export default function Dashboard({ searchQuery }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      let res;
      if (searchQuery) {
        res = await searchProducts(searchQuery);
      } else {
        res = await fetchProducts();
      }
      setProducts(res.data || []);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const avgPrice =
    products.length > 0
      ? products.reduce((sum, p) => sum + (p.price || 0), 0) / products.length
      : 0;

  const topRated = products.filter((p) => p.rating && p.rating >= 4).length;

  return (
    <div className="dashboard container">
      {/* Hero Stats */}
      <section className="stats-section slide-up">
        <div className="stats-header">
          <h1>
            Price <span className="gradient-text">Dashboard</span>
          </h1>
          <p>Track Amazon products and monitor price changes in real-time.</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card glass-card">
            <div className="stat-icon" style={{ background: 'rgba(6, 182, 212, 0.1)' }}>
              <Package size={20} style={{ color: 'var(--accent-1)' }} />
            </div>
            <div className="stat-info">
              <span className="stat-value">{products.length}</span>
              <span className="stat-label">Total Products</span>
            </div>
          </div>

          <div className="stat-card glass-card">
            <div className="stat-icon" style={{ background: 'rgba(52, 211, 153, 0.1)' }}>
              <BarChart3 size={20} style={{ color: 'var(--success)' }} />
            </div>
            <div className="stat-info">
              <span className="stat-value">{topRated}</span>
              <span className="stat-label">Top Rated (4★+)</span>
            </div>
          </div>

          <div className="stat-card glass-card">
            <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.1)' }}>
              <TrendingUp size={20} style={{ color: 'var(--accent-2)' }} />
            </div>
            <div className="stat-info">
              <span className="stat-value">
                {avgPrice > 0 ? `₹${Math.round(avgPrice).toLocaleString('en-IN')}` : '—'}
              </span>
              <span className="stat-label">Avg. Price</span>
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="products-section">
        <div className="products-header">
          <h2>
            {searchQuery ? `Results for "${searchQuery}"` : 'Your Products'}
          </h2>
          <button
            className="btn btn-primary"
            onClick={() => setShowModal(true)}
            id="add-product-btn"
          >
            <Plus size={16} />
            Add Product
          </button>
        </div>

        {loading ? (
          <div className="products-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="product-skeleton glass-card">
                <div className="skeleton" style={{ height: 200 }} />
                <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div className="skeleton" style={{ height: 16, width: '80%' }} />
                  <div className="skeleton" style={{ height: 16, width: '50%' }} />
                  <div className="skeleton" style={{ height: 28, width: '40%', marginTop: 8 }} />
                </div>
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="empty-state fade-in">
            <Frown size={48} />
            <h3>{searchQuery ? 'No products found' : 'No products tracked yet'}</h3>
            <p>
              {searchQuery
                ? 'Try a different search term.'
                : 'Click "Add Product" to start tracking Amazon prices.'}
            </p>
            {!searchQuery && (
              <button
                className="btn btn-primary"
                onClick={() => setShowModal(true)}
              >
                <Plus size={16} />
                Add Your First Product
              </button>
            )}
          </div>
        ) : (
          <div className="products-grid">
            {products.map((product, index) => (
              <div key={product.product_id} style={{ animationDelay: `${index * 60}ms` }} className="fade-in">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        )}
      </section>

      {showModal && (
        <AddProductModal
          onClose={() => setShowModal(false)}
          onAdded={loadProducts}
        />
      )}
    </div>
  );
}
