import { api } from './api';

export const taskApi = {
  listTasks: () =>
    api.get('/tasks'),

  getTask: (id) =>
    api.get(`/tasks/${id}`),

  createTask: (task) =>
    api.post('/tasks', task),
};
