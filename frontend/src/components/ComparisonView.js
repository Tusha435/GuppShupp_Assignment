import React, { useState } from 'react';
import './ComparisonView.css';
import { chatAPI } from '../services/api';
import { FaRobot, FaPaperPlane } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

const PERSONALITIES = [
  { value: 'calm_mentor', label: '🧘 Calm Mentor', color: '#667eea', description: 'Wise and patient guide' },
  { value: 'witty_friend', label: '😄 Witty Friend', color: '#f093fb', description: 'Playful and humorous' },
  { value: 'therapist', label: '💭 Therapist', color: '#4facfe', description: 'Empathetic and reflective' },
  { value: 'professional', label: '💼 Professional', color: '#43e97b', description: 'Clear and efficient' },
];

const AI_PROVIDERS = [
  { value: 'openai', label: 'OpenAI GPT-4' },
  { value: 'anthropic', label: 'Anthropic Claude' },
];

function ComparisonView({  }) {
  const [inputMessage, setInputMessage] = useState('');
  const [responses, setResponses] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('openai');

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    setIsLoading(true);
    setResponses(null);

    try {
      const result = await chatAPI.comparePersonalities( inputMessage, selectedProvider);
      setResponses(result.responses);
    } catch (error) {
      console.error('Error comparing personalities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="comparison-view">
      <div className="comparison-header">
        <h2>Personality Comparison</h2>
        <p>See how different personalities respond to the same message</p>
      </div>

      <form onSubmit={handleCompare} className="comparison-input-form">
        <div className="input-group">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Enter a message to compare personalities..."
            className="comparison-input"
            disabled={isLoading}
          />
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="provider-select-comparison"
            disabled={isLoading}
          >
            {AI_PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
          <button
            type="submit"
            className="compare-btn"
            disabled={!inputMessage.trim() || isLoading}
          >
            {isLoading ? 'Comparing...' : 'Compare'}
            <FaPaperPlane />
          </button>
        </div>
      </form>

      {isLoading && (
        <div className="loading-comparison">
          <div className="spinner-large"></div>
          <p>Generating responses from all personalities...</p>
        </div>
      )}

      {responses && !isLoading && (
        <div className="comparison-grid">
          {PERSONALITIES.map((personality) => (
            <div
              key={personality.value}
              className="personality-card"
              style={{ borderTopColor: personality.color }}
            >
              <div className="personality-card-header">
                <div className="personality-info">
                  <FaRobot style={{ color: personality.color }} />
                  <div>
                    <h3>{personality.label}</h3>
                    <p className="personality-description">{personality.description}</p>
                  </div>
                </div>
              </div>
              <div className="personality-card-content">
                <div className="response-label">Response:</div>
                <div className="response-text">
                  <ReactMarkdown>
                    {responses[personality.value] || 'No response available'}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!responses && !isLoading && (
        <div className="comparison-placeholder">
          <FaRobot className="placeholder-icon" />
          <h3>Ready to Compare</h3>
          <p>Enter a message above to see how different AI personalities respond</p>
          <div className="example-prompts">
            <h4>Try asking:</h4>
            <ul>
              <li>"I'm feeling stressed about work"</li>
              <li>"Tell me about your approach to problem-solving"</li>
              <li>"I need advice on learning a new skill"</li>
              <li>"What's your take on work-life balance?"</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default ComparisonView;
