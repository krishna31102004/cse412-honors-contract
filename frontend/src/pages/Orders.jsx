import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { apiGet } from '../api.js';

const DEFAULT_LIMIT = 10;

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [filters, setFilters] = useState({ limit: DEFAULT_LIMIT, offset: 0, user_id: '', start_date: '', end_date: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({ total: 0 });

  useEffect(() => {
    fetchOrders();
  }, [filters.limit, filters.offset, filters.user_id, filters.start_date, filters.end_date]);

  async function fetchOrders() {
    setLoading(true);
    setError('');
    try {
      const startIso = filters.start_date ? new Date(filters.start_date).toISOString() : undefined;
      const endIso = filters.end_date ? new Date(filters.end_date).toISOString() : undefined;
      const resp = await apiGet('/orders', {
        limit: filters.limit,
        offset: filters.offset,
        user_id: filters.user_id ? Number(filters.user_id) : undefined,
        start_date: startIso,
        end_date: endIso,
      });
      setOrders(resp.items);
      setPagination({ total: resp.total, limit: resp.limit, offset: resp.offset });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFilters((prev) => {
      const nextValue = name === 'limit' ? Number(value) : value;
      return { ...prev, [name]: nextValue, offset: 0 };
    });
  }

  function changePage(delta) {
    setFilters((prev) => ({ ...prev, offset: Math.max(0, prev.offset + delta * prev.limit) }));
  }

  const total = pagination.total || 0;
  const start = total ? filters.offset + 1 : 0;
  const end = total ? Math.min(filters.offset + filters.limit, total) : 0;

  return (
    <section>
      <h2>Orders</h2>
      <div className="filters">
        <input name="user_id" value={filters.user_id} onChange={handleChange} placeholder="User ID" type="number" min="1" />
        <input name="start_date" value={filters.start_date} onChange={handleChange} type="date" />
        <input name="end_date" value={filters.end_date} onChange={handleChange} type="date" />
        <select name="limit" value={filters.limit} onChange={handleChange}>
          {[10, 25, 50].map((n) => (
            <option key={n} value={n}>
              {n} per page
            </option>
          ))}
        </select>
        <button onClick={() => fetchOrders()}>Apply</button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>User ID</th>
            <th>Date</th>
            <th>Status</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>{o.id}</td>
              <td>{o.user_id}</td>
              <td>{new Date(o.order_date).toLocaleString()}</td>
              <td>{o.status}</td>
              <td>
                <Link to={`/orders/${o.id}`}>View</Link>
              </td>
            </tr>
          ))}
          {!loading && orders.length === 0 && (
            <tr>
              <td colSpan={5}>No orders found.</td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="pagination">
        <button onClick={() => changePage(-1)} disabled={filters.offset === 0}>
          Previous
        </button>
        <span>
          Showing {start} - {end} of {total}
        </span>
        <button onClick={() => changePage(1)} disabled={filters.offset + filters.limit >= total}>
          Next
        </button>
      </div>
    </section>
  );
}
