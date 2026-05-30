import React from 'react';
import { Link } from 'react-router-dom';

function TaskCard({ task }) {
  return (
    <Link to={`/tasks/${task.id}`} style={{ textDecoration: 'none' }}>
      <div className="card" style={{ marginBottom: 12 }}>
        <h3>{task.title}</h3>
        <p style={{ color: '#666', marginTop: 8 }}>{task.description}</p>
        <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
          <span style={{
            padding: '2px 8px',
            borderRadius: 12,
            fontSize: 12,
            background: task.priority === 'high' ? '#ffebee' : task.priority === 'medium' ? '#fff3e0' : '#e8f5e9',
            color: task.priority === 'high' ? '#c62828' : task.priority === 'medium' ? '#ef6c00' : '#2e7d32',
          }}>
            {task.priority}
          </span>
          <span style={{ fontSize: 12, color: '#999' }}>
            {task.status}
          </span>
        </div>
      </div>
    </Link>
  );
}

export default TaskCard;
