import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SessionManager() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [creating, setCreating] = useState(false);
  const [userId, setUserId] = useState('');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  // Fetch sessions on component mount
  useEffect(() => {
    fetchSessions();
    const interval = setInterval(fetchSessions, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/sessions`);
      setSessions(response.data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch sessions: ${err.message}`);
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    try {
      setCreating(true);
      const response = await axios.post(`${API_BASE}/sessions/create`, {
        user_id: userId || undefined,
        metadata: {
          created_at: new Date().toISOString(),
        },
      });
      setSessions([...sessions, response.data]);
      setSelectedSession(response.data);
      setUserId('');
      setError(null);
    } catch (err) {
      setError(`Failed to create session: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const pauseSession = async (sessionId) => {
    try {
      await axios.post(`${API_BASE}/sessions/${sessionId}/pause`);
      await fetchSessions();
    } catch (err) {
      setError(`Failed to pause session: ${err.message}`);
    }
  };

  const resumeSession = async (sessionId) => {
    try {
      await axios.post(`${API_BASE}/sessions/${sessionId}/resume`);
      await fetchSessions();
    } catch (err) {
      setError(`Failed to resume session: ${err.message}`);
    }
  };

  const completeSession = async (sessionId) => {
    try {
      await axios.post(`${API_BASE}/sessions/${sessionId}/complete`);
      await fetchSessions();
    } catch (err) {
      setError(`Failed to complete session: ${err.message}`);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this session?')) return;
    try {
      await axios.delete(`${API_BASE}/sessions/${sessionId}`);
      setSessions(sessions.filter(s => s.id !== sessionId));
      if (selectedSession?.id === sessionId) {
        setSelectedSession(null);
      }
    } catch (err) {
      setError(`Failed to delete session: ${err.message}`);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#4caf50',
      paused: '#ff9800',
      completed: '#2196f3',
      expired: '#f44336',
    };
    return colors[status] || '#999';
  };

  const getStatusBgColor = (status) => {
    const colors = {
      active: '#e8f5e9',
      paused: '#fff3e0',
      completed: '#e3f2fd',
      expired: '#ffebee',
    };
    return colors[status] || '#f5f5f5';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Session Management</h1>

      {error && (
        <div style={{
          padding: '12px',
          marginBottom: '16px',
          background: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '4px',
          color: '#c62828',
        }}>
          {error}
        </div>
      )}

      {/* Create Session Section */}
      <div style={{
        padding: '20px',
        background: '#f5f5f5',
        borderRadius: '8px',
        marginBottom: '24px',
      }}>
        <h2>Create New Session</h2>
        <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
          <input
            type="email"
            placeholder="User ID (optional)"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            style={{
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd',
              flex: 1,
            }}
          />
          <button
            onClick={createSession}
            disabled={creating}
            style={{
              padding: '8px 16px',
              background: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: creating ? 'not-allowed' : 'pointer',
              opacity: creating ? 0.6 : 1,
            }}
          >
            {creating ? 'Creating...' : 'Create Session'}
          </button>
        </div>
      </div>

      {/* Sessions Grid */}
      <div>
        <h2>Active Sessions ({sessions.length})</h2>
        {loading && <p>Loading sessions...</p>}
        {sessions.length === 0 && !loading && <p>No active sessions</p>}

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '16px',
          marginTop: '16px',
        }}>
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => setSelectedSession(session)}
              style={{
                padding: '16px',
                border: selectedSession?.id === session.id ? '2px solid #2196f3' : '1px solid #ddd',
                borderRadius: '8px',
                background: selectedSession?.id === session.id ? '#e3f2fd' : 'white',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h3 style={{ margin: '0 0 8px 0' }}>
                    {session.id.substring(0, 8)}...
                  </h3>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    User: {session.user_id || 'Anonymous'}
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
                    Steps: {session.step_count || 0}
                  </p>
                </div>
                <span
                  style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    background: getStatusBgColor(session.status),
                    color: getStatusColor(session.status),
                  }}
                >
                  {session.status}
                </span>
              </div>

              <div style={{ marginTop: '12px', fontSize: '12px', color: '#999' }}>
                <p>Created: {new Date(session.created_at).toLocaleString()}</p>
                <p>Expires: {new Date(session.expires_at).toLocaleString()}</p>
              </div>

              <div style={{
                display: 'flex',
                gap: '8px',
                marginTop: '12px',
                justifyContent: 'flex-end',
              }}>
                {session.status === 'active' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      pauseSession(session.id);
                    }}
                    style={{
                      padding: '4px 12px',
                      fontSize: '12px',
                      background: '#ff9800',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Pause
                  </button>
                )}

                {session.status === 'paused' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      resumeSession(session.id);
                    }}
                    style={{
                      padding: '4px 12px',
                      fontSize: '12px',
                      background: '#4caf50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Resume
                  </button>
                )}

                {session.status !== 'completed' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      completeSession(session.id);
                    }}
                    style={{
                      padding: '4px 12px',
                      fontSize: '12px',
                      background: '#2196f3',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Complete
                  </button>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  style={{
                    padding: '4px 12px',
                    fontSize: '12px',
                    background: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Session Details */}
      {selectedSession && (
        <div style={{
          marginTop: '32px',
          padding: '20px',
          background: '#f9f9f9',
          borderRadius: '8px',
          border: '1px solid #e0e0e0',
        }}>
          <h2>Session Details</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <p><strong>Session ID:</strong> {selectedSession.id}</p>
              <p><strong>User ID:</strong> {selectedSession.user_id || 'N/A'}</p>
              <p><strong>Status:</strong> {selectedSession.status}</p>
              <p><strong>Step Count:</strong> {selectedSession.step_count}</p>
            </div>
            <div>
              <p><strong>Created:</strong> {new Date(selectedSession.created_at).toLocaleString()}</p>
              <p><strong>Updated:</strong> {new Date(selectedSession.updated_at).toLocaleString()}</p>
              <p><strong>Expires:</strong> {new Date(selectedSession.expires_at).toLocaleString()}</p>
              <p><strong>Active:</strong> {selectedSession.is_active ? 'Yes' : 'No'}</p>
            </div>
          </div>

          <div style={{ marginTop: '16px' }}>
            <h3>State</h3>
            <pre style={{
              background: '#fff',
              padding: '12px',
              borderRadius: '4px',
              border: '1px solid #ddd',
              overflow: 'auto',
              maxHeight: '300px',
            }}>
              {JSON.stringify(selectedSession.state, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default SessionManager;
