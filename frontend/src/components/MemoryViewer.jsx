import React from 'react';

function MemoryViewer({ memory }) {
  if (!memory) return null;

  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3>Agent Memory</h3>
      <pre style={{
        background: '#f8f9fa',
        padding: 12,
        borderRadius: 6,
        fontSize: 13,
        marginTop: 12,
        overflowX: 'auto',
      }}>
        {JSON.stringify(memory, null, 2)}
      </pre>
    </div>
  );
}

export default MemoryViewer;
