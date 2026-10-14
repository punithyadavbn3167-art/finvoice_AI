
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'

export default function Layout({ theme, toggleTheme }) {
  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <div className="theme-toolbar">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? ' Light Mode' : ' Dark Mode'}
          </button>
        </div>

        <Outlet />
      </main>
    </div>
  )
}
