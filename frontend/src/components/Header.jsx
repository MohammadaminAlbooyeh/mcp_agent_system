import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header style={{
      background: '#1a73e8',
      color: 'white',
      padding: '16px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      <Link to="/" style={{ color: 'white', textDecoration: 'none', fontSize: 20, fontWeight: 'bold' }}>
        MCP Agent System
      </Link>
      <span>v0.1.0</span>
    </header>
  );
}

export default Header;
