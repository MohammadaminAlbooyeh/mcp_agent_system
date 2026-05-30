import React from 'react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/agent', label: 'Agent' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/tools', label: 'Tools' },
  { to: '/monitoring', label: 'Monitoring' },
  { to: '/settings', label: 'Settings' },
];

function Sidebar() {
  return (
    <nav style={{
      width: 220,
      background: 'white',
      borderRight: '1px solid #dcdde1',
      padding: '16px 0',
      minHeight: 'calc(100vh - 60px)',
    }}>
      {links.map(link => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.to === '/'}
          style={({ isActive }) => ({
            display: 'block',
            padding: '10px 24px',
            color: isActive ? '#1a73e8' : '#2c3e50',
            background: isActive ? '#e8f0fe' : 'transparent',
            textDecoration: 'none',
            fontWeight: isActive ? 'bold' : 'normal',
            borderLeft: isActive ? '3px solid #1a73e8' : '3px solid transparent',
          })}
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}

export default Sidebar;
