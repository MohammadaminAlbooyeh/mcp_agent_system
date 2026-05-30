import { useState, useCallback } from 'react';
import { agentApi } from '../services/agent_api';

export function useAgent() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runTask = useCallback(async (task, workflow) => {
    setLoading(true);
    setError(null);
    try {
      const data = await agentApi.runTask(task, workflow);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, runTask };
}
