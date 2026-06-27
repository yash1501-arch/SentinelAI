export type NetworkQuery = {
  person_id?: string | null;
  case_id?: string | null;
  depth: number;
};

export type NetworkNode = {
  id: string;
  label: string;
  type: string;
  metadata: Record<string, unknown> | null;
};

export type NetworkEdge = {
  source: string;
  target: string;
  relationship: string;
  weight: number | null;
};

export type NetworkResponse = {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  centrality: Record<string, number> | null;
  communities: string[][] | null;
};

export type ExportPDFRequest = {
  session_id: string;
  case_ids?: string[] | null;
  include_charts: boolean;
};

export type AuditLog = {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  description: string | null;
  created_at: string;
};
