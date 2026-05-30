import React, { useState, useEffect } from 'react';
import TaskCard from '../components/TaskCard';

function TasksPage() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetch('/api/tasks')
      .then(res => res.json())
      .then(setTasks)
      .catch(console.error);
  }, []);

  return (
    <div>
      <h1>Tasks</h1>
      <div style={{ marginTop: 16 }}>
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} />
        ))}
        {tasks.length === 0 && <p className="card">No tasks yet</p>}
      </div>
    </div>
  );
}

export default TasksPage;
