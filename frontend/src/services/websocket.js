const WS_BASE = process.env.REACT_APP_WS_URL || 'ws://localhost:8001';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = {};
  }

  connect(path = '/ws') {
    this.ws = new WebSocket(`${WS_BASE}${path}`);
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const type = data.type || 'message';
      if (this.listeners[type]) {
        this.listeners[type].forEach(fn => fn(data));
      }
    };
    this.ws.onclose = () => {
      setTimeout(() => this.connect(path), 3000);
    };
  }

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    this.ws?.close();
  }
}

export const wsService = new WebSocketService();
