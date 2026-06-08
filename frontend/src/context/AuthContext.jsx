// auth context
// global authentication state management

import React, { createContext, useState, useEffect } from 'react';
import TokenManager from '../services/tokenManager';
import AuthService from '../services/authService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const user = TokenManager.getUser();
    const token = TokenManager.getAccessToken();
    
    if (user && token) {
      setCurrentUser(user);
      setIsAuthenticated(true);
    }
    
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await AuthService.passwordLogin(username, password);
      
      if (response.requires_otp) {
        return {
          success: false,
          requiresOTP: true,
          userId: response.user_id,
          message: response.message,
        };
      }

      if (response.success) {
        TokenManager.saveTokens(response.access_token, response.refresh_token);
        TokenManager.saveUser(response.user);
        setCurrentUser(response.user);
        setIsAuthenticated(true);
        
        return {
          success: true,
          requiresOTP: false,
        };
      }

      return {
        success: false,
        message: response.message || 'Login failed',
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed',
      };
    }
  };

  const verifyOTP = async (userId, otpCode) => {
    try {
      const response = await AuthService.verifyOTP(userId, otpCode);
      
      if (response.success) {
        TokenManager.saveTokens(response.access_token, response.refresh_token);
        TokenManager.saveUser(response.user);
        setCurrentUser(response.user);
        setIsAuthenticated(true);
        
        return {
          success: true,
        };
      }

      return {
        success: false,
        message: response.message || 'OTP verification failed',
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'OTP verification failed',
      };
    }
  };

  const ssoLogin = async (code, state) => {
    try {
      const response = await AuthService.ssoCallback(code, state);
      
      if (response.success) {
        TokenManager.saveTokens(response.access_token, response.refresh_token);
        TokenManager.saveUser(response.user);
        setCurrentUser(response.user);
        setIsAuthenticated(true);
        
        return {
          success: true,
        };
      }

      return {
        success: false,
        message: response.message || 'SSO login failed',
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'SSO login failed',
      };
    }
  };

  const ssoDirectLogin = async () => {
    try {
      const response = await AuthService.ssoDirectLogin();
      
      if (response.success) {
        TokenManager.saveTokens(response.access_token, response.refresh_token);
        TokenManager.saveUser(response.user);
        setCurrentUser(response.user);
        setIsAuthenticated(true);
        
        return {
          success: true,
        };
      }

      return {
        success: false,
        message: response.message || 'SSO login failed',
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'SSO login failed',
      };
    }
  };

  const logout = async () => {
    try {
      await AuthService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      TokenManager.clearTokens();
      setCurrentUser(null);
      setIsAuthenticated(false);
    }
  };

  const value = {
    currentUser,
    isAuthenticated,
    loading,
    login,
    verifyOTP,
    ssoLogin,
    ssoDirectLogin,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
