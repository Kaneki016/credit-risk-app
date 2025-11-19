import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: 'Hi! I\'m your Credit Risk Assistant. 🤖\n\nI can help you with:\n• 📊 Database statistics\n• 🔍 Prediction history\n• 📈 Model performance\n• ⚙️ System status\n• ❓ How to use features\n\nNote: I query your database directly - no AI API needed!\n\nWhat would you like to know?',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Quick action buttons
  const quickActions = [
    { label: '📊 Database Stats', query: 'show database statistics' },
    { label: '🔍 Recent Predictions', query: 'show recent predictions' },
    { label: '📈 Model Performance', query: 'show model performance' },
    { label: '🔔 API Usage', query: 'show api usage' },
    { label: '❓ Help', query: 'how do I use this system?' }
  ]

  const handleQuickAction = (query) => {
    handleSend(query)
  }

  const handleSend = async (messageText = input) => {
    if (!messageText.trim()) return

    const userMessage = {
      type: 'user',
      text: messageText,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Call chatbot API
      const response = await fetch('http://localhost:8000/chatbot/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: messageText })
      })

      const data = await response.json()

      const botMessage = {
        type: 'bot',
        text: data.response,
        data: data.data,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage = {
        type: 'bot',
        text: 'Sorry, I encountered an error. Please make sure the backend is running.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatData = (data) => {
    if (!data) return null

    return (
      <div className="chat-data">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="data-row">
            <span className="data-key">{key}:</span>
            <span className="data-value">
              {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
            </span>
          </div>
        ))}
      </div>
    )
  }

  return (
    <>
      {/* Chat Button */}
      <motion.button
        className={`chat-button ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        {isOpen ? '✕' : '💬'}
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="chat-window"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            {/* Header */}
            <div className="chat-header">
              <div className="chat-header-content">
                <div className="chat-avatar">🤖</div>
                <div className="chat-title">
                  <h3>Credit Risk Assistant</h3>
                  <p>Ask me anything about your data</p>
                </div>
              </div>
              <button className="chat-close" onClick={() => setIsOpen(false)}>
                ✕
              </button>
            </div>

            {/* Messages */}
            <div className="chat-messages">
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  className={`chat-message ${message.type}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="message-content">
                    <div className="message-text">{message.text}</div>
                    {message.data && formatData(message.data)}
                    <div className="message-time">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </motion.div>
              ))}

              {loading && (
                <motion.div
                  className="chat-message bot"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            {messages.length <= 2 && (
              <div className="chat-quick-actions">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    className="quick-action-btn"
                    onClick={() => handleQuickAction(action.query)}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="chat-input-container">
              <textarea
                className="chat-input"
                placeholder="Ask me anything..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                rows="1"
              />
              <button
                className="chat-send"
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
              >
                {loading ? '⏳' : '➤'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
