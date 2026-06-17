// dashboard component
// protected dashboard page showing user info

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import AuthService from '../../services/authService';
import PageTransition from '../common/PageTransition';
import AnimatedLogoutButton from '../common/AnimatedLogoutButton';
import './Dashboard.css';

const Dashboard = () => {
  const [protectedData, setProtectedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', is_staff: false });
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchProtectedData();
    if (currentUser?.is_staff) {
      fetchUsers();
    }
  }, [currentUser]);

  const fetchProtectedData = async () => {
    try {
      const response = await AuthService.getProtectedData();
      setProtectedData(response);
    } catch (error) {
      console.error('Error fetching protected data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    setUsersLoading(true);
    try {
      const data = await AuthService.getAllUsers();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setUsersLoading(false);
    }
  };

  const handleToggleOTP = async (userId) => {
    try {
      const response = await AuthService.toggleUserOTP(userId);
      setUsers(users.map(u => u.id === userId ? { ...u, otp_enabled: response.otp_enabled } : u));
    } catch (error) {
      console.error('Error toggling OTP:', error);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await AuthService.createUser(newUser);
      setNewUser({ username: '', email: '', password: '', is_staff: false });
      fetchUsers();
    } catch (error) {
      console.error('Error adding user:', error);
      alert('Error adding user: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await AuthService.deleteUser(userId);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const handleToggleActive = async (userId) => {
    try {
      const response = await AuthService.toggleUserActive(userId);
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: response.is_active } : u));
    } catch (error) {
      console.error('Error toggling active:', error);
    }
  };

  const handleResetPassword = async (userId) => {
    if (window.confirm('Reset this user\'s password to "Password123!"?')) {
      try {
        await AuthService.resetUserPassword(userId);
        alert('Password successfully reset to Password123!');
      } catch (error) {
        console.error('Error resetting password:', error);
        alert('Error resetting password');
      }
    }
  };

  const [pwForm, setPwForm] = useState({ old: '', new: '', confirm: '' });
  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (pwForm.new !== pwForm.confirm) {
      alert('New passwords do not match!');
      return;
    }
    try {
      await AuthService.changePassword(pwForm.old, pwForm.new);
      alert('Password successfully changed!');
      setPwForm({ old: '', new: '', confirm: '' });
    } catch (error) {
      console.error('Error changing password:', error);
      alert('Error: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleToggleMyOTP = async () => {
    try {
      await AuthService.toggleMyOTP();
      alert('OTP setting toggled. Please log in again to see changes or the context will update automatically if implemented.');
    } catch (error) {
      console.error('Error toggling my OTP:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Banking Dashboard</h1>
          <AnimatedLogoutButton onLogout={handleLogout} />
        </div>

        <div className="dashboard-content">
          <div className="welcome-card">
            <h2>Welcome, {currentUser?.username}! 👋</h2>
            <p>You have successfully authenticated to the banking platform.</p>
          </div>

          <div className="info-grid">
            <div className="info-card">
              <h3>User Information</h3>
              <div className="info-item">
                <span className="label">Username:</span>
                <span className="value">{currentUser?.username}</span>
              </div>
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{currentUser?.email}</span>
              </div>
              <div className="info-item">
                <span className="label">User ID:</span>
                <span className="value">{currentUser?.id}</span>
              </div>
              <div className="info-item">
                <span className="label">OTP Enabled:</span>
                <span className="value">{currentUser?.otp_enabled ? '✅ Yes' : '❌ No'}</span>
              </div>
              {currentUser?.sso_provider && (
                <div className="info-item">
                  <span className="label">SSO Provider:</span>
                  <span className="value">{currentUser.sso_provider}</span>
                </div>
              )}
            </div>

            <div className="info-card">
              <h3>Protected Resource</h3>
              {protectedData && (
                <>
                  <p className="success-message">{protectedData.message}</p>
                  <div className="info-item">
                    <span className="label">Status:</span>
                    <span className="value success">✅ Authenticated</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {currentUser?.is_staff && (
            <div className="admin-control-center">
              <h3>Admin Control Center</h3>
              {usersLoading ? (
                <p>Loading users...</p>
              ) : (
                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>OTP Enabled</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map(user => (
                        <tr key={user.id}>
                          <td>{user.id}</td>
                          <td>{user.username}</td>
                          <td>{user.email}</td>
                          <td>{user.is_staff ? 'Admin' : 'Standard'}</td>
                          <td>
                            <span className={`status-badge ${user.is_active ? 'success' : 'danger'}`}>
                              {user.is_active ? 'Active' : 'Suspended'}
                            </span>
                          </td>
                          <td>
                            <span className={`status-badge ${user.otp_enabled ? 'success' : 'danger'}`}>
                              {user.otp_enabled ? 'Yes' : 'No'}
                            </span>
                          </td>
                          <td className="actions-cell">
                            <button 
                              className="btn-action-small"
                              onClick={() => handleToggleActive(user.id)}
                              disabled={user.id === currentUser.id}
                            >
                              Toggle Status
                            </button>
                            <button 
                              className="btn-action-small"
                              onClick={() => handleResetPassword(user.id)}
                            >
                              Reset PW
                            </button>
                            <button 
                              className="btn-action-small"
                              onClick={() => handleToggleOTP(user.id)}
                            >
                              Toggle OTP
                            </button>
                            <button 
                              className="btn-action-small danger"
                              onClick={() => handleDeleteUser(user.id)}
                              disabled={user.id === currentUser.id}
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              
              {!usersLoading && (
                <div className="add-user-section">
                  <h4>Add New User</h4>
                  <form onSubmit={handleAddUser} className="add-user-form">
                    <input type="text" placeholder="Username" value={newUser.username} onChange={e => setNewUser({...newUser, username: e.target.value})} required />
                    <input type="email" placeholder="Email" value={newUser.email} onChange={e => setNewUser({...newUser, email: e.target.value})} required />
                    <input type="password" placeholder="Password" value={newUser.password} onChange={e => setNewUser({...newUser, password: e.target.value})} required />
                    <label>
                      <input type="checkbox" checked={newUser.is_staff} onChange={e => setNewUser({...newUser, is_staff: e.target.checked})} /> Admin
                    </label>
                    <button type="submit" className="btn-action-small">Add User</button>
                  </form>
                </div>
              )}
            </div>
          )}

          <div className="actions-card">
            <h3>Available Actions</h3>
            <div className="action-buttons">
              <button onClick={() => navigate('/audit-logs')} className="btn-action">
                📋 View Audit Logs
              </button>
              <button onClick={fetchProtectedData} className="btn-action">
                🔄 Refresh Data
              </button>
            </div>
          </div>

          <div className="info-grid">
            <div className="info-card">
              <h3>Security Settings</h3>
              
              <div className="change-password-section mt-4">
                <h4>Change Password</h4>
                <form onSubmit={handleChangePassword} className="change-password-form">
                  <input type="password" placeholder="Old Password" value={pwForm.old} onChange={e => setPwForm({...pwForm, old: e.target.value})} required />
                  <input type="password" placeholder="New Password" value={pwForm.new} onChange={e => setPwForm({...pwForm, new: e.target.value})} required />
                  <input type="password" placeholder="Confirm New Password" value={pwForm.confirm} onChange={e => setPwForm({...pwForm, confirm: e.target.value})} required />
                  <button type="submit" className="btn-action-small">Change Password</button>
                </form>
              </div>

              <div className="settings-section">
                <h4>Account Capabilities</h4>
                <div className="capability-toggles">
                  <button onClick={handleToggleMyOTP} className="btn-action-small">Toggle My OTP</button>
                </div>
              </div>
            </div>

            <div className="info-card">
              <h3>About This Platform</h3>
              <p>
                This is a component-based authentication platform demonstrating multiple 
                authentication mechanisms used in modern banking systems:
              </p>
              <ul>
                <li>✅ Username/Password Authentication</li>
                <li>✅ One-Time Password (OTP) Verification</li>
                <li>✅ Single Sign-On (SSO) Integration</li>
                <li>✅ JWT Token Management</li>
                <li>✅ Session Tracking</li>
                <li>✅ Audit Logging</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Dashboard;
