'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { MessageSquare, FileText, Plus, Trash2, ShieldCheck, Terminal } from 'lucide-react';
import { fetchConversations, deleteConversation, fetchHealth } from '@/lib/api';
import { Conversation } from '@/lib/types';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [healthStatus, setHealthStatus] = useState<string>('checking...');

  useEffect(() => {
    loadConversations();
    checkBackendHealth();
  }, [pathname]);

  const loadConversations = async () => {
    try {
      const list = await fetchConversations();
      setConversations(list);
    } catch (e) {
      // Backend may be booting
    }
  };

  const checkBackendHealth = async () => {
    try {
      const h = await fetchHealth();
      setHealthStatus(h.status);
    } catch (e) {
      setHealthStatus('offline');
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      router.push('/chat');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-full select-none">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-white text-lg tracking-tight">
          <div className="w-7 h-7 rounded-md bg-emerald-500 flex items-center justify-center text-slate-950 font-black text-sm">
            E
          </div>
          <span>Eve AI</span>
        </Link>
        <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-900 px-2 py-1 rounded border border-slate-800">
          <span className={`w-2 h-2 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
          {healthStatus}
        </div>
      </div>

      <div className="p-3 space-y-2">
        <Link
          href="/chat"
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </Link>

        <nav className="flex flex-col gap-1 pt-2">
          <Link
            href="/chat"
            className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/chat' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Chat
          </Link>
          <Link
            href="/documents"
            className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              pathname === '/documents' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <FileText className="w-4 h-4" />
            Knowledge Base
          </Link>
        </nav>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 py-1">
          Recent Chats
        </div>
        {conversations.length === 0 ? (
          <div className="text-xs text-slate-500 px-3 py-2 italic">No conversations yet</div>
        ) : (
          conversations.map((c) => (
            <div
              key={c.id}
              className="group flex items-center justify-between px-3 py-2 rounded-md text-sm text-slate-300 hover:bg-slate-900 hover:text-white cursor-pointer transition-colors"
              onClick={() => router.push(`/chat?id=${c.id}`)}
            >
              <span className="truncate text-xs">{c.title}</span>
              <button
                onClick={(e) => handleDelete(e, c.id)}
                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity p-1"
                title="Delete conversation"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="p-3 border-t border-slate-800 text-xs text-slate-500 flex items-center justify-between">
        <span>v0.1.0 • Groq + pgvector</span>
      </div>
    </aside>
  );
}
