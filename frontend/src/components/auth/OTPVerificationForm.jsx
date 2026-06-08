// form to verify the otp code

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import HackerBackground from './HackerBackground';
import PageTransition from '../common/PageTransition';
import './Auth.css';

const OTPVerificationForm = () => {
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { verifyOTP } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const userId = location.state?.userId;
  const message = location.state?.message;

  if (!userId) {
    navigate('/auth/password');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await verifyOTP(userId, otpCode);

      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.message || 'OTP verification failed');
      }
    } catch (err) {
      setError('An error occurred during OTP verification');
    } finally {
      setLoading(false);
    }
  };

  return (
    <HackerBackground>
      <PageTransition>
        <div className="signin">
          <div className="content">
            <h2>Verify OTP</h2>

            {message && <div className="info-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}

            <form className="form" onSubmit={handleSubmit}>
              <div className="inputBox">
                <input
                  type="text"
                  id="otp"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  maxLength="6"
                  required
                  disabled={loading}
                  className="otp-input"
                />
                <i>6-Digit Code</i>
              </div>

              <div className="inputBox">
                <button type="submit" disabled={loading || otpCode.length !== 6}>
                  {loading ? 'Verifying...' : 'Verify OTP'}
                </button>
              </div>
            </form>

            <div className="auth-footer">
              <button onClick={() => navigate('/auth/password')} className="btn-link">
                ← Back to login
              </button>
            </div>
          </div>
        </div>
      </PageTransition>
    </HackerBackground>
  );
};

export default OTPVerificationForm;
