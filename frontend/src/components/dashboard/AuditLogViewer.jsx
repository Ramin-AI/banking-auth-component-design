// audit log viewer component
// displays authentication audit logs

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthService from '../../services/authService';
import PageTransition from '../common/PageTransition';
import './Dashboard.css';

const AuditLogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      const response = await AuthService.getAuditLogs();
      if (response.success) {
        setLogs(response.logs);
      } else {
        setError('Failed to fetch audit logs');
      }
    } catch (err) {
      setError('Error fetching audit logs');
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType) => {
    const icons = {
      'LOGIN_SUCCESS': '✅',
      'LOGIN_FAILED': '❌',
      'OTP_GENERATED': '🔢',
      'OTP_VERIFIED': '✅',
      'OTP_FAILED': '❌',
      'SSO_INITIATED': '🌐',
      'SSO_SUCCESS': '✅',
      'SSO_FAILED': '❌',
      'LOGOUT': '🚪',
      'TOKEN_REFRESH': '🔄',
    };
    return icons[eventType] || '📝';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading audit logs...</div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Audit Logs</h1>
          <button onClick={() => navigate('/dashboard')} className="btn-back">
            ← Back to Dashboard
          </button>
        </div>

        <div className="dashboard-content">
          {error && <div className="error-message">{error}</div>}

          <div className="audit-logs-card">
            <div className="logs-header">
              <h3>Authentication Events</h3>
              <button onClick={fetchAuditLogs} className="btn-refresh">
                🔄 Refresh
              </button>
            </div>

            {logs.length === 0 ? (
              <p className="no-logs">No audit logs found.</p>
            ) : (
              <div className="logs-table">
                <table>
                  <thead>
                    <tr>
                      <th>Event</th>
                      <th>Type</th>
                      <th>Username</th>
                      <th>IP Address</th>
                      <th>Timestamp</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id}>
                        <td>
                          <span className="event-icon">{getEventIcon(log.event_type)}</span>
                        </td>
                        <td>
                          <span className={`event-type ${log.event_type.toLowerCase()}`}>
                            {log.event_type.replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td>{log.username || '-'}</td>
                        <td>{log.ip_address}</td>
                        <td>{formatDate(log.timestamp)}</td>
                        <td>
                          {log.metadata && Object.keys(log.metadata).length > 0 ? (
                            <details>
                              <summary>View</summary>
                              <pre>{JSON.stringify(log.metadata, null, 2)}</pre>
                            </details>
                          ) : (
                            '-'
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="info-card">
            <h3>About Audit Logs</h3>
            <p>
              Audit logs track all authentication events in the system for security 
              and compliance purposes. Each log entry includes:
            </p>
            <ul>
              <li>Event type (login, logout, OTP, SSO, etc.)</li>
              <li>IP address of the request</li>
              <li>Timestamp of the event</li>
              <li>Additional metadata (method, reason, etc.)</li>
            </ul>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default AuditLogViewer;
