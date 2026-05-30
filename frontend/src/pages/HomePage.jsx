import React from 'react';

function HomePage() {
  return (
    <div>
      <h1>MCP Agent System Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, marginTop: 24 }}>
        <div className="card"><h3>Tasks</h3><p>0 Active</p></div>
        <div className="card"><h3>Tools</h3><p>15 Available</p></div>
        <div className="card"><h3>Executions</h3><p>0 Today</p></div>
        <div className="card"><h3>System</h3><p>Healthy</p></div>
      </div>
    </div>
  );
}

export default HomePage;
