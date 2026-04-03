const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchProducts() {
  return request('/product');
}

export async function addProduct(url) {
  return request('/product', {
    method: 'POST',
    body: JSON.stringify({ url }),
  });
}

export async function searchProducts(keyword) {
  return request(`/product/search/${encodeURIComponent(keyword)}`);
}

export async function toggleTracking(productId, active) {
  return request(`/product/track/${productId}?active=${active}`, {
    method: 'PATCH',
  });
}

export async function fetchFullHistory(productId) {
  return request(`/history/all/${productId}`);
}

export async function deleteProduct(productId) {
  return request(`/product/${productId}`, {
    method: 'DELETE',
  });
}
