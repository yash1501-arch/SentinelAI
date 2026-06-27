export type VizType = "table" | "line" | "bar" | "map" | "gauge" | "network" | "graph";

export type Source = {
  type: string;
  detail: string;
};

export type Visualization = {
  type: VizType;
  title: string;
  data: Record<string, unknown>[];
};

export type ConversationRequest = {
  session_id: string;
  message: string;
  language?: string;
};

export type ConversationResponse = {
  session_id: string;
  reply: string;
  language: string;
  sources: Source[] | null;
  confidence_score: number | null;
  processing_time_ms: number | null;
  reasoning_chain: string[] | null;
  visualizations: Visualization[] | null;
};

export type ConversationHistoryItem = {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  language: string;
  created_at: string;
};

export type VoiceTranscribeResponse = {
  status: string;
  transcript: string;
  language: string;
  confidence: number;
  translation_en: string | null;
  duration_seconds: number;
};
