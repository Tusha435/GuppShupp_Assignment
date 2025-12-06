import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import { chatAPI } from '../services/api';
import { FaPaperPlane, FaRobot, FaUser, FaTrash } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

const PERSONALITIES = [
  { value: 'calm_mentor', label: '🧘 Calm Mentor', color: '#667eea' },
  { value: 'witty_friend', label: '😄 Witty Friend', color: '#f093fb' },
  { value: 'therapist', label: '💭 Therapist', color: '#4facfe' },
  { value: 'professional', label: '💼 Professional', color: '#43e97b' },
];

const AI_PROVIDERS = [
  { value: 'openai', label: 'OpenAI GPT-4' },
  { value: 'anthropic', label: 'Anthropic Claude' },
];

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedPersonality, setSelectedPersonality] = useState('calm_mentor');
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // Create placeholder for streaming response
    const assistantMessageId = Date.now();
    const assistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      personality: selectedPersonality,
      provider: selectedProvider,
      timestamp: new Date().toISOString(),
      isStreaming: true,
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      await chatAPI.sendMessageStream(
        messageToSend,
        selectedPersonality,
        selectedProvider,
        // onChunk - append to the streaming message
        (chunk) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        // onComplete - mark streaming as done
        (metadata) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, isStreaming: false, ...metadata }
                : msg
            )
          );
          setIsLoading(false);
        },
        // onError - show error
        (error) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: `Sorry, I encountered an error: ${error}`,
                    isError: true,
                    isStreaming: false,
                  }
                : msg
            )
          );
          setIsLoading(false);
        }
      );
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: 'Sorry, I encountered an error. Please try again.',
                isError: true,
                isStreaming: false,
              }
            : msg
        )
      );
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      try {
        await chatAPI.clearHistory();
        setMessages([]);
      } catch (error) {
        console.error('Error clearing chat:', error);
      }
    }
  };

  const getPersonalityColor = () => {
    const personality = PERSONALITIES.find((p) => p.value === selectedPersonality);
    return personality?.color || '#667eea';
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-controls">
          <div className="control-group">
            <label>Personality:</label>
            <select
              value={selectedPersonality}
              onChange={(e) => setSelectedPersonality(e.target.value)}
              className="personality-select"
              style={{ borderColor: getPersonalityColor() }}
            >
              {PERSONALITIES.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
          <div className="control-group">
            <label>AI Provider:</label>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="provider-select"
            >
              {AI_PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
          <button onClick={handleClearChat} className="clear-btn" title="Clear chat">
            <FaTrash />
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <FaRobot className="welcome-icon" />
            <h3>Welcome to Personality AI Chat!</h3>
            <p>Start a conversation and watch how different personalities respond.</p>
            <p className="hint">Try asking about your day, sharing a problem, or just chatting!</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={message.id || index}
            className={`message ${message.role} ${message.isError ? 'error' : ''} ${message.isStreaming ? 'streaming' : ''}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? (
                <FaUser />
              ) : (
                <FaRobot style={{ color: getPersonalityColor() }} />
              )}
            </div>
            <div className="message-content">
              {message.role === 'assistant' && message.personality && (
                <div className="message-meta">
                  <span className="personality-badge" style={{ backgroundColor: getPersonalityColor() }}>
                    {PERSONALITIES.find((p) => p.value === message.personality)?.label}
                  </span>
                  <span className="provider-badge">{message.provider}</span>
                </div>
              )}
              <div className="message-text">
                <ReactMarkdown>{message.content || ' '}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-avatar">
              <FaRobot style={{ color: getPersonalityColor() }} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={!inputMessage.trim() || isLoading}
          style={{ backgroundColor: getPersonalityColor() }}
        >
          <FaPaperPlane />
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;
