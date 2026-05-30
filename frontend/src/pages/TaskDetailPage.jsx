import React from 'react';
import { useParams } from 'react-router-dom';

function TaskDetailPage() {
  const { id } = useParams();

  return (
    <div>
      <h1>Task Detail</h1>
      <div className="card" style={{ marginTop: 16 }}>
        <p><strong>ID:</strong> {id}</p>
        <p><strong>Status:</strong> Pending</p>
      </div>
    </div>
  );
}

export default TaskDetailPage;
