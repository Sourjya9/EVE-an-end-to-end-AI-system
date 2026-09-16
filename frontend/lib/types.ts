export interface Citation {
  document_id: string;
  filename: string;
  chunk_index: number;
  score: number;
  snippet: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[] | null;
  token_count?: number | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  user_id?: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  status: 'processing' | 'indexed' | 'failed';
  chunk_count: number;
  error_message?: string | null;
  created_at: string;
}

export interface StreamChunk {
  delta: string;
  citations?: Citation[] | null;
  conversation_id?: string | null;
  done: boolean;
}
