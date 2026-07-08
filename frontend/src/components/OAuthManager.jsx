import React, { useState, useEffect } from 'react';
import axios from 'axios';

function OAuthManager({ sessionId }) {
  const [provider, setProvider] = useState('gmail');
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [authUrl, setAuthUrl] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  // Check auth status on mount or when session changes
  useEffect(() => {
    if (sessionId) {
      checkAuthStatus();
      const interval = setInterval(checkAuthStatus, 10000); // Check every 10s
      return () => clearInterval(interval);
    }
  }, [sessionId, provider]);

  const checkAuthStatus = async () => {
    if (!sessionId) return;

    try {
      const response = await axios.get(
        `${API_BASE}/oauth/status/${provider}`,
        { params: { session_id: sessionId } }
      );
      setAuthStatus(response.data);
      setError(null);
    } catch (err) {
      setAuthStatus(null);
      console.error('Error checking auth status:', err);
    }
  };

  const startAuthorization = async () => {
    if (!sessionId) {
      setError('Please create or select a session first');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE}/oauth/authorize/${provider}`,
        {},
        { params: { session_id: sessionId } }
      );

      setAuthUrl(response.data.auth_url);
      setShowAuthModal(true);
      setError(null);

      // Open auth URL in new window
      const width = 500;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;

      window.open(
        response.data.auth_url,
        'OAuth Authorization',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      // Poll for callback (in real app, use callback endpoint)
      const pollTimer = setInterval(() => {
        checkAuthStatus();
      }, 2000);

      setTimeout(() => clearInterval(pollTimer), 30000); // Stop polling after 30s
    } catch (err) {
      setError(`Failed to start authorization: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthCallback = async (code) => {
    if (!sessionId || !code) return;

    try {
      setLoading(true);
      await axios.post(
        `${API_BASE}/oauth/callback/${provider}`,
        {
          code,
          session_id: sessionId,
          provider,
        }
      );

      await checkAuthStatus();
      setShowAuthModal(false);
      setAuthUrl(null);
      setError(null);
    } catch (err) {
      setError(`Failed to complete authorization: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      await axios.post(
        `${API_BASE}/oauth/refresh/${provider}`,
        {},
        { params: { session_id: sessionId } }
      );

      await checkAuthStatus();
      setError(null);
    } catch (err) {
      setError(`Failed to refresh token: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const disconnect = async () => {
    if (!window.confirm(`Disconnect from ${provider}?`)) return;

    if (!sessionId) return;

    try {
      setLoading(true);
      await axios.post(
        `${API_BASE}/oauth/disconnect/${provider}`,
        {},
        { params: { session_id: sessionId } }
      );

      setAuthStatus(null);
      setError(null);
    } catch (err) {
      setError(`Failed to disconnect: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getAuthStatusColor = (authenticated) => {
    return authenticated ? '#4caf50' : '#f44336';
  };

  const getAuthStatusBg = (authenticated) => {
    return authenticated ? '#e8f5e9' : '#ffebee';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px' }}>
      <h2>OAuth Authorization Management</h2>

      {!sessionId && (
        <div style={{
          padding: '12px',
          background: '#fff3e0',
          border: '1px solid #ff9800',
          borderRadius: '4px',
          color: '#e65100',
          marginBottom: '16px',
        }}>
          ℹ️ Please create or select a session to manage OAuth credentials
        </div>
      )}

      {error && (
        <div style={{
          padding: '12px',
          background: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '4px',
          color: '#c62828',
          marginBottom: '16px',
        }}>
          ❌ {error}
        </div>
      )}

      {/* Provider Selection */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          OAuth Provider
        </label>
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ddd',
          }}
        >
          <option value="gmail">Gmail</option>
          <option value="outlook" disabled>Outlook (Coming Soon)</option>
          <option value="github" disabled>GitHub (Coming Soon)</option>
        </select>
      </div>

      {/* Auth Status Card */}
      {authStatus && (
        <div style={{
          padding: '16px',
          background: getAuthStatusBg(authStatus.authenticated),
          border: `1px solid ${getAuthStatusColor(authStatus.authenticated)}`,
          borderRadius: '8px',
          marginBottom: '20px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ margin: '0 0 8px 0', fontWeight: 'bold', fontSize: '16px' }}>
                {authStatus.authenticated ? '✓ Authenticated' : '✗ Not Authenticated'}
              </p>
              {authStatus.user_email && (
                <p style={{ margin: '0 0 4px 0', color: '#666' }}>
                  Email: {authStatus.user_email}
                </p>
              )}
              {authStatus.expires_at && (
                <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
                  Token expires: {new Date(authStatus.expires_at).toLocaleString()}
                </p>
              )}
              {authStatus.is_expired && (
                <p style={{ margin: '0', color: '#f44336', fontSize: '14px', fontWeight: 'bold' }}>
                  ⚠️ Token Expired - Refresh Required
                </p>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            gap: '8px',
            marginTop: '12px',
          }}>
            {authStatus.authenticated && authStatus.is_expired && (
              <button
                onClick={refreshToken}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  background: '#ff9800',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.6 : 1,
                  fontSize: '14px',
                }}
              >
                {loading ? 'Refreshing...' : 'Refresh Token'}
              </button>
            )}

            {authStatus.authenticated && (
              <button
                onClick={disconnect}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  background: '#f44336',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.6 : 1,
                  fontSize: '14px',
                }}
              >
                {loading ? 'Disconnecting...' : 'Disconnect'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* No Auth Status or Not Authenticated */}
      {!authStatus?.authenticated && (
        <div style={{
          padding: '20px',
          background: '#f5f5f5',
          borderRadius: '8px',
          textAlign: 'center',
        }}>
          <p style={{ marginTop: 0 }}>No active authorization for {provider}</p>
          <button
            onClick={startAuthorization}
            disabled={loading || !sessionId}
            style={{
              padding: '10px 24px',
              background: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading || !sessionId ? 'not-allowed' : 'pointer',
              opacity: loading || !sessionId ? 0.6 : 1,
              fontSize: '16px',
              fontWeight: 'bold',
            }}
          >
            {loading ? 'Authorizing...' : `Authorize with ${provider}`}
          </button>
        </div>
      )}

      {/* Auth Modal */}
      {showAuthModal && authUrl && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            background: 'white',
            padding: '24px',
            borderRadius: '8px',
            maxWidth: '500px',
            width: '90%',
          }}>
            <h3>Authorization in Progress</h3>
            <p>A browser window has opened for authorization. Please complete the authentication flow.</p>
            <p style={{ fontSize: '14px', color: '#666' }}>
              After authorization, this page will update automatically.
            </p>
            <div style={{
              display: 'flex',
              gap: '8px',
              marginTop: '16px',
              justifyContent: 'flex-end',
            }}>
              <button
                onClick={() => {
                  setShowAuthModal(false);
                  setAuthUrl(null);
                }}
                style={{
                  padding: '8px 16px',
                  background: '#e0e0e0',
                  color: '#333',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Close
              </button>
              <button
                onClick={checkAuthStatus}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  background: '#2196f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.6 : 1,
                }}
              >
                {loading ? 'Checking...' : 'Check Status'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Provider Info */}
      <div style={{
        marginTop: '32px',
        padding: '16px',
        background: '#f9f9f9',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#666',
      }}>
        <h4 style={{ margin: '0 0 8px 0' }}>About {provider} Authorization</h4>
        {provider === 'gmail' && (
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li>Access to Gmail API for sending emails</li>
            <li>Tokens are encrypted and stored securely</li>
            <li>Automatic token refresh when expired</li>
            <li>Can disconnect anytime to revoke access</li>
            <li>Session-isolated credentials</li>
          </ul>
        )}
      </div>
    </div>
  );
}

export default OAuthManager;
