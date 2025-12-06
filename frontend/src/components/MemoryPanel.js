import React, { useState, useEffect } from 'react';
import './MemoryPanel.css';
import { chatAPI } from '../services/api';
import { FaBrain, FaHeart, FaLightbulb, FaSync } from 'react-icons/fa';

function MemoryPanel() {
  const [memories, setMemories] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchMemories = async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.getMemory();
      setMemories(response.memories);
    } catch (error) {
      console.error('Error fetching memories:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchMemories, 30000);
    return () => clearInterval(interval);
  }, []);

  const hasMemories = memories && (
    memories.preferences?.length > 0 ||
    memories.facts?.length > 0 ||
    memories.emotional_patterns?.emotional_patterns?.length > 0
  );

  return (
    <div className="memory-panel">
      <div className="memory-header">
        <div className="memory-title">
          <FaBrain className="memory-icon" />
          <h3>Memory Insights</h3>
        </div>
        <button onClick={fetchMemories} className="refresh-btn" disabled={isLoading}>
          <FaSync className={isLoading ? 'spinning' : ''} />
        </button>
      </div>

      <div className="memory-content">
        {isLoading && !memories ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading memories...</p>
          </div>
        ) : !hasMemories ? (
          <div className="empty-state">
            <FaBrain className="empty-icon" />
            <p>No memories yet</p>
            <span className="empty-hint">Start chatting to build your memory profile!</span>
          </div>
        ) : (
          <div className="memory-sections">
            {/* Preferences */}
            {memories.preferences?.length > 0 && (
              <div className="memory-section">
                <div className="section-header">
                  <FaLightbulb className="section-icon preferences" />
                  <h4>Preferences</h4>
                </div>
                <ul className="memory-list">
                  {memories.preferences.map((pref, index) => (
                    <li key={index} className="memory-item preferences">
                      {pref}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Emotional Patterns */}
            {memories.emotional_patterns && (
              <div className="memory-section">
                <div className="section-header">
                  <FaHeart className="section-icon emotions" />
                  <h4>Emotional Profile</h4>
                </div>

                {memories.emotional_patterns.dominant_emotion &&
                 memories.emotional_patterns.dominant_emotion !== 'neutral' && (
                  <div className="emotion-badge">
                    <span className="badge-label">Dominant Emotion:</span>
                    <span className="badge-value">
                      {memories.emotional_patterns.dominant_emotion}
                    </span>
                  </div>
                )}

                {memories.emotional_patterns.communication_style &&
                 memories.emotional_patterns.communication_style !== 'standard' && (
                  <div className="emotion-badge">
                    <span className="badge-label">Style:</span>
                    <span className="badge-value">
                      {memories.emotional_patterns.communication_style}
                    </span>
                  </div>
                )}

                {memories.emotional_patterns.emotional_patterns?.length > 0 && (
                  <ul className="memory-list">
                    {memories.emotional_patterns.emotional_patterns.map((pattern, index) => (
                      <li key={index} className="memory-item emotions">
                        {pattern}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Facts */}
            {memories.facts?.length > 0 && (
              <div className="memory-section">
                <div className="section-header">
                  <FaBrain className="section-icon facts" />
                  <h4>Important Facts</h4>
                </div>
                <ul className="memory-list">
                  {memories.facts.map((fact, index) => (
                    <li key={index} className="memory-item facts">
                      {fact}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MemoryPanel;
