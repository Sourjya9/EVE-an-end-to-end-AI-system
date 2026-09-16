'use client';

import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import CitationBadge from './citation-badge';
import { fetchConversation, streamChat } from '@/lib/api';
import { Message, Citation } from '@/lib/types';

export default function ChatInterface() {
  const searchParams = useSearchParams();
  const activeId = searchParams.get('id');

  const [conversationId, setConversationId] = useState<string | null>(activeId);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (activeId) {
      setConversationId(activeId);
      loadConversation(activeId);
    } else {
      setConversationId(null);
      setMessages([]);
    }
  }, [activeId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const loadConversation = async (id: string) => {
    try { setMessages((await fetchConversation(id)).messages); } catch {}
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isStreaming) return;

    const text = input.trim();
    setInput('');
    setError(null);

    const userMsg: Message = {
      id: String(Date.now()), conversation_id: conversationId || '',
      role: 'user', content: text, created_at: new Date().toISOString(),
    };
    const asstMsg: Message = {
      id: String(Date.now() + 1), conversation_id: conversationId || '',
      role: 'assistant', content: '', citations: null, created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg, asstMsg]);
    setIsStreaming(true);

    let accumulated = '';
    let currentCitations: Citation[] = [];

    await streamChat(text, conversationId,
      (chunk) => {
        if (chunk.conversation_id && !conversationId) setConversationId(chunk.conversation_id);
        if (chunk.citations) currentCitations = chunk.citations;
        if (chunk.delta) accumulated += chunk.delta;

        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last?.role === 'assistant') {
            last.content = accumulated;
            last.citations = currentCitations;
          }
          return updated;
        });
        if (chunk.done) setIsStreaming(false);
      },
      (err) => { setError(err.message); setIsStreaming(false); }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', maxWidth: 760, margin: '0 auto', width: '100%', padding: '0 1rem' }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', paddingTop: '2rem', paddingBottom: '1rem' }}>
        {messages.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60%', gap: '0.75rem', color: 'var(--text-muted)' }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'var(--bg-secondary)', border: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 20, color: 'var(--text-secondary)' }}>E</div>
            <span style={{ fontSize: '0.9rem' }}>How can I help you today?</span>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {messages.map(m => (
              <div key={m.id} style={{
                display: 'flex',
                flexDirection: m.role === 'user' ? 'row-reverse' : 'row',
                alignItems: 'flex-start',
                gap: '0.75rem',
              }}>
                {/* Avatar */}
                <div style={{
                  width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                  background: m.role === 'user' ? 'var(--bg-hover)' : 'var(--bg-secondary)',
                  border: '1px solid var(--border-light)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.7rem', fontWeight: 700,
                  color: 'var(--text-secondary)',
                }}>
                  {m.role === 'user' ? 'U' : 'E'}
                </div>

                {/* Bubble */}
                <div style={{
                  maxWidth: '80%',
                  padding: '0.65rem 0.9rem',
                  borderRadius: 12,
                  fontSize: '0.9rem',
                  lineHeight: 1.65,
                  background: m.role === 'user' ? 'var(--bg-tertiary)' : 'transparent',
                  border: m.role === 'user' ? '1px solid var(--border)' : 'none',
                  color: 'var(--text-primary)',
                }}>
                  {m.content ? (
                    <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
                  ) : (
                    isStreaming && m.role === 'assistant' ? (
                      <span style={{ display: 'inline-flex', gap: 4, alignItems: 'center' }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1s infinite' }} />
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1s 0.2s infinite' }} />
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1s 0.4s infinite' }} />
                      </span>
                    ) : null
                  )}
                  {m.citations && m.citations.length > 0 && <CitationBadge citations={m.citations} />}
                </div>
              </div>
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '0.5rem 0.75rem', borderRadius: 8, background: 'var(--bg-secondary)', border: '1px solid #3a1a1a', color: '#f87171', fontSize: '0.8rem', marginBottom: '0.5rem' }}>
          {error}
        </div>
      )}

      {/* Input */}
      <div style={{ paddingBottom: '1.25rem', paddingTop: '0.5rem' }}>
        <div style={{
          display: 'flex', alignItems: 'flex-end', gap: '0.5rem',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-light)',
          borderRadius: 12, padding: '0.6rem 0.75rem',
        }}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message Eve..."
            rows={1}
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: 'var(--text-primary)', fontSize: '0.9rem', lineHeight: 1.5,
              resize: 'none', maxHeight: '160px', overflowY: 'auto',
              fontFamily: 'inherit',
            }}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isStreaming}
            style={{
              padding: '0.4rem 0.9rem',
              borderRadius: 8,
              border: 'none',
              background: input.trim() && !isStreaming ? 'var(--text-primary)' : 'var(--bg-hover)',
              color: input.trim() && !isStreaming ? 'var(--bg-primary)' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: input.trim() && !isStreaming ? 'pointer' : 'not-allowed',
              transition: 'all 0.15s',
              flexShrink: 0,
            }}
          >
            Send
          </button>
        </div>
        <div style={{ textAlign: 'center', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
          Enter to send · Shift+Enter for newline
        </div>
      </div>
    </div>
  );
}
