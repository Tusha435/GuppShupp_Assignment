import React, { useState, useEffect } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import ComparisonView from './components/ComparisonView';
import MemoryPanel from './components/MemoryPanel';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import { authAPI } from './services/api';
import { FaBrain, FaComments, FaCode, FaShieldAlt, FaSignOutAlt, FaUser } from 'react-icons/fa';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeView, setActiveView] = useState('chat');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.user);
      setIsAuthenticated(true);

      // Set default view based on role
      if (response.user.role === 'admin') {
        setActiveView('admin');
      }
    } catch (error) {
      // Token invalid, clear it
      localStorage.removeItem('token');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
    setIsAuthenticated(true);

    // Set default view based on role
    if (userData.role === 'admin') {
      setActiveView('admin');
    } else {
      setActiveView('chat');
    }
  };

  const handleLogout = () => {
    // Securely clear all sensitive data
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.clear();
    setUser(null);
    setIsAuthenticated(false);
    setActiveView('chat');
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <FaBrain className="loading-icon" />
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const isAdmin = user?.role === 'admin';

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <FaBrain className="logo-icon" />
            <h1>Personality AI Chatbot</h1>
          </div>
          <div className="user-info">
            <div className="user-details">
              <FaUser className="user-icon" />
              <div>
                <div className="username">{user?.username}</div>
                <div className={`user-role ${user?.role}`}>
                  {user?.role === 'admin' ? '🔐 Admin' : '👤 User'}
                </div>
              </div>
            </div>
            <button onClick={handleLogout} className="logout-btn">
              <FaSignOutAlt /> Logout
            </button>
          </div>
        </div>

        {!isAdmin && <p className="tagline">Experience AI with memory and multiple personalities</p>}

        <div className="view-toggle">
          {isAdmin && (
            <button
              className={`toggle-btn admin ${activeView === 'admin' ? 'active' : ''}`}
              onClick={() => setActiveView('admin')}
            >
              <FaShieldAlt /> Admin Dashboard
            </button>
          )}
          <button
            className={`toggle-btn ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            <FaComments /> Chat
          </button>
          <button
            className={`toggle-btn ${activeView === 'comparison' ? 'active' : ''}`}
            onClick={() => setActiveView('comparison')}
          >
            <FaCode /> Compare Personalities
          </button>
        </div>
      </header>

      <main className="app-main">
        {activeView === 'admin' && isAdmin ? (
          <AdminDashboard />
        ) : activeView === 'chat' ? (
          <div className="chat-layout">
            <div className="chat-main">
              <ChatInterface />
            </div>
            <div className="memory-sidebar">
              <MemoryPanel />
            </div>
          </div>
        ) : (
          <ComparisonView />
        )}
      </main>
    </div>
  );
}

export default App;
