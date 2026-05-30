import { useState, useEffect, useCallback } from 'react';

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onopen = () => setConnected(true);
    ws.onmessage = (event) => {
      try {
        setData(JSON.parse(event.data));
      } catch {
        setData(event.data);
      }
    };
    ws.onclose = () => setConnected(false);
    return () => ws.close();
  }, [url]);

  const send = useCallback((message) => {
    if (connected) {
      ws.send(JSON.stringify(message));
    }
  }, [connected]);

  return { data, connected, send };
}
