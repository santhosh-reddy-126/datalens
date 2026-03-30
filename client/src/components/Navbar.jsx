import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, BarChart3, Zap } from 'lucide-react';
import './Navbar.css';

export default function Navbar({ onSearch }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query.trim());
  };

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
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="nav-link"
          >
            Docs
          </a>
        </div>
      </div>
    </nav>
  );
}
