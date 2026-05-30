import React, { useState } from 'react';

function SettingsPage() {
  const [settings, setSettings] = useState({
    llmProvider: 'openai',
    maxSteps: 20,
    theme: 'light',
  });

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
        <button style={{ background: '#1a73e8', color: 'white' }}>Save Settings</button>
      </div>
    </div>
  );
}

export default SettingsPage;
