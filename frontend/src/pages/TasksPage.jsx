import React from 'react';
import TaskCard from '../components/TaskCard';
import { useTasks } from '../hooks/useTasks';

function TasksPage() {
  const { tasks, loading } = useTasks();

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
