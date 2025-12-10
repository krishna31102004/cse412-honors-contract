import { NavLink, Route, Routes } from 'react-router-dom';

import Products from './pages/Products.jsx';
import Orders from './pages/Orders.jsx';
import OrderDetail from './pages/OrderDetail.jsx';
import CreateOrder from './pages/CreateOrder.jsx';
import Analytics from './pages/Analytics.jsx';

const navItems = [
  { to: '/', label: 'Products', end: true },
  { to: '/orders', label: 'Orders' },
  { to: '/orders/create', label: 'Create Order' },
  { to: '/analytics', label: 'Analytics' },
];

function Layout({ children }) {
  return (
    <div className="app-shell">
      <header>
        <h1>Order Management</h1>
        <nav>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end ?? false}
              className={({ isActive }) => (isActive ? 'active' : undefined)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Products />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/create" element={<CreateOrder />} />
        <Route path="/orders/:orderId" element={<OrderDetail />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Layout>
  );
}
