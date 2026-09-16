import Link from 'next/link';

export default function HomePage() {
  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      gap: '2rem',
    }}>
      <div style={{ textAlign: 'center', maxWidth: '480px' }}>
        <div style={{
          width: 48, height: 48,
          borderRadius: 12,
          background: 'var(--bg-tertiary)',
          border: '1px solid var(--border-light)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 22, fontWeight: 700,
          color: 'var(--text-primary)',
          margin: '0 auto 1.5rem',
        }}>E</div>

        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: '0 0 0.5rem', color: 'var(--text-primary)' }}>
          Eve
        </h1>
        <p style={{ color: 'var(--text-secondary)', margin: '0 0 2rem', lineHeight: 1.6 }}>
          An AI assistant with document understanding, semantic search, and conversational memory.
        </p>

        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
          <Link href="/chat" style={{
            padding: '0.6rem 1.25rem',
            borderRadius: 8,
            background: 'var(--text-primary)',
            color: 'var(--bg-primary)',
            fontWeight: 600,
            fontSize: '0.875rem',
            textDecoration: 'none',
          }}>
            Start chatting
          </Link>
          <Link href="/documents" style={{
            padding: '0.6rem 1.25rem',
            borderRadius: 8,
            background: 'transparent',
            color: 'var(--text-secondary)',
            border: '1px solid var(--border-light)',
            fontWeight: 500,
            fontSize: '0.875rem',
            textDecoration: 'none',
          }}>
            Manage documents
          </Link>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '0.75rem',
        maxWidth: '640px',
        width: '100%',
      }}>
        {[
          { label: 'LangGraph Agent', desc: 'Routes queries, retrieves context, generates grounded answers.' },
          { label: 'pgvector RAG', desc: 'Chunk, embed, and search documents with cosine similarity.' },
          { label: 'Groq Streaming', desc: 'Low-latency token streaming with source citations.' },
        ].map(f => (
          <div key={f.label} style={{
            padding: '1rem',
            borderRadius: 10,
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border)',
          }}>
            <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
              {f.label}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {f.desc}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
