import { useState } from 'react';
import { Link } from 'react-router-dom';

import { apiPost } from '../api.js';

const STATUS_OPTIONS = ['pending', 'paid', 'shipped', 'delivered', 'cancelled'];

export default function CreateOrder() {
  const [userId, setUserId] = useState('');
  const [status, setStatus] = useState('pending');
  const [items, setItems] = useState([{ product_id: '', quantity: 1 }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(null);

  function addItem() {
    setItems((prev) => [...prev, { product_id: '', quantity: 1 }]);
  }

  function removeItem(index) {
    setItems((prev) => prev.filter((_, idx) => idx !== index));
  }

  function updateItem(index, field, value) {
    setItems((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, [field]: value } : item))
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess(null);

    const productIds = items.map((item) => Number(item.product_id)).filter(Boolean);
    if (productIds.length !== new Set(productIds).size) {
      setError('Each product can only appear once.');
      return;
    }

    const payload = {
      user_id: Number(userId),
      status,
      items: items
        .filter((item) => item.product_id)
        .map((item) => ({ product_id: Number(item.product_id), quantity: Number(item.quantity) })),
    };

    if (!payload.user_id || payload.items.length === 0) {
      setError('User ID and at least one item are required.');
      return;
    }

    setLoading(true);
    try {
      const order = await apiPost('/orders', payload);
      setSuccess(order);
      setItems([{ product_id: '', quantity: 1 }]);
      setUserId('');
      setStatus('pending');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h2>Create Order</h2>
      <form onSubmit={handleSubmit} className="order-form">
        <div className="form-row">
          <label className="form-field">
            User ID
            <input type="number" value={userId} onChange={(e) => setUserId(e.target.value)} min="1" required />
          </label>
          <label className="form-field">
            Status
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              {STATUS_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="items-list">
          <div className="items-header">
            <h3>Items</h3>
            <button type="button" onClick={addItem}>
              Add Item
            </button>
          </div>
          {items.map((item, index) => (
            <div key={index} className="item-row">
              <label className="form-field">
                Product ID
                <input
                  type="number"
                  min="1"
                  value={item.product_id}
                  onChange={(e) => updateItem(index, 'product_id', e.target.value)}
                  required
                />
              </label>
              <label className="form-field">
                Quantity
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                  required
                />
              </label>
              {items.length > 1 && (
                <button type="button" className="remove" onClick={() => removeItem(index)}>
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>

        {error && <p className="error">{error}</p>}
        {success && (
          <p className="success">
            Order created with ID {success.id}. <Link to={`/orders/${success.id}`}>View order</Link>
          </p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Order'}
        </button>
      </form>
    </section>
  );
}
