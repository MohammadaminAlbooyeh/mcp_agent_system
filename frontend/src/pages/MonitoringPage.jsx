import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { wsService } from '../services/websocket';

function MonitoringPage() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    api.get('/monitoring/metrics').then(setMetrics).catch(console.error);
    wsService.connect('/ws/monitoring');
    wsService.on('metrics', (data) => setMetrics(data));
  }, []);

  return (
    <div>
      <h1>Monitoring</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginTop: 24 }}>
        <div className="card"><h3>Completed</h3><p>{metrics?.tasks_completed || 0}</p></div>
        <div className="card"><h3>Failed</h3><p>{metrics?.tasks_failed || 0}</p></div>
        <div className="card"><h3>Tools Called</h3><p>{metrics?.tools_called || 0}</p></div>
        <div className="card"><h3>Avg Time</h3><p>{metrics?.avg_execution_time || 0}s</p></div>
      </div>
    </div>
  );
}

export default MonitoringPage;
