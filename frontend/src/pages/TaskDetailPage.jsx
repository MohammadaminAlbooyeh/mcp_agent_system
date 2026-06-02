import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { taskApi } from '../services/task_api';

function TaskDetailPage() {
  const { id } = useParams();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    taskApi.getTask(id).then(data => {
      setTask(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  if (loading) return <div><h1>Task Detail</h1><div className="card" style={{ marginTop: 16 }}><p>Loading...</p></div></div>;
  if (!task) return <div><h1>Task Detail</h1><div className="card" style={{ marginTop: 16 }}><p>Task not found</p></div></div>;

  return (
    <div>
      <h1>Task Detail</h1>
      <div className="card" style={{ marginTop: 16 }}>
        <p><strong>ID:</strong> {task.id}</p>
        <p><strong>Title:</strong> {task.title}</p>
        <p><strong>Description:</strong> {task.description}</p>
        <p><strong>Priority:</strong> {task.priority}</p>
        <p><strong>Status:</strong> {task.status}</p>
        <p><strong>Created:</strong> {new Date(task.created_at).toLocaleString()}</p>
      </div>
    </div>
  );
}

export default TaskDetailPage;
