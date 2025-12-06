import React, { useState } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import ComparisonView from './components/ComparisonView';
import MemoryPanel from './components/MemoryPanel';
import { FaBrain, FaComments, FaCode } from 'react-icons/fa';

function App() {
  const [activeView, setActiveView] = useState('chat'); // 'chat' or 'comparison'
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <FaBrain className="logo-icon" />
            <h1>Personality AI Chatbot</h1>
          </div>
          <p className="tagline">Experience AI with memory and multiple personalities</p>
        </div>
        <div className="view-toggle">
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
        {activeView === 'chat' ? (
          <div className="chat-layout">
            <div className="chat-main">
              <ChatInterface userId={userId} />
            </div>
            <div className="memory-sidebar">
              <MemoryPanel userId={userId} />
            </div>
          </div>
        ) : (
          <ComparisonView userId={userId} />
        )}
      </main>

      <footer className="app-footer">
        <p>Built with LangChain, OpenAI, Anthropic, Flask & React</p>
      </footer>
    </div>
  );
}

export default App;
