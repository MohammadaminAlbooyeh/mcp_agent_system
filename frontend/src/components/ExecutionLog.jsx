import React from 'react';

function ExecutionLog({ logs }) {
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3>Execution Log</h3>
      <div style={{
        background: '#1e1e1e',
        color: '#d4d4d4',
        padding: 16,
        borderRadius: 6,
        fontFamily: 'monospace',
        fontSize: 13,
        marginTop: 12,
        maxHeight: 300,
        overflowY: 'auto',
      }}>
        {logs ? logs.map((log, i) => (
          <div key={i} style={{ marginBottom: 4 }}>{log}</div>
        )) : (
          <div style={{ color: '#888' }}>Waiting for execution...</div>
        )}
      </div>
    </div>
  );
}

export default ExecutionLog;
