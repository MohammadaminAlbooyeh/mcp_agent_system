import React, { useState } from 'react';
import TaskInput from '../components/TaskInput';
import ExecutionLog from '../components/ExecutionLog';
import ReasoningViewer from '../components/ReasoningViewer';
import ResultViewer from '../components/ResultViewer';

function AgentPage() {
  const [task, setTask] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (taskText) => {
    setLoading(true);
    setTask(taskText);
    try {
      const response = await fetch('/api/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: taskText }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  return (
    <div>
      <h1>Agent Interface</h1>
      <TaskInput onSubmit={handleSubmit} loading={loading} />
      {loading && <ExecutionLog />}
      {result && <ResultViewer result={result} />}
      {result && <ReasoningViewer task={task} />}
    </div>
  );
}

export default AgentPage;
