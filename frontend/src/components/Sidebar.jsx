import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ShieldAlert,
  TrendingUp,
  PackageSearch,
  Sparkles,
  Activity,
  Pill,
  Menu,
  X,
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { section: 'Overview', items: [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  ]},
  { section: 'Analytics', items: [
    { to: '/risk', label: 'Risk Assessment', icon: ShieldAlert },
    { to: '/forecast', label: 'Demand Forecast', icon: TrendingUp },
    { to: '/stockout', label: 'Stockout Monitor', icon: Activity },
  ]},
  { section: 'Operations', items: [
    { to: '/reorder', label: 'Reorder Engine', icon: PackageSearch },
    { to: '/inventory', label: 'Inventory', icon: Pill },
    { to: '/insights', label: 'AI Insights', icon: Sparkles },
  ]},
];

export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="mobile-menu-btn"
        onClick={() => setMobileOpen(prev => !prev)}
        aria-label="Toggle menu"
        id="mobile-menu-toggle"
      >
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay */}
      <div
        className={`sidebar-overlay ${mobileOpen ? 'open' : ''}`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`} id="sidebar-nav">
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <Pill />
          </div>
          <div className="sidebar-brand-text">
            <span className="sidebar-brand-name">MedChain</span>
            <span className="sidebar-brand-sub">Supply Intelligence</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {navItems.map(group => (
            <div className="sidebar-section" key={group.section}>
              <div className="sidebar-section-label">{group.section}</div>
              {group.items.map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `sidebar-link ${isActive ? 'active' : ''}`
                  }
                  onClick={() => setMobileOpen(false)}
                  id={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <item.icon />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className="sidebar-status-dot" />
            <span>System Online</span>
          </div>
        </div>
      </aside>
    </>
  );
}
