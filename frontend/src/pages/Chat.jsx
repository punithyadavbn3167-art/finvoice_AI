import { useEffect, useRef, useState } from 'react'
import { apiRequest } from '../services/api.js'

const createWelcomeMessage = () => ({
  id: 'welcome',
  role: 'assistant',
  content:
    "Hey! I'm FinVoice AI, your finance assistant. Ask me about your expenses, revenue, invoices, or financial summary.",
})

export default function Chat() {
  const [messages, setMessages] = useState([createWelcomeMessage()])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage(event) {
    event?.preventDefault()

    const message = input.trim()

    if (!message || loading) return

    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: message,
    }

    setMessages((current) => [...current, userMessage])
    setInput('')
    setError('')
    setLoading(true)

    try {
      const data = await apiRequest('/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      })

      const answer =
        data.response ??
        data.answer ??
        data.message ??
        'I received a response, but it did not contain an answer.'

      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          content:
            typeof answer === 'string'
              ? answer
              : JSON.stringify(answer, null, 2),
        },
      ])
    } catch (error) {
      setError(
        error.message ||
          'Could not connect to FinVoice AI. Check that your backend is running, then try again.',
      )
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function clearChat() {
    if (loading) return

    setMessages([createWelcomeMessage()])
    setError('')
    setInput('')
    inputRef.current?.focus()
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage(event)
    }
  }

  const suggestions = [
    'What are my total expenses?',
    'Show my revenue and net balance',
    'Which invoices are overdue?',
    'How much did I spend on Amazon?',
  ]

  return (
    <section className="chat-page">
      <header className="page-header chat-page-header">
        <div>
          <p className="eyebrow">YOUR AI FINANCE ASSISTANT</p>
          <h1>FinVoice AI</h1>
          <p>Understand your business finances through conversation.</p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={clearChat}
          disabled={loading}
        >
          Clear chat
        </button>
      </header>

      <div className="chat-workspace panel">
        <div className="chat-status">
          <span className="chat-status-dot" />
          <div>
            <strong>FinVoice Assistant</strong>
            <p>Ask questions about your financial data</p>
          </div>
        </div>

        <div
          className="chat-messages"
          aria-live="polite"
          aria-label="Chat messages"
        >
          {messages.map((message) => (
            <div
              className={`chat-message-row ${message.role}`}
              key={message.id}
            >
              <div
                className={`chat-avatar ${message.role}`}
                aria-hidden="true"
              >
                {message.role === 'user' ? 'Y' : 'F'}
              </div>

              <div className={`chat-message ${message.role}`}>
                <span className="chat-sender">
                  {message.role === 'user' ? 'You' : 'FinVoice AI'}
                </span>
                <p>{message.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-message-row assistant">
              <div className="chat-avatar assistant" aria-hidden="true">
                F
              </div>

              <div className="chat-message assistant">
                <span className="chat-sender">FinVoice AI</span>
                <div className="thinking-indicator" role="status">
                  <span />
                  <span />
                  <span />
                  <small>FinVoice is thinking…</small>
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {messages.length === 1 && !loading && (
          <div className="chat-suggestions">
            <p>Try asking</p>
            <div className="suggestion-list">
              {suggestions.map((suggestion) => (
                <button
                  type="button"
                  className="suggestion-chip"
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="chat-error" role="alert">
            <span>{error}</span>
            <button
              type="button"
              onClick={() => {
                setError('')
                inputRef.current?.focus()
              }}
            >
              Dismiss
            </button>
          </div>
        )}

        <form className="chat-input-form" onSubmit={sendMessage}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask FinVoice about your finances..."
            aria-label="Message FinVoice AI"
            rows={1}
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            {loading ? 'Thinking…' : 'Send ↑'}
          </button>
        </form>

        <p className="chat-footnote">
          Enter to send · Shift + Enter for a new line
        </p>
      </div>
    </section>
  )
}
