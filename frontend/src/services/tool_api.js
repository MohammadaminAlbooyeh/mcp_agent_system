import { api } from './api';

export const toolApi = {
  listTools: () =>
    api.get('/tools'),

  executeTool: (name, params) =>
    api.post('/tools/execute', { name, params }),
};
