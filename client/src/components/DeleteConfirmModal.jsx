import { AlertTriangle, Loader2, X } from 'lucide-react';
import './DeleteConfirmModal.css';

export default function DeleteConfirmModal({ onClose, onConfirm, loading, productTitle }) {
  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal glass-card delete-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={18} />
        </button>

        <div className="modal-header">
          <div className="modal-icon warning">
            <AlertTriangle size={20} />
          </div>
          <h2>Delete Product</h2>
          <p>This action cannot be undone.</p>
        </div>

        <div className="delete-modal-content">
          <p className="warning-text">
            You are about to permanently delete <strong>{productTitle || 'this product'}</strong> and all its price history.
          </p>
        </div>

        <div className="modal-actions">
          <button
            className="btn btn-ghost"
            onClick={onClose}
            disabled={loading}
            id="delete-cancel-btn"
          >
            Cancel
          </button>
          <button
            className="btn btn-danger"
            onClick={onConfirm}
            disabled={loading}
            id="delete-confirm-btn"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="spin" />
                Deleting...
              </>
            ) : (
              <>Delete Product</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
