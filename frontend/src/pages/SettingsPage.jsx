import React, { useState } from 'react';
import { api } from '../services/api';

function SettingsPage() {
  const [settings, setSettings] = useState({
    llmProvider: 'openai',
    maxSteps: 20,
    theme: 'light',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      await api.post('/settings', settings);
      setMessage('Settings saved successfully');
    } catch (err) {
      setMessage(`Failed to save: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1>Settings</h1>
      <div className="card" style={{ marginTop: 16 }}>
        <div style={{ marginBottom: 16 }}>
          <label>LLM Provider</label>
          <select value={settings.llmProvider} onChange={e => setSettings({...settings, llmProvider: e.target.value})}>
            <option value="openai">OpenAI</option>
            <option value="claude">Claude</option>
            <option value="groq">Groq</option>
            <option value="local">Local</option>
          </select>
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>Max Steps</label>
          <input type="number" value={settings.maxSteps} onChange={e => setSettings({...settings, maxSteps: parseInt(e.target.value)})} />
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>Theme</label>
          <select value={settings.theme} onChange={e => setSettings({...settings, theme: e.target.value})}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>
        <button
          style={{ background: '#1a73e8', color: 'white', cursor: 'pointer' }}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
        {message && <p style={{ marginTop: 8, color: message.includes('Failed') ? 'red' : 'green' }}>{message}</p>}
      </div>
    </div>
  );
}

export default SettingsPage;
