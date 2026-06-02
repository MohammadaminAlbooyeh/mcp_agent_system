import { useState, useCallback } from 'react';
import { api } from '../services/api';

export function useExecution() {
  const [executions, setExecutions] = useState([]);
  const [isExecuting, setIsExecuting] = useState(false);

  const execute = useCallback(async (toolCalls) => {
    setIsExecuting(true);
    const results = [];
    for (const call of toolCalls) {
      try {
        const data = await api.post('/executions/execute', call);
        results.push(data);
        setExecutions(prev => [...prev, data]);
      } catch (err) {
        results.push({ error: err.message });
      }
    }
    setIsExecuting(false);
    return results;
  }, []);

  return { executions, isExecuting, execute };
}
