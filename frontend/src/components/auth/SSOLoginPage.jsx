// single sign on login page

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import HackerBackground from './HackerBackground';
import PageTransition from '../common/PageTransition';
import './Auth.css';

const SSOLoginPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchParams] = useSearchParams();
  
  const { ssoLogin, ssoDirectLogin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Check if this is a callback from SSO provider
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (code && state) {
      handleSSOCallback(code, state);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const handleSSOCallback = async (code, state) => {
    setLoading(true);
    setError('');

    try {
      const result = await ssoLogin(code, state);

      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.message || 'SSO login failed');
      }
    } catch (err) {
      setError('An error occurred during SSO login');
    } finally {
      setLoading(false);
    }
  };

  const handleDirectSSO = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await ssoDirectLogin();
      
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.message || 'SSO login failed');
      }
    } catch (err) {
      setError('An error occurred during SSO login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <HackerBackground>
      <PageTransition>
        <div className="signin">
          <div className="content">
            <h2>SSO Login</h2>

            {error && <div className="error-message">{error}</div>}

            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Processing SSO authentication...</p>
              </div>
            ) : (
              <>
                <div className="sso-info">
                  <p>Click the button below to authenticate using our simulated SSO provider.</p>
                  <p className="info-text">
                    In a real system, this would redirect to an external identity provider 
                    (e.g., Google, Microsoft, Okta).
                  </p>
                </div>

                <button onClick={handleDirectSSO} className="btn-sso">
                  <span className="sso-icon">🌐</span>
                  Login with SSO
                </button>

                <div className="auth-footer">
                  <button onClick={() => navigate('/')} className="btn-link">
                    ← Back to methods
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </PageTransition>
    </HackerBackground>
  );
};

export default SSOLoginPage;
