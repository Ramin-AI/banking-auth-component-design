// main app with routing stuff

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AuthMethodSelector from './components/auth/AuthMethodSelector';
import PasswordLoginForm from './components/auth/PasswordLoginForm';
import OTPVerificationForm from './components/auth/OTPVerificationForm';
import SSOLoginPage from './components/auth/SSOLoginPage';
import Dashboard from './components/dashboard/Dashboard';
import AuditLogViewer from './components/dashboard/AuditLogViewer';
import ThemeToggle from './components/common/ThemeToggle';
import './App.css';
import './light-theme.css';

// this is the main entry point, hope routing works fine
function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <ThemeToggle />
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<AuthMethodSelector />} />
            <Route path="/auth/password" element={<PasswordLoginForm />} />
            <Route path="/auth/otp" element={<OTPVerificationForm />} />
            <Route path="/auth/sso" element={<SSOLoginPage />} />
            <Route path="/auth/sso-callback" element={<SSOLoginPage />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/audit-logs"
              element={
                <ProtectedRoute>
                  <AuditLogViewer />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
