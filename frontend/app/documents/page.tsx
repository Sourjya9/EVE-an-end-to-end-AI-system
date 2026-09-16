'use client';

import DocumentUploader from '@/components/document-uploader';

export default function DocumentsPage() {
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '2.5rem 2rem' }}>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
          Documents
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
          Upload documents to enable retrieval-augmented generation. Eve will chunk, embed, and index them using Jina AI + pgvector.
        </p>
        <DocumentUploader />
      </div>
    </div>
  );
}
