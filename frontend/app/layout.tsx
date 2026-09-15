import './globals.css';
import { ReactNode } from 'react';
import Sidebar from '@/components/sidebar';

export const metadata = {
  title: 'Eve - Production AI Assistant',
  description: 'Full-stack AI assistant with LangGraph, Groq, Jina AI, pgvector, and Next.js',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
        <Sidebar />
        <main className="flex-1 flex flex-col h-full min-w-0 bg-slate-900">
          {children}
        </main>
      </body>
    </html>
  );
}
