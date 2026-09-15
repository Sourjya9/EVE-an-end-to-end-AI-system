'use client';

import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { Citation } from '@/lib/types';

export default function CitationBadge({ citations }: { citations: Citation[] }) {
  const [expanded, setExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-800/80">
      <button
        onClick={() => setExpanded(!expanded)}
        className="inline-flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
      >
        <FileText className="w-3.5 h-3.5" />
        <span>{citations.length} Grounded Source{citations.length > 1 ? 's' : ''}</span>
        {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      {expanded && (
        <div className="mt-2 space-y-2">
          {citations.map((c, i) => (
            <div
              key={i}
              className="p-2.5 rounded-md bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-1"
            >
              <div className="flex items-center justify-between font-mono text-emerald-400 text-[11px]">
                <span className="truncate font-semibold">{c.filename} (Chunk #{c.chunk_index})</span>
                <span className="bg-emerald-950/60 text-emerald-400 px-1.5 py-0.5 rounded text-[10px] border border-emerald-800/50">
                  Score: {(c.score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-slate-400 leading-relaxed italic">"{c.snippet}"</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
