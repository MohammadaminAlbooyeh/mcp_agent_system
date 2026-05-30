import { useState, useEffect, useCallback } from 'react';
import { toolApi } from '../services/tool_api';

export function useTools() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchTools = useCallback(async () => {
    setLoading(true);
    try {
      const data = await toolApi.listTools();
      setTools(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTools(); }, [fetchTools]);

  return { tools, loading, refetch: fetchTools };
}
