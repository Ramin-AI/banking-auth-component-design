// simple form for username/password login

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import HackerBackground from './HackerBackground';
import PageTransition from '../common/PageTransition';
import './Auth.css';

const PasswordLoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(username.trim(), password.trim());

      if (result.success) {
        navigate('/dashboard');
      } else if (result.requiresOTP) {
        navigate('/auth/otp', {
          state: {
            userId: result.userId,
            message: result.message,
          },
        });
      } else {
        setError(result.message || 'Login failed');
      }
    } catch (err) {
      setError('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <HackerBackground>
      <PageTransition>
        <div className="signin">
          <div className="content">
            <h2>Sign In</h2>

            {error && <div className="error-message">{error}</div>}

            <form className="form" onSubmit={handleSubmit}>
              <div className="inputBox">
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  disabled={loading}
                />
                <i>Username</i>
              </div>

              <div className="inputBox">
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
                <i>Password</i>
              </div>

              <div className="links">
                <button type="button" onClick={() => navigate('/')}>
                  ← Back
                </button>
                <button type="button" className="link-green" onClick={() => navigate('/auth/sso')}>
                  SSO Login
                </button>
              </div>

              <div className="inputBox">
                <button type="submit" disabled={loading}>
                  {loading ? 'Logging in...' : 'Login'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </PageTransition>
    </HackerBackground>
  );
};

export default PasswordLoginForm;
