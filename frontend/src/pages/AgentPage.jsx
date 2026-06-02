import React, { useState } from 'react';
import TaskInput from '../components/TaskInput';
import ExecutionLog from '../components/ExecutionLog';
import ReasoningViewer from '../components/ReasoningViewer';
import ResultViewer from '../components/ResultViewer';
import { agentApi } from '../services/agent_api';
import { wsService } from '../services/websocket';

function AgentPage() {
  const [task, setTask] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [liveLogs, setLiveLogs] = useState([]);

  const handleSubmit = async (taskText) => {
    setLoading(true);
    setTask(taskText);
    setLiveLogs([]);
    try {
      wsService.connect('/ws/agent');
      wsService.on('execution', (data) => {
        setLiveLogs(prev => [...prev, `[${data.tool}] ${data.status} (${data.duration_ms}ms)`]);
      });
      const data = await agentApi.runTask(taskText);
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
      {(loading || liveLogs.length > 0) && <ExecutionLog logs={liveLogs} />}
      {result && <ResultViewer result={result} />}
      {result && <ReasoningViewer task={task} />}
    </div>
  );
}

export default AgentPage;
