// authentication service
// handles all authentication api calls

import api from './api';

class AuthService {
  static async passwordLogin(username, password) {
    const response = await api.post('/auth/password-login', {
      username,
      password,
    });
    return response.data;
  }

  static async verifyOTP(userId, otpCode) {
    const response = await api.post('/auth/verify-otp', {
      user_id: userId,
      otp_code: otpCode,
    });
    return response.data;
  }

  static async initiateSSO() {
    const response = await api.get('/auth/sso-login');
    return response.data;
  }

  static async ssoCallback(code, state) {
    const response = await api.post('/auth/sso-callback', {
      code,
      state,
    });
    return response.data;
  }

  static async ssoDirectLogin() {
    const response = await api.post('/auth/sso-direct');
    return response.data;
  }

  static async logout() {
    const response = await api.post('/auth/logout');
    return response.data;
  }

  static async getProtectedData() {
    const response = await api.get('/auth/protected');
    return response.data;
  }

  static async getAuditLogs(userId = null) {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/auth/audit-logs', { params });
    return response.data;
  }

  static async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  static async getAllUsers() {
    const response = await api.get('/auth/admin/users');
    return response.data;
  }

  static async toggleUserOTP(userId) {
    const response = await api.put(`/auth/admin/users/${userId}/toggle-otp`);
    return response.data;
  }

  static async deleteUser(userId) {
    const response = await api.delete(`/auth/admin/users/${userId}`);
    return response.data;
  }

  static async createUser(userData) {
    const response = await api.post('/auth/admin/users', userData);
    return response.data;
  }

  static async toggleUserActive(userId) {
    const response = await api.put(`/auth/admin/users/${userId}/toggle-active`);
    return response.data;
  }

  static async resetUserPassword(userId) {
    const response = await api.put(`/auth/admin/users/${userId}/reset-password`);
    return response.data;
  }

  static async changePassword(oldPassword, newPassword) {
    const response = await api.put('/auth/user/change-password', { old_password: oldPassword, new_password: newPassword });
    return response.data;
  }

  static async toggleMyOTP() {
    const response = await api.put('/auth/user/toggle-otp');
    return response.data;
  }
}

export default AuthService;
