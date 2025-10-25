import { useState } from 'react';

function ChatMessage({ entry }) {
  const isUser = entry.role === 'user';
  return (
    <article className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>{isUser ? 'You' : 'WK'}</div>
      <div className="chat-copy">
        <header className="chat-meta">
          <span className="chat-role">{isUser ? 'Learner' : entry.flair || 'Navigator'}</span>
          {entry.timestamp && <span className="chip subtle">{entry.timestamp}</span>}
        </header>
        <p className="chat-text">{entry.content}</p>
        {entry.tags?.length ? (
          <ul className="tag-cloud">
            {entry.tags.map((tag) => (
              <li key={tag}>{tag}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </article>
  );
}

export function ChatPanel({ messages, onSend }) {
  const [value, setValue] = useState('');
  const [attachments, setAttachments] = useState([]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed) {
      return;
    }
    onSend(trimmed, attachments);
    setValue('');
    setAttachments([]);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleFileInput = (event) => {
    const files = Array.from(event.target.files || []);
    if (!files.length) {
      return;
    }
    setAttachments((current) => [...current, ...files.map((file) => file.name)]);
  };

  return (
    <section className="panel chat-panel">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Today&apos;s companion</p>
          <h2>Wonder Knowledge navigator</h2>
        </div>
      </header>
      <div className="chat-stream" role="log" aria-live="polite">
        {messages.map((entry, index) => (
          <ChatMessage key={`${entry.role}-${index}`} entry={entry} />
        ))}
      </div>
      <footer className="composer">
        <textarea
          placeholder="Ask about your graph, sessions, or share ideas…"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <label className="attachment-box">
          Add references (optional)
          <input type="file" multiple onChange={handleFileInput} />
        </label>
        {attachments.length ? (
          <ul className="attachment-list">
            {attachments.map((file) => (
              <li key={file} className="chip">
                {file}
              </li>
            ))}
          </ul>
        ) : null}
        <div className="composer-actions">
          <p className="helper">Press Enter to send, Shift+Enter for a new line.</p>
          <button type="button" className="button primary" onClick={handleSend}>
            Send
          </button>
        </div>
      </footer>
    </section>
  );
}
