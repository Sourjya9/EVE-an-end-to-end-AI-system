'use client';

import { useEffect, useState } from 'react';
import { fetchDocuments, uploadDocument, deleteDocument } from '@/lib/api';
import { DocumentItem } from '@/lib/types';

export default function DocumentUploader() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try { setDocuments(await fetchDocuments()); } catch {}
  };

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMsg(null);
    try {
      const res = await uploadDocument(file);
      setMsg({ ok: true, text: `Indexed "${file.name}" — ${res.message}` });
      await load();
    } catch (err: any) {
      setMsg({ ok: false, text: err.message || 'Upload failed.' });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string) => {
    try { await deleteDocument(id); setDocuments(prev => prev.filter(d => d.id !== id)); } catch {}
  };

  const statusColor = (s: string) => {
    if (s === 'indexed') return '#4ade80';
    if (s === 'failed') return '#f87171';
    return '#fbbf24';
  };

  return (
    <div style={{ maxWidth: 680, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Drop zone */}
      <label style={{
        position: 'relative',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        border: '1.5px dashed var(--border-light)',
        borderRadius: 12,
        padding: '2.5rem',
        cursor: uploading ? 'not-allowed' : 'pointer',
        background: 'var(--bg-secondary)',
        transition: 'border-color 0.15s',
        gap: '0.5rem',
      }}>
        <input
          type="file"
          accept=".pdf,.txt,.md,.markdown"
          onChange={handleFile}
          disabled={uploading}
          style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}
        />
        <div style={{ fontSize: '1.5rem', opacity: 0.4 }}>↑</div>
        <div style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
          {uploading ? 'Processing…' : 'Click to upload a document'}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          PDF, TXT, or Markdown · Max 10 MB
        </div>
      </label>

      {/* Notification */}
      {msg && (
        <div style={{
          padding: '0.6rem 0.9rem',
          borderRadius: 8,
          background: 'var(--bg-secondary)',
          border: `1px solid ${msg.ok ? '#1a3a2a' : '#3a1a1a'}`,
          color: msg.ok ? '#4ade80' : '#f87171',
          fontSize: '0.8rem',
        }}>
          {msg.text}
        </div>
      )}

      {/* Document list */}
      {documents.length > 0 && (
        <div style={{ border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
          <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Knowledge base — {documents.length} document{documents.length > 1 ? 's' : ''}
          </div>
          {documents.map((d, i) => (
            <div key={d.id} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '0.7rem 1rem',
              borderBottom: i < documents.length - 1 ? '1px solid var(--border)' : 'none',
              background: 'var(--bg-secondary)',
            }}>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' }}>{d.filename}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2, fontFamily: 'monospace' }}>
                  {(d.file_size_bytes / 1024).toFixed(1)} KB · {d.chunk_count} chunks · {d.file_type.toUpperCase()}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '0.72rem', color: statusColor(d.status), fontWeight: 600, textTransform: 'uppercase' }}>
                  {d.status}
                </span>
                <button
                  onClick={() => handleDelete(d.id)}
                  style={{
                    background: 'transparent', border: 'none',
                    color: 'var(--text-muted)', cursor: 'pointer',
                    fontSize: 16, lineHeight: 1, padding: '2px 6px',
                    borderRadius: 5,
                  }}
                  title="Delete"
                >×</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
