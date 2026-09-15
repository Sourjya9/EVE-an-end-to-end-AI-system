'use client';

import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Send, Bot, User, Sparkles, AlertCircle } from 'lucide-react';
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

  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const loadConversation = async (id: string) => {
    try {
      const detail = await fetchConversation(id);
      setMessages(detail.messages);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userText = input.trim();
    setInput('');
    setError(null);

    // Append user message immediately
    const tempUserMsg: Message = {
      id: String(Date.now()),
      conversation_id: conversationId || '',
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };

    // Placeholder for streaming assistant response
    const tempAsstMsg: Message = {
      id: String(Date.now() + 1),
      conversation_id: conversationId || '',
      role: 'assistant',
      content: '',
      citations: null,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg, tempAsstMsg]);
    setIsStreaming(true);

    let accumulatedContent = '';
    let currentCitations: Citation[] = [];

    await streamChat(
      userText,
      conversationId,
      (chunk) => {
        if (chunk.conversation_id && !conversationId) {
          setConversationId(chunk.conversation_id);
        }
        if (chunk.citations) {
          currentCitations = chunk.citations;
        }
        if (chunk.delta) {
          accumulatedContent += chunk.delta;
        }

        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === 'assistant') {
            last.content = accumulatedContent;
            last.citations = currentCitations;
          }
          return updated;
        });

        if (chunk.done) {
          setIsStreaming(false);
        }
      },
      (err) => {
        setError(err.message);
        setIsStreaming(false);
      }
    );
  };

  return (
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto p-4">
      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold text-slate-300">Start a conversation with Eve</h2>
            <p className="text-sm text-slate-400 max-w-md">
              Ask questions about your uploaded documents, discuss architecture, or test LangGraph reasoning flows.
            </p>
          </div>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 text-sm ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-xl px-4 py-3 ${
                  m.role === 'user'
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-700/20'
                    : 'bg-slate-800/80 border border-slate-700/50 text-slate-200'
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed">
                  {m.content || (isStreaming && m.role === 'assistant' ? (
                    <span className="inline-flex gap-1 items-center text-slate-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse delay-150" />
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse delay-300" />
                    </span>
                  ) : null)}
                </div>

                {m.citations && m.citations.length > 0 && (
                  <CitationBadge citations={m.citations} />
                )}
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error alert */}
      {error && (
        <div className="mb-3 p-3 rounded-lg bg-red-950/60 border border-red-800/50 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Input bar */}
      <form onSubmit={handleSend} className="pt-3">
        <div className="relative flex items-center">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend(e);
              }
            }}
            placeholder="Message Eve... (Shift+Enter for newline)"
            rows={1}
            className="w-full rounded-xl bg-slate-800/90 border border-slate-700/80 pl-4 pr-12 py-3 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-emerald-500 resize-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="absolute right-2 p-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 disabled:opacity-40 disabled:hover:bg-emerald-600 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
