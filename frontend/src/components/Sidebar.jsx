import { NavLink } from 'react-router-dom'

const navigation = [
  { label: 'Dashboard', path: '/', icon: '◫' },
  { label: 'Transactions', path: '/transactions', icon: '↕' },
  { label: 'Invoices', path: '/invoices', icon: '▤' },
  { label: 'AI Assistant', path: '/chat', icon: '✧' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">F</div>
        <div>
          <h2>FinVoice AI</h2>
          <span>Finance workspace</span>
        </div>
      </div>

      <p className="nav-heading">WORKSPACE</p>

      <nav className="sidebar-nav">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-dot" />
        <span>Finance workspace</span>
      </div>
    </aside>
  )
}
