import { useState, useRef, useEffect } from 'react';
import { Send, Plus, Paperclip, Mic, FileText, X } from 'lucide-react';
import { chatAPI } from './services/api';
import type { Message, Conversation } from './services/api';
import './index.css';

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConv, setCurrentConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const data = await chatAPI.getConversations();
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations', err);
    }
  };

  const selectConversation = async (id: number) => {
    try {
      const data = await chatAPI.getConversation(id);
      setCurrentConv(data);
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to load conversation', err);
    }
  };

  const startNewChat = () => {
    setCurrentConv(null);
    setMessages([]);
    setAttachedFile(null);
  };

  const handleSend = async () => {
    if ((!input.trim() && !attachedFile) || isLoading) return;

    let convId = currentConv?.id;
    let fileId = undefined;

    setIsLoading(true);

    try {
      // Handle file upload first if present
      if (attachedFile) {
        // Add a temporary user message for UX
        const tempMsg: Message = { id: Date.now(), role: 'user', content: `Uploaded file: ${attachedFile.name}` };
        setMessages(prev => [...prev, tempMsg]);
        
        const uploadRes = await chatAPI.uploadDocument(attachedFile, convId);
        convId = uploadRes.conversation_id;
        fileId = uploadRes.document_id;
        setAttachedFile(null);
      }

      if (input.trim()) {
        // Add user message to UI
        const userMsg: Message = { id: Date.now(), role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');

        const res = await chatAPI.sendMessage(input, convId, fileId);
        
        // Add assistant message to UI
        const botMsg: Message = {
          id: Date.now() + 1,
          role: 'assistant',
          content: res.reply,
          sources: res.sources
        };
        setMessages(prev => [...prev, botMsg]);
        
        if (!currentConv) {
          // It's a new conversation, load it
          loadConversations();
          selectConversation(res.conversation_id);
        }
      }
    } catch (err) {
      console.error('Failed to send message', err);
      // Add error message
      setMessages(prev => [...prev, { id: Date.now(), role: 'assistant', content: 'Sorry, I encountered an error processing your request.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <button className="new-chat-btn" onClick={startNewChat}>
          <Plus size={18} />
          New Chat
        </button>
        
        <div className="chat-history">
          {conversations.map(conv => (
            <div 
              key={conv.id} 
              className={`history-item ${currentConv?.id === conv.id ? 'active' : ''}`}
              onClick={() => selectConversation(conv.id)}
            >
              {conv.title}
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        <div className="chat-header">
          {currentConv ? currentConv.title : 'New Conversation'}
        </div>
        
        <div className="messages-container">
          {messages.length === 0 ? (
            <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <h2>Multimodal AI Chatbot</h2>
              <p>Ask a question, upload a document or an image to get started.</p>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className={`message-row ${msg.role}`}>
                <div className="message-bubble">
                  <div className="message-content">{msg.content}</div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="message-sources">
                      <strong>Sources:</strong>
                      {msg.sources.map((src, i) => (
                        <a key={i} href={src.url} target="_blank" rel="noopener noreferrer" className="source-link">
                          {src.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="message-row assistant">
              <div className="message-bubble">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          {attachedFile && (
            <div className="upload-preview">
              <div className="file-badge">
                <FileText size={16} />
                {attachedFile.name}
                <button className="remove-btn" onClick={() => setAttachedFile(null)}>
                  <X size={14} />
                </button>
              </div>
            </div>
          )}
          
          <div className="input-container">
            <button className="action-btn" onClick={() => fileInputRef.current?.click()} title="Attach file">
              <Paperclip size={20} />
            </button>
            <input 
              type="file" 
              className="hidden-input" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,image/*"
            />
            
            <textarea 
              className="chat-input"
              placeholder="Message AI Chatbot..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            
            <button className="action-btn" title="Voice Input">
              <Mic size={20} />
            </button>
            
            <button 
              className="action-btn send-btn" 
              onClick={handleSend}
              disabled={(!input.trim() && !attachedFile) || isLoading}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
