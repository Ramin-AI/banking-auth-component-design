// page to select how to login

import React from 'react';
import { useNavigate } from 'react-router-dom';
import HackerBackground from './HackerBackground';
import PageTransition from '../common/PageTransition';
import './Auth.css';

const AuthMethodSelector = () => {
  const navigate = useNavigate();

  return (
    <HackerBackground>
      <PageTransition>
        <div className="signin signin--wide">
          <div className="content">

            {/* title */}
            <h2 className="selector-title">Authentication</h2>

            {/* login options */}
            <div className="auth-methods">
              <div
                className="auth-method-card"
                id="btn-password-login"
                onClick={() => navigate('/auth/password')}
              >
                <span className="method-icon">🔐</span>
                <h3>Password Login</h3>
                <p>Traditional username and password authentication</p>
              </div>

              <div
                className="auth-method-card"
                id="btn-sso-login"
                onClick={() => navigate('/auth/sso')}
              >
                <span className="method-icon">🌐</span>
                <h3>SSO Login</h3>
                <p>Single Sign-On authentication (Simulated)</p>
              </div>
            </div>

            <div className="selector-bottom">
              {/* divider label */}
              <div className="divider-with-badge">
                <span className="divider-badge">Demo Credentials</span>
              </div>

              {/* hardcoded users for testing */}
              <div className="cred-grid">
                <div className="cred-row cred-row--header">
                  <span>Username</span>
                  <span>Password</span>
                  <span>Access Type</span>
                </div>

                <div className="cred-row">
                  <span className="cred-user">ramin_joon</span>
                  <span className="cred-pass">Password123!</span>
                  <span className="cred-tag cred-tag--standard">Standard</span>
                </div>

                <div className="cred-row">
                  <span className="cred-user">parsa_joon</span>
                  <span className="cred-pass">Password123!</span>
                  <span className="cred-tag cred-tag--otp">OTP Enabled</span>
                </div>

                <div className="cred-row">
                  <span className="cred-user">admin_user</span>
                  <span className="cred-pass">Admin123!</span>
                  <span className="cred-tag cred-tag--admin">Admin</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </PageTransition>
    </HackerBackground>
  );
};

export default AuthMethodSelector;
