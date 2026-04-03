import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts';
import {
  ArrowLeft, Star, Eye, EyeOff, TrendingDown, TrendingUp,
  BarChart3, Clock, ExternalLink, Trash2
} from 'lucide-react';
import { fetchProducts, fetchFullHistory, toggleTracking, deleteProduct } from '../services/api';
import DeleteConfirmModal from '../components/DeleteConfirmModal';
import './ProductDetail.css';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip glass-card">
      <p className="tooltip-date">{label}</p>
      <p className="tooltip-price">₹{payload[0].value?.toLocaleString('en-IN')}</p>
    </div>
  );
}

export default function ProductDetail() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [prodRes, histRes] = await Promise.all([
          fetchProducts(),
          fetchFullHistory(productId),
        ]);
        const found = (prodRes.data || []).find((p) => p.product_id === productId);
        setProduct(found || null);

        const rawHistory = histRes.data || [];
        const formatted = rawHistory.map((h) => ({
          date: new Date(h.created_at).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
          }),
          fullDate: new Date(h.created_at).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          }),
          price: h.price,
        }));
        setHistory(formatted);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [productId]);

  const handleToggle = async () => {
    if (!product) return;
    try {
      await toggleTracking(productId, !product.tracking);
      setProduct((p) => ({ ...p, tracking: !p.tracking }));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = () => {
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    setDeleting(true);
    try {
      await deleteProduct(productId);
      navigate('/');
    } catch (err) {
      console.error('Delete failed:', err);
      alert(err.message || 'Failed to delete product');
      setDeleting(false);
      setShowDeleteModal(false);
    }
  };

  if (loading) {
    return (
      <div className="detail-page container">
        <div className="detail-loading">
          <div className="skeleton" style={{ height: 32, width: 200 }} />
          <div className="skeleton" style={{ height: 300, width: '100%', marginTop: 24 }} />
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="detail-page container">
        <div className="empty-state">
          <h3>Product not found</h3>
          <Link to="/" className="btn btn-ghost" style={{ marginTop: 16 }}>
            <ArrowLeft size={16} /> Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const prices = history.map((h) => h.price).filter(Boolean);
  const minPrice = prices.length ? Math.min(...prices) : null;
  const maxPrice = prices.length ? Math.max(...prices) : null;
  const avgPrice = prices.length
    ? Math.round(prices.reduce((a, b) => a + b, 0) / prices.length)
    : null;

  return (
    <div className="detail-page container slide-up">
      {/* Back Navigation */}
      <Link to="/" className="back-link">
        <ArrowLeft size={16} />
        Back to Dashboard
      </Link>

      {/* Product Header */}
      <div className="detail-header glass-card">
        <div className="detail-image">
          {product.imageUrl ? (
            <img src={product.imageUrl} alt={product.title} />
          ) : (
            <div className="detail-image-placeholder">
              <BarChart3 size={48} />
            </div>
          )}
        </div>

        <div className="detail-info">
          <div className="detail-info-top">
            <span className={`badge ${product.tracking ? 'badge-success' : 'badge-warning'}`}>
              {product.tracking ? 'Tracking Active' : 'Tracking Paused'}
            </span>
          </div>

          <h1 className="detail-title">{product.title}</h1>

          <div className="detail-price-row">
            {product.price != null && (
              <span className="detail-current-price">
                ₹{product.price.toLocaleString('en-IN')}
              </span>
            )}
            {product.rating != null && (
              <span className="detail-rating">
                <Star size={16} fill="var(--warning)" stroke="var(--warning)" />
                {product.rating} / 5
              </span>
            )}
          </div>

          <div className="detail-actions">
            <button
              className={`btn ${product.tracking ? 'btn-ghost' : 'btn-primary'}`}
              onClick={handleToggle}
              id="toggle-tracking-btn"
            >
              {product.tracking ? (
                <>
                  <EyeOff size={16} /> Pause Tracking
                </>
              ) : (
                <>
                  <Eye size={16} /> Resume Tracking
                </>
              )}
            </button>
            {product.url && (
              <a
                href={product.url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-ghost"
              >
                <ExternalLink size={16} /> View on Amazon
              </a>
            )}
            <button
              className="btn btn-ghost"
              onClick={handleDelete}
              disabled={deleting}
              style={{ color: 'var(--danger)' }}
              id="delete-product-btn"
            >
              <Trash2 size={16} /> {deleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </div>

      {/* Price Stats */}
      {prices.length > 0 && (
        <div className="price-stats-grid">
          <div className="price-stat glass-card">
            <TrendingDown size={18} style={{ color: 'var(--success)' }} />
            <div>
              <span className="price-stat-value">₹{minPrice?.toLocaleString('en-IN')}</span>
              <span className="price-stat-label">Lowest Price</span>
            </div>
          </div>
          <div className="price-stat glass-card">
            <TrendingUp size={18} style={{ color: 'var(--danger)' }} />
            <div>
              <span className="price-stat-value">₹{maxPrice?.toLocaleString('en-IN')}</span>
              <span className="price-stat-label">Highest Price</span>
            </div>
          </div>
          <div className="price-stat glass-card">
            <BarChart3 size={18} style={{ color: 'var(--accent-2)' }} />
            <div>
              <span className="price-stat-value">₹{avgPrice?.toLocaleString('en-IN')}</span>
              <span className="price-stat-label">Average Price</span>
            </div>
          </div>
          <div className="price-stat glass-card">
            <Clock size={18} style={{ color: 'var(--accent-1)' }} />
            <div>
              <span className="price-stat-value">{history.length}</span>
              <span className="price-stat-label">Price Points</span>
            </div>
          </div>
        </div>
      )}

      {/* Price History Chart */}
      <div className="chart-section glass-card">
        <div className="chart-header">
          <h2>
            <BarChart3 size={20} />
            Price History
          </h2>
          {history.length > 0 && (
            <span className="tag">
              <Clock size={12} />
              {history.length} data points
            </span>
          )}
        </div>

        {history.length > 0 ? (
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={360}>
              <AreaChart data={history} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                    <stop offset="50%" stopColor="#8b5cf6" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#06b6d4" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.04)"
                  vertical={false}
                />
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={(v) => `₹${(v / 1000).toFixed(v >= 1000 ? 0 : 1)}k`}
                  dx={-10}
                  domain={['dataMin - 100', 'dataMax + 100']}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="url(#lineGradient)"
                  strokeWidth={2.5}
                  fill="url(#priceGradient)"
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: '#06b6d4',
                    stroke: '#0a0b0f',
                    strokeWidth: 2,
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="chart-empty">
            <BarChart3 size={40} />
            <p>No price history yet. Price changes will appear here once detected.</p>
          </div>
        )}
      </div>

      {showDeleteModal && (
        <DeleteConfirmModal
          onClose={() => setShowDeleteModal(false)}
          onConfirm={confirmDelete}
          loading={deleting}
          productTitle={product?.title}
        />
      )}
    </div>
  );
}
