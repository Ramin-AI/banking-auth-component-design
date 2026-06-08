// api client
// axios instance with interceptors for authentication

import axios from 'axios';
import TokenManager from './tokenManager';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// interceptor to inject the token, had to add isAuthRoute to stop a bug where it kept refreshing during login
api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    const isAuthRoute = config.url?.includes('/auth/password-login') || 
                        config.url?.includes('/auth/sso-direct') ||
                        config.url?.includes('/auth/verify-otp') ||
                        config.url?.includes('/auth/sso-login') ||
                        config.url?.includes('/auth/sso-callback');

    if (token && !isAuthRoute) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    // Do not attempt refresh on auth routes to prevent login failures with orphaned tokens
    const isAuthRoute = originalRequest.url?.includes('/auth/password-login') || 
                        originalRequest.url?.includes('/auth/sso-direct') ||
                        originalRequest.url?.includes('/auth/verify-otp') ||
                        originalRequest.url?.includes('/auth/sso-login') ||
                        originalRequest.url?.includes('/auth/sso-callback');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRoute) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenManager.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          TokenManager.saveTokens(access_token, refreshToken);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        TokenManager.clearTokens();
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
