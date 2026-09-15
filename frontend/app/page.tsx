import Link from 'next/link';
import { MessageSquare, FileText, Cpu, Database, Shield, Zap, ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto flex flex-col justify-center">
      <div className="text-center space-y-4 mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Production-Style AI Assistant
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-6xl">
          Meet <span className="text-emerald-400">Eve</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          An end-to-end AI assistant featuring LangGraph reasoning, Groq ultra-low latency inference,
          Jina AI embeddings, and PostgreSQL pgvector semantic retrieval.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-all shadow-lg shadow-emerald-600/20"
          >
            <MessageSquare className="w-5 h-5" />
            Start Chatting
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/documents"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium transition-all"
          >
            <FileText className="w-5 h-5" />
            Ingest Documents
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 transition-all">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-4">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">LangGraph Agent</h3>
          <p className="text-sm text-slate-400">
            Stateful graph orchestration with intent classification, conditional routing, and grounded generation.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 transition-all">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 mb-4">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">pgvector RAG</h3>
          <p className="text-sm text-slate-400">
            Clean chunking, Jina v3 dense embeddings, and cosine similarity retrieval directly in PostgreSQL.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 transition-all">
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 mb-4">
            <Zap className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Groq Streaming</h3>
          <p className="text-sm text-slate-400">
            Lightning-fast token streaming over SSE with source citations and responsive Markdown rendering.
          </p>
        </div>
      </div>
    </div>
  );
}
