import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, BarChart3, Zap, LogOut, ChevronDown, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

export default function Navbar({ onSearch }) {
  const [query, setQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const menuRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handler(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query.trim());
  };

  function handleLogout() {
    logout();
    navigate('/login');
  }

  const initials = user?.name
    ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">
            <BarChart3 size={22} />
            <Zap size={10} className="brand-spark" />
          </div>
          <span className="brand-text">
            Data<span className="gradient-text">Lens</span>
          </span>
        </Link>

        <form className="navbar-search" onSubmit={handleSubmit}>
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search tracked products..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (e.target.value === '') onSearch('');
            }}
          />
        </form>

        <div className="navbar-actions">
          {/* User menu */}
          <div className="nav-user-menu" ref={menuRef}>
            <button
              id="nav-user-btn"
              className="nav-user-btn"
              onClick={() => setMenuOpen(v => !v)}
              aria-expanded={menuOpen}
            >
              <div className="nav-avatar">{initials}</div>
              <span className="nav-user-name">{user?.name?.split(' ')[0] ?? 'User'}</span>
              <ChevronDown size={14} className={`nav-chevron ${menuOpen ? 'open' : ''}`} />
            </button>

            {menuOpen && (
              <div className="nav-dropdown">
                <div className="nav-dropdown-header">
                  <p className="nav-dd-name">{user?.name}</p>
                  <p className="nav-dd-email">{user?.email}</p>
                </div>
                <div className="nav-dropdown-divider" />
                <button
                  id="nav-logout-btn"
                  className="nav-dd-item nav-dd-item--danger"
                  onClick={handleLogout}
                >
                  <LogOut size={15} />
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
