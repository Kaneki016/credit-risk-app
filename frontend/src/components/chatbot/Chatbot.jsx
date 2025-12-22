import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ENDPOINTS } from '../../utils/api'

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
    // Use requestAnimationFrame to ensure DOM is updated before scrolling
    // This prevents interference with text selection
    requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Ensure text selection is always enabled after any state update
  useEffect(() => {
    if (isOpen) {
      // Force enable text selection on all message elements
      const enableTextSelection = () => {
        const messageElements = document.querySelectorAll('.chat-message, .message-content, .message-text')
        messageElements.forEach((el) => {
          if (el instanceof HTMLElement) {
            el.style.userSelect = 'text'
            el.style.webkitUserSelect = 'text'
            el.style.mozUserSelect = 'text'
            el.style.msUserSelect = 'text'
          }
        })
      }
      
      // Run immediately and after a short delay to catch any delayed renders
      enableTextSelection()
      const timeout = setTimeout(enableTextSelection, 100)
      return () => clearTimeout(timeout)
    }
  }, [messages, isOpen, loading])

  // Quick action buttons
  const quickActions = [
    { label: '📊 Database Stats', query: 'show database statistics' },
    { label: '🔍 Recent Predictions', query: 'show recent predictions' },
    { label: '📈 Model Performance', query: 'show model performance' },
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

    // Add user message immediately
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Get current messages (before adding user message) for history
      const currentMessages = messages
        .filter(msg => msg.type === 'user' || msg.type === 'bot')
        .slice(-10) // Keep last 10 messages for context
        .map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.text
        }))

      // Call chatbot API
      const response = await fetch(ENDPOINTS.CHATBOT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: messageText,
          history: currentMessages,
          context: null
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()

      // Handle error response from API
      if (data.error) {
        const errorMessage = {
          type: 'bot',
          text: data.response || `Error: ${data.error}. ${data.error === 'no_api_key' ? 'Please configure an AI API key in the environment variables.' : 'Please try again later.'}`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
        return
      }

      // Clean up response text (remove any XML-like tags or formatting artifacts)
      let responseText = data.response || 'I received your message but could not generate a response.'
      
      // Remove common formatting artifacts from AI responses
      responseText = responseText
        .replace(/<s>/g, '')  // Remove start tags
        .replace(/<\/s>/g, '') // Remove end tags
        .replace(/^\s+|\s+$/g, '') // Trim whitespace
        .replace(/\n{3,}/g, '\n\n') // Normalize multiple newlines

      const botMessage = {
        type: 'bot',
        text: responseText,
        data: data.data,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Chatbot error:', error)
      const errorMessage = {
        type: 'bot',
        text: `Sorry, I encountered an error: ${error.message || 'Unknown error'}. Please make sure the backend is running and try again.`,
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
            style={{ 
              userSelect: 'text',
              WebkitUserSelect: 'text',
              MozUserSelect: 'text',
              msUserSelect: 'text',
              touchAction: 'pan-y'
            }}
            // Prevent drag from interfering with text selection
            drag={false}
            dragConstraints={false}
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
                  style={{ 
                    userSelect: 'text',
                    WebkitUserSelect: 'text',
                    MozUserSelect: 'text',
                    msUserSelect: 'text',
                    // Prevent Framer Motion from interfering with text selection
                    touchAction: 'pan-y'
                  }}
                  // Prevent drag gestures from interfering with text selection
                  drag={false}
                  dragConstraints={false}
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
                  style={{ 
                    userSelect: 'text',
                    WebkitUserSelect: 'text',
                    MozUserSelect: 'text',
                    msUserSelect: 'text',
                    touchAction: 'pan-y'
                  }}
                  drag={false}
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
