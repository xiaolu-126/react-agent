export interface ChatRequest {
  message: string;
  streamer_name?: string;
  user_preferences?: string;
}

export interface ChatResponse {
  reply: string;
  conversation_id: string;
}

export interface GenerateRequest {
  streamer_name: string;
  tags?: string;
  content?: string;
  preferences?: string;
}

export interface GenerateResponse {
  streamer_name: string;
  recommendation: string;
  sources: string[];
}

export interface ModelInfo {
  name: string;
  display_name: string;
  is_current: boolean;
}

export interface ModelListResponse {
  models: ModelInfo[];
  current: string;
}

export interface SystemPromptInfo {
  name: string;
  description: string;
  category: string;
  is_current: boolean;
}

export interface SystemPromptListResponse {
  prompts: SystemPromptInfo[];
  current: string;
}

export interface SystemPromptContent {
  name: string;
  content: string;
  file_path: string;
}

export interface AgentStatus {
  current_model: string;
  available_models: string[];
  current_system_prompt: string;
  conversation_length: number;
  knowledge_base_count: number;
}

export interface HistoryResponse {
  messages: { role: string; content: string }[];
  total: number;
}

export interface KnowledgeStatus {
  document_count: number;
  collection_name: string;
  persist_directory: string;
  embedding_model: string;
}

export interface KnowledgeSearchResult {
  content: string;
  metadata: Record<string, unknown>;
  score: number | null;
}

export interface KnowledgeSearchResponse {
  results: KnowledgeSearchResult[];
  total: number;
}

export interface CustomPromptInfo {
  name: string;
  description: string;
  category: string;
  input_variables: string[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

export interface Conversation {
  id: string;
  name: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}