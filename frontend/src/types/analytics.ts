export type CrimeHotspot = {
  id: string;
  latitude: number;
  longitude: number;
  cluster_id: number | null;
  risk_score: number | null;
  crime_density: number | null;
  radius_meters: number | null;
};

export type ForecastRequest = {
  forecast_type: string;
  district?: string | null;
  crime_type_id?: string | null;
  days_ahead: number;
};

export type ForecastDataPoint = {
  date: string;
  predicted_value: number;
  lower_bound: number | null;
  upper_bound: number | null;
};

export type ForecastResponse = {
  forecast_data: ForecastDataPoint[];
  model_used: string;
  confidence_level: number;
  features_used: string[] | null;
};

export type TrendParams = {
  district?: string;
  crime_type?: string;
  period?: string;
  date_from?: string;
  date_to?: string;
};

export type HotspotParams = {
  district?: string;
  days?: number;
};

export type SociologicalParams = {
  district?: string;
  year?: number;
};

export type StatisticsParams = {
  district?: string;
  date_from?: string;
  date_to?: string;
};

export type SimilarCaseRequest = {
  case_id: string;
  top_k: number;
};

export type SimilarCaseResult = {
  case_id: string;
  fir_number: string;
  similarity_score: number;
  crime_type: string;
  incident_date: string;
  matched_features: Record<string, unknown> | null;
};
