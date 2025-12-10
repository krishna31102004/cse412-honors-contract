import { useEffect, useState } from 'react';

import { apiGet } from '../api.js';

const DEFAULT_LIMIT = 10;

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    limit: DEFAULT_LIMIT,
    offset: 0,
    category_id: '',
    q: '',
    min_price: '',
    max_price: '',
  });
  const [pagination, setPagination] = useState({ total: 0 });

  useEffect(() => {
    apiGet('/categories')
      .then((data) => setCategories(data.items || []))
      .catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [filters.limit, filters.offset, filters.category_id, filters.q, filters.min_price, filters.max_price]);

  async function fetchProducts() {
    setLoading(true);
    setError('');
    try {
      const resp = await apiGet('/products', {
        limit: filters.limit,
        offset: filters.offset,
        category_id: filters.category_id ? Number(filters.category_id) : undefined,
        q: filters.q || undefined,
        min_price: filters.min_price !== '' ? Number(filters.min_price) : undefined,
        max_price: filters.max_price !== '' ? Number(filters.max_price) : undefined,
      });
      setProducts(resp.items);
      setPagination({ total: resp.total, limit: resp.limit, offset: resp.offset });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(e) {
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
      <h2>Products</h2>
      <div className="filters">
        <select name="category_id" value={filters.category_id} onChange={handleInputChange}>
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
        <input name="q" value={filters.q} onChange={handleInputChange} placeholder="Search name or SKU" />
        <input name="min_price" value={filters.min_price} onChange={handleInputChange} placeholder="Min price" type="number" step="0.01" />
        <input name="max_price" value={filters.max_price} onChange={handleInputChange} placeholder="Max price" type="number" step="0.01" />
        <select name="limit" value={filters.limit} onChange={handleInputChange}>
          {[10, 25, 50].map((n) => (
            <option key={n} value={n}>
              {n} per page
            </option>
          ))}
        </select>
        <button onClick={() => fetchProducts()}>Apply</button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>SKU</th>
            <th>Price</th>
            <th>In Stock</th>
            <th>Category</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{p.sku}</td>
              <td>${Number(p.price).toFixed(2)}</td>
              <td>{p.in_stock}</td>
              <td>{p.category_id}</td>
            </tr>
          ))}
          {!loading && products.length === 0 && (
            <tr>
              <td colSpan={5}>No products found.</td>
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
