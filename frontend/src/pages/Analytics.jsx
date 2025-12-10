import { useEffect, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts';

import { apiGet } from '../api.js';

export default function Analytics() {
  const [filters, setFilters] = useState({ start_date: '', end_date: '' });
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    setError('');
    try {
      const params = {
        start_date: filters.start_date || undefined,
        end_date: filters.end_date || undefined,
      };
      const resp = await apiGet('/analytics/daily-sales', params);
      const normalized = (resp.items || []).map((row) => ({
        ...row,
        total_sales: Number(row.total_sales),
      }));
      setData(normalized);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  }

  return (
    <section>
      <h2>Daily Sales</h2>
      <div className="filters">
        <input type="date" name="start_date" value={filters.start_date} onChange={handleChange} />
        <input type="date" name="end_date" value={filters.end_date} onChange={handleChange} />
        <button onClick={fetchData}>Apply</button>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && data.length === 0 && <p>No data for selected range.</p>}
      {data.length > 0 && (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="sale_day" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="total_sales" stroke="#2563eb" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
