import './globals.css';
import { ReactNode } from 'react';
import Sidebar from '@/components/sidebar';

export const metadata = {
  title: 'Eve',
  description: 'AI assistant with RAG, LangGraph, and Groq',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg-primary)' }}>
        <Sidebar />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, background: 'var(--bg-primary)' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
