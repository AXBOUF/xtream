import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Moon, Sun, Droplet } from 'lucide-react'
import './Navigation.css'

function Navigation({ isDarkMode, setIsDarkMode }) {
  const [isOpen, setIsOpen] = React.useState(false)
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className={`navbar ${isDarkMode ? 'dark' : ''}`}>
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <Droplet size={24} />
          <span>Xtream Wash</span>
        </Link>

        <button className="menu-toggle" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <div className={`nav-menu ${isOpen ? 'active' : ''}`}>
          <Link
            to="/"
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => setIsOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            to="/record"
            className={`nav-link ${isActive('/record') ? 'active' : ''}`}
            onClick={() => setIsOpen(false)}
          >
            Daily Record
          </Link>
          <Link
            to="/reports"
            className={`nav-link ${isActive('/reports') ? 'active' : ''}`}
            onClick={() => setIsOpen(false)}
          >
            Reports
          </Link>
        </div>

        <button
          className="theme-toggle"
          onClick={() => setIsDarkMode(!isDarkMode)}
          title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </nav>
  )
}

export default Navigation
