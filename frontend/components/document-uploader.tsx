'use client';

import { useEffect, useState } from 'react';
import { UploadCloud, File, Trash2, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { fetchDocuments, uploadDocument, deleteDocument } from '@/lib/api';
import { DocumentItem } from '@/lib/types';

export default function DocumentUploader() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMsg(null);

    try {
      const res = await uploadDocument(file);
      setStatusMsg({ type: 'success', message: `Indexed "${file.name}": ${res.message}` });
      await loadDocs();
    } catch (err: any) {
      setStatusMsg({ type: 'error', message: err.message || 'Failed to upload document' });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="relative border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 text-center transition-colors bg-slate-900/50">
        <input
          type="file"
          accept=".pdf,.txt,.md,.markdown"
          onChange={handleFileChange}
          disabled={uploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />
        <div className="flex flex-col items-center justify-center space-y-2">
          <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
            <UploadCloud className="w-6 h-6 text-emerald-400" />
          </div>
          <div className="text-sm font-medium text-slate-200">
            {uploading ? 'Processing & Embedding Chunks...' : 'Click or drag documents to upload'}
          </div>
          <p className="text-xs text-slate-400">Supported formats: PDF, TXT, Markdown (Max 10MB)</p>
        </div>
      </div>

      {/* Notification banner */}
      {statusMsg && (
        <div
          className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
            statusMsg.type === 'success'
              ? 'bg-emerald-950/60 border border-emerald-800 text-emerald-300'
              : 'bg-red-950/60 border border-red-800 text-red-300'
          }`}
        >
          {statusMsg.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          )}
          <span>{statusMsg.message}</span>
        </div>
      )}

      {/* Document table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Uploaded Knowledge Assets</h2>
          <button onClick={loadDocs} className="text-slate-400 hover:text-white text-xs flex items-center gap-1">
            <RefreshCw className="w-3 h-3" /> Refresh
          </button>
        </div>

        {documents.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 italic">
            No documents indexed yet. Upload a document to enable RAG.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 flex items-center justify-between text-sm hover:bg-slate-800/40 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400">
                    <File className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-200">{doc.filename}</div>
                    <div className="text-xs text-slate-400 font-mono">
                      {(doc.file_size_bytes / 1024).toFixed(1)} KB • {doc.chunk_count} chunks • {doc.file_type.toUpperCase()}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span
                    className={`px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider ${
                      doc.status === 'indexed'
                        ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50'
                        : doc.status === 'failed'
                        ? 'bg-red-950/70 text-red-400 border border-red-800/50'
                        : 'bg-amber-950/70 text-amber-400 border border-amber-800/50'
                    }`}
                  >
                    {doc.status}
                  </span>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 text-slate-500 hover:text-red-400 rounded-md hover:bg-slate-800 transition-colors"
                    title="Delete Document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
