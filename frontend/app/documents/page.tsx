'use client';

import DocumentUploader from '@/components/document-uploader';

export default function DocumentsPage() {
  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Document Knowledge Base</h1>
        <p className="text-slate-400">
          Upload PDF, TXT, or Markdown documents. Eve will chunk, embed, and index them into pgvector for grounded question answering.
        </p>
      </div>
      <DocumentUploader />
    </div>
  );
}
