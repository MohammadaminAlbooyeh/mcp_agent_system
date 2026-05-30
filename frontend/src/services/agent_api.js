import { api } from './api';

export const agentApi = {
  runTask: (task, workflow) =>
    api.post('/agents/run', { task, workflow }),

  getTools: () =>
    api.get('/tools'),
};
