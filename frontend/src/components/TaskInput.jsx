import React, { useState } from 'react';

function TaskInput({ onSubmit, loading }) {
  const [task, setTask] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (task.trim()) {
      onSubmit(task);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card" style={{ marginTop: 16 }}>
      <textarea
        value={task}
        onChange={e => setTask(e.target.value)}
        placeholder="Describe a task for the agent..."
        rows={4}
        style={{ marginBottom: 12 }}
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !task.trim()}
        style={{
          background: loading ? '#ccc' : '#1a73e8',
          color: 'white',
          padding: '10px 24px',
        }}
      >
        {loading ? 'Running...' : 'Run Task'}
      </button>
    </form>
  );
}

export default TaskInput;
