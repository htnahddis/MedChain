import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import RiskPage from './pages/RiskPage';
import ForecastPage from './pages/ForecastPage';
import StockoutPage from './pages/StockoutPage';
import ReorderPage from './pages/ReorderPage';
import InventoryPage from './pages/InventoryPage';
import InsightsPage from './pages/InsightsPage';

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/risk" element={<RiskPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/stockout" element={<StockoutPage />} />
        <Route path="/reorder" element={<ReorderPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/insights" element={<InsightsPage />} />
      </Routes>
    </div>
  );
}
