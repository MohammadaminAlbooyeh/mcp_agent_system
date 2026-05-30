export const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8001';

export const TASK_PRIORITIES = ['low', 'medium', 'high', 'critical'];
export const TASK_STATUSES = ['pending', 'in_progress', 'completed', 'failed'];
export const LLM_PROVIDERS = ['openai', 'claude', 'groq', 'local'];

export const TOOL_CATEGORIES = [
  'web_tools', 'database_tools', 'file_tools', 'email_tools',
  'api_tools', 'code_tools', 'utility_tools',
];
