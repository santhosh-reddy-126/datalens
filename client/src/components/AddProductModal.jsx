import { useState } from 'react';
import { Link2, Loader2, X, Plus, CheckCircle2 } from 'lucide-react';
import { addProduct } from '../services/api';
import './AddProductModal.css';

export default function AddProductModal({ onClose, onAdded }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError('');
    try {
      await addProduct(url.trim());
      setSuccess(true);
      setTimeout(() => {
        onAdded();
        onClose();
      }, 1200);
    } catch (err) {
      setError(err.message || 'Failed to add product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal glass-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={18} />
        </button>

        {success ? (
          <div className="modal-success">
            <CheckCircle2 size={48} className="success-icon" />
            <h3>Product Added!</h3>
            <p>Tracking has started automatically.</p>
          </div>
        ) : (
          <>
            <div className="modal-header">
              <div className="modal-icon">
                <Plus size={20} />
              </div>
              <h2>Track New Product</h2>
              <p>Paste an Amazon product URL to start tracking its price.</p>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
              <div className="input-group">
                <Link2 size={16} className="input-icon" />
                <input
                  type="url"
                  placeholder="https://www.amazon.in/dp/..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={loading}
                  autoFocus
                  id="add-product-url-input"
                />
              </div>

              {error && <div className="modal-error">{error}</div>}

              <button
                type="submit"
                className="btn btn-primary modal-submit"
                disabled={loading || !url.trim()}
                id="add-product-submit-btn"
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="spin" />
                    Scraping product...
                  </>
                ) : (
                  <>
                    <Plus size={16} />
                    Start Tracking
                  </>
                )}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
