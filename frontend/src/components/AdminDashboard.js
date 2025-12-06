import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';
import { adminAPI } from '../services/api';
import { FaUsers, FaChartLine, FaSearch, FaEye, FaDownload, FaSync } from 'react-icons/fa';

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersData, statsData, logsData] = await Promise.all([
        adminAPI.getAllUsers(),
        adminAPI.getStats(),
        adminAPI.getAllLogs(50)
      ]);

      setUsers(usersData.users || []);
      setStats(statsData);
      setLogs(logsData.activity || []);
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewUserLogs = async (userId) => {
    try {
      const userLogs = await adminAPI.getUserLogs(userId);
      setSelectedUser(userLogs);
      setActiveTab('user-detail');
    } catch (error) {
      console.error('Error fetching user logs:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      const results = await adminAPI.searchLogs(searchQuery);
      setSearchResults(results.results || []);
      // ✅ Stay on the "search" tab, just show results below
      // setActiveTab('search-results');  // REMOVE this line
    } catch (error) {
      console.error('Error searching logs:', error);
      // (Optional) you can set some error state here to show a message in the UI
    }
  };

  const handleExportUser = async (userId) => {
    try {
      await adminAPI.exportUserLogs(userId);
      alert(`User data exported successfully!`);
    } catch (error) {
      console.error('Error exporting user data:', error);
      alert('Export failed');
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>🔐 Admin Dashboard</h1>
        <p className="admin-warning">Secret monitoring - Users cannot see this</p>
        <button onClick={loadData} className="refresh-btn" disabled={loading}>
          <FaSync className={loading ? 'spinning' : ''} /> Refresh
        </button>
      </div>

      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FaChartLine /> Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <FaUsers /> All Users
        </button>
        <button
          className={`tab-btn ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          <FaEye /> All Logs
        </button>
        <button
          className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <FaSearch /> Search
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <h2>System Overview</h2>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon users">
                  <FaUsers />
                </div>
                <div className="stat-info">
                  <div className="stat-value">{stats?.total_registered_users || 0}</div>
                  <div className="stat-label">Registered Users</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon active">
                  <FaChartLine />
                </div>
                <div className="stat-info">
                  <div className="stat-value">{stats?.total_active_chatters || 0}</div>
                  <div className="stat-label">Active Chatters</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon logs">
                  <FaEye />
                </div>
                <div className="stat-info">
                  <div className="stat-value">{logs.length}</div>
                  <div className="stat-label">Recent Activities</div>
                </div>
              </div>
            </div>

            {stats?.user_statistics && stats.user_statistics.length > 0 && (
              <div className="user-activity-summary">
                <h3>User Activity Summary</h3>
                <div className="activity-list">
                  {stats.user_statistics.map((userStat, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-header">
                        <strong>{userStat.user_id}</strong>
                        <button
                          onClick={() => handleViewUserLogs(userStat.user_id)}
                          className="view-detail-btn"
                        >
                          <FaEye /> View Details
                        </button>
                      </div>
                      <div className="activity-stats">
                        <span>Messages: {userStat.total_messages}</span>
                        <span>Avg Response: {userStat.avg_response_time?.toFixed(0)}ms</span>
                        <span>Last Active: {userStat.last_activity ? new Date(userStat.last_activity).toLocaleString() : 'Never'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'search' && (
          <div className="search-section">
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                placeholder="Search in all logs (messages, summaries, etc.)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit">Search</button>
            </form>

            {/* ✅ Only depend on searchResults.length */}
            {searchResults.length > 0 && (
              <div className="search-results">
                <h3>Search Results ({searchResults.length})</h3>
                <ul>
                  {searchResults.map((log) => (
                    <li key={log.id}>
                      <div><strong>User:</strong> {log.user_email}</div>
                      <div><strong>Message:</strong> {log.user_message}</div>
                      <div><strong>Response:</strong> {log.assistant_response}</div>
                      <div><strong>Timestamp:</strong> {new Date(log.timestamp).toLocaleString()}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Optional: show a "no results" message */}
            {searchResults.length === 0 && searchQuery.trim() && (
              <p>No results found for “{searchQuery}”.</p>
            )}
          </div>
        )}


        {activeTab === 'logs' && (
          <div className="logs-section">
            <h2>All Activity Logs</h2>
            <div className="logs-list">
              {logs.map((log, index) => (
                <div key={index} className="log-entry">
                  <div className="log-header">
                    <span className={`log-type ${log.event_type}`}>
                      {log.event_type}
                    </span>
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="log-body">
                    <div className="log-user">User: {log.user_id}</div>
                    {log.message && (
                      <div className="log-message">
                        <strong>Message:</strong> {log.message.substring(0, 100)}
                        {log.message.length > 100 && '...'}
                      </div>
                    )}
                    {log.response && (
                      <div className="log-response">
                        <strong>Response:</strong> {log.response.substring(0, 100)}
                        {log.response.length > 100 && '...'}
                      </div>
                    )}
                    {log.personality && (
                      <div className="log-meta">
                        Personality: {log.personality} | Provider: {log.provider}
                        {log.response_time_ms && ` | ${log.response_time_ms.toFixed(0)}ms`}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'search' && (
          <div className="search-section">
            <h2>Search All Conversations</h2>
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search through all user conversations..."
                className="search-input"
              />
              <button type="submit" className="search-btn">
                <FaSearch /> Search
              </button>
            </form>

            {activeTab === 'search-results' && searchResults.length > 0 && (
              <div className="search-results">
                <h3>Search Results ({searchResults.length})</h3>
                <div className="results-list">
                  {searchResults.map((result, index) => (
                    <div key={index} className="result-item">
                      <div className="result-header">
                        <span className="result-user">{result.user_id}</span>
                        <span className="result-time">
                          {new Date(result.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="result-content">
                        {result.message || result.response}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'user-detail' && selectedUser && (
          <div className="user-detail-section">
            <button onClick={() => setActiveTab('overview')} className="back-btn">
              ← Back
            </button>

            <h2>User Details: {selectedUser.user_id}</h2>

            <div className="user-stats-grid">
              <div className="stat-box">
                <div className="stat-label">Total Messages</div>
                <div className="stat-value">{selectedUser.statistics.total_messages}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Total Responses</div>
                <div className="stat-value">{selectedUser.statistics.total_responses}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Avg Message Length</div>
                <div className="stat-value">
                  {selectedUser.statistics.avg_message_length?.toFixed(0)} chars
                </div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Avg Response Time</div>
                <div className="stat-value">
                  {selectedUser.statistics.avg_response_time?.toFixed(0)}ms
                </div>
              </div>
            </div>

            <div className="chat-history">
              <h3>Complete Chat History ({selectedUser.message_count} messages)</h3>
              <div className="conversation-log">
                {selectedUser.chat_history.map((msg, index) => (
                  <div key={index} className={`conv-message ${msg.role}`}>
                    <div className="conv-role">{msg.role.toUpperCase()}</div>
                    <div className="conv-content">{msg.content}</div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => handleExportUser(selectedUser.user_id)}
              className="export-full-btn"
            >
              <FaDownload /> Export Complete Data
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
