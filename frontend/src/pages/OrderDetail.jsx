import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { apiGet } from '../api.js';

export default function OrderDetail() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const data = await apiGet(`/orders/${orderId}`);
        setOrder(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [orderId]);

  if (loading) {
    return <p>Loading...</p>;
  }
  if (error) {
    return <p className="error">{error}</p>;
  }
  if (!order) {
    return <p>No order found.</p>;
  }

  return (
    <section>
      <h2>Order {order.id}</h2>
      <div className="order-header">
        <p>
          <strong>User ID:</strong> {order.user_id}
        </p>
        <p>
          <strong>Status:</strong> {order.status}
        </p>
        <p>
          <strong>Date:</strong> {new Date(order.order_date).toLocaleString()}
        </p>
      </div>
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>SKU</th>
            <th>Unit Price</th>
            <th>Quantity</th>
            <th>Line Total</th>
          </tr>
        </thead>
        <tbody>
          {order.items.map((item) => {
            const unitPrice = Number(item.unit_price);
            const lineTotal = unitPrice * item.quantity;
            return (
              <tr key={item.id}>
                <td>{item.product_name || item.product_id}</td>
                <td>{item.product_sku || '-'}</td>
                <td>${unitPrice.toFixed(2)}</td>
                <td>{item.quantity}</td>
                <td>${lineTotal.toFixed(2)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
