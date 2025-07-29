export interface DrugResponse {
  response: string;
  safety_warning: boolean;
  confidence: 'High' | 'Medium' | 'Low';
  sources: DrugSource[];
  disclaimer: string;
  query: string;
  multi_drug_count?: number;
  error?: string;
}

export interface DrugSource {
  drug: string;
  section: string;
  url?: string;
  last_updated?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: DrugSource[];
  confidence?: string;
  safety_warning?: boolean;
  disclaimer?: string;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  created_at: Date;
  updated_at: Date;
}

export interface DrugOverview {
  drug_name: string;
  found: boolean;
  generic_name?: string;
  brand_names?: string[];
  sections?: Record<string, string>;
  source_url?: string;
  last_updated?: string;
  disclaimer?: string;
  message?: string;
}