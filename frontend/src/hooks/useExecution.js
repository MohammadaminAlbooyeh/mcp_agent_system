import { useState, useCallback } from 'react';

export function useExecution() {
  const [executions, setExecutions] = useState([]);
  const [isExecuting, setIsExecuting] = useState(false);

  const execute = useCallback(async (toolCalls) => {
    setIsExecuting(true);
    const results = [];
    for (const call of toolCalls) {
      try {
        const response = await fetch('/api/executions/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(call),
        });
        const data = await response.json();
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
