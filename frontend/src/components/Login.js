import React, { useState } from 'react';
import './Login.css';
import { authAPI } from '../services/api';
import { FaUser, FaLock, FaEnvelope, FaBrain } from 'react-icons/fa';

function Login({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // Login - credentials are never logged or exposed
        const response = await authAPI.login(formData.email, formData.password);
        // Clear sensitive data from memory
        const sanitizedUser = { ...response.user };
        delete sanitizedUser.password;
        onLoginSuccess(response.token, sanitizedUser);
      } else {
        // Register - credentials are never logged or exposed
        await authAPI.register(formData.email, formData.password, formData.username);
        // Auto-login after registration
        const response = await authAPI.login(formData.email, formData.password);
        const sanitizedUser = { ...response.user };
        delete sanitizedUser.password;
        onLoginSuccess(response.token, sanitizedUser);
      }
    } catch (err) {
      // Never expose credentials in error messages
      setError(err.error || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({ email: '', password: '', username: '' });
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="bubble bubble-1"></div>
        <div className="bubble bubble-2"></div>
        <div className="bubble bubble-3"></div>
      </div>

      <div className="login-card">
        <div className="login-header">
          <FaBrain className="login-icon" />
          <h1>Personality AI Chatbot</h1>
          <p>{isLogin ? 'Welcome back!' : 'Create your account'}</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          {!isLogin && (
            <div className="form-group">
              <label>
                <FaUser />
                <span>Username</span>
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter your username"
                required={!isLogin}
              />
            </div>
          )}

          <div className="form-group">
            <label>
              <FaEnvelope />
              <span>Email</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label>
              <FaLock />
              <span>Password</span>
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              minLength="8"
            />
            {!isLogin && (
              <small>Minimum 8 characters</small>
            )}
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button onClick={switchMode} className="switch-mode-btn">
              {isLogin ? 'Register' : 'Login'}
            </button>
          </p>
        </div>

        {/* Demo accounts section removed for production security */}
        {process.env.NODE_ENV === 'development' && (
          <div className="demo-accounts">
            <h4>Dev Mode - Demo Accounts:</h4>
            <div className="demo-account">
              <strong>User:</strong> Register a new account
            </div>
            <small style={{ opacity: 0.6, fontSize: '0.75rem' }}>
              Contact admin for admin access
            </small>
          </div>
        )}
      </div>
    </div>
  );
}

export default Login;
