'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { fetchConversations, deleteConversation, fetchHealth } from '@/lib/api';
import { Conversation } from '@/lib/types';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [online, setOnline] = useState(false);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  useEffect(() => {
    loadConversations();
    checkHealth();
  }, [pathname]);

  const loadConversations = async () => {
    try { setConversations(await fetchConversations()); } catch {}
  };

  const checkHealth = async () => {
    try { const h = await fetchHealth(); setOnline(h.status === 'healthy'); } catch { setOnline(false); }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    e.preventDefault();
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (pathname.includes(id)) router.push('/chat');
    } catch {}
  };

  const navItem = (href: string, label: string) => {
    const active = pathname === href || (href === '/chat' && pathname.startsWith('/chat'));
    return (
      <Link href={href} style={{
        display: 'flex', alignItems: 'center', gap: '0.6rem',
        padding: '0.45rem 0.75rem',
        borderRadius: 7,
        fontSize: '0.875rem',
        fontWeight: 500,
        color: active ? 'var(--text-primary)' : 'var(--text-secondary)',
        background: active ? 'var(--bg-hover)' : 'transparent',
        textDecoration: 'none',
        transition: 'all 0.1s',
      }}>
        {label}
      </Link>
    );
  };

  return (
    <aside style={{
      width: 256,
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{
        padding: '1rem 1rem 0.75rem',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', textDecoration: 'none' }}>
          <div style={{
            width: 28, height: 28, borderRadius: 7,
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-light)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 700, fontSize: 13, color: 'var(--text-primary)',
          }}>E</div>
          <span style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)' }}>Eve</span>
        </Link>
        <div style={{
          width: 7, height: 7, borderRadius: '50%',
          background: online ? '#4ade80' : '#555',
          flexShrink: 0,
        }} title={online ? 'Backend online' : 'Backend offline'} />
      </div>

      {/* Nav */}
      <div style={{ padding: '0.6rem 0.6rem 0' }}>
        <Link href="/chat" style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
          padding: '0.5rem',
          borderRadius: 7,
          fontSize: '0.8rem',
          fontWeight: 500,
          color: 'var(--text-secondary)',
          border: '1px solid var(--border-light)',
          background: 'transparent',
          textDecoration: 'none',
          marginBottom: '0.5rem',
          transition: 'all 0.1s',
        }}>
          + New chat
        </Link>
        {navItem('/chat', 'Chat')}
        {navItem('/documents', 'Documents')}
      </div>

      {/* Conversation history */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0.75rem 0.6rem 0' }}>
        {conversations.length > 0 && (
          <>
            <div style={{
              fontSize: '0.7rem',
              fontWeight: 600,
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              padding: '0 0.5rem 0.5rem',
            }}>Recent</div>
            {conversations.map(c => (
              <div
                key={c.id}
                onClick={() => router.push(`/chat?id=${c.id}`)}
                onMouseEnter={() => setHoveredId(c.id)}
                onMouseLeave={() => setHoveredId(null)}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '0.4rem 0.6rem',
                  borderRadius: 7,
                  cursor: 'pointer',
                  background: hoveredId === c.id ? 'var(--bg-hover)' : 'transparent',
                  transition: 'background 0.1s',
                  marginBottom: 2,
                }}
              >
                <span style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  flex: 1,
                }}>{c.title}</span>
                {hoveredId === c.id && (
                  <button
                    onClick={(e) => handleDelete(e, c.id)}
                    style={{
                      marginLeft: 4, padding: '2px 6px',
                      borderRadius: 5, border: 'none',
                      background: 'transparent',
                      color: 'var(--text-muted)',
                      cursor: 'pointer', fontSize: 14, lineHeight: 1,
                    }}
                    title="Delete"
                  >×</button>
                )}
              </div>
            ))}
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '0.75rem 1rem',
        borderTop: '1px solid var(--border)',
        fontSize: '0.7rem',
        color: 'var(--text-muted)',
      }}>
        Eve v0.1.0
      </div>
    </aside>
  );
}
