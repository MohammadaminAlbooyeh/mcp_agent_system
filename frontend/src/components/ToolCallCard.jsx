import React from 'react';

function ToolCallCard({ call }) {
  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4>{call.tool_name}</h4>
        <span style={{
          padding: '2px 8px',
          borderRadius: 12,
          fontSize: 12,
          background: call.status === 'success' ? '#e8f5e9' : '#ffebee',
          color: call.status === 'success' ? '#2e7d32' : '#c62828',
        }}>
          {call.status}
        </span>
      </div>
      <pre style={{ fontSize: 12, marginTop: 8, background: '#f5f5f5', padding: 8, borderRadius: 4 }}>
        {JSON.stringify(call.params, null, 2)}
      </pre>
      {call.result && (
        <p style={{ marginTop: 8, fontSize: 13, color: '#666' }}>
          {call.result.substring(0, 200)}
        </p>
      )}
    </div>
  );
}

export default ToolCallCard;
