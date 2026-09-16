'use client';

import { useState } from 'react';
import { Citation } from '@/lib/types';

export default function CitationBadge({ citations }: { citations: Citation[] }) {
  const [open, setOpen] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div style={{ marginTop: '0.75rem' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          background: 'transparent',
          border: '1px solid var(--border)',
          borderRadius: 6,
          padding: '0.2rem 0.6rem',
          cursor: 'pointer',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
        }}
      >
        <span style={{ opacity: 0.6 }}>⊕</span>
        {citations.length} source{citations.length > 1 ? 's' : ''}
        <span style={{ fontSize: 10, opacity: 0.5 }}>{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {citations.map((c, i) => (
            <div key={i} style={{
              padding: '0.6rem 0.75rem',
              borderRadius: 8,
              background: 'var(--bg-primary)',
              border: '1px solid var(--border)',
              fontSize: '0.75rem',
            }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                marginBottom: '0.3rem',
              }}>
                <span style={{ fontWeight: 600, color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                  {c.filename} · chunk {c.chunk_index}
                </span>
                <span style={{
                  color: 'var(--text-muted)',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border)',
                  borderRadius: 4, padding: '1px 6px',
                  fontSize: '0.7rem',
                }}>
                  {(c.score * 100).toFixed(0)}%
                </span>
              </div>
              <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.5, fontStyle: 'italic' }}>
                "{c.snippet}"
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
