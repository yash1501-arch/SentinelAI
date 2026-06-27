export type CrimeType = {
  id: string;
  name: string;
  category: string;
  description: string | null;
  severity_level: number;
};

export type CrimeIncident = {
  id: string;
  fir_id: string;
  crime_type_id: string;
  incident_date: string;
  incident_time: string | null;
  description: string;
  modus_operandi: string | null;
  is_solved: boolean;
  property_value_loss: number;
  injury_count: number;
  fatality_count: number;
  created_at: string;
  crime_type: CrimeType | null;
};

export type Evidence = {
  id: string;
  fir_id: string;
  evidence_type: string;
  name: string;
  description: string | null;
  is_forensically_analyzed: boolean;
  is_admissible: boolean;
};

export type Person = {
  id: string;
  first_name: string;
  middle_name: string | null;
  last_name: string;
  alias: string | null;
  date_of_birth: string | null;
  gender: string | null;
  nationality: string | null;
  occupation: string | null;
  phone: string | null;
  email: string | null;
};

export type FIR = {
  id: string;
  fir_number: string;
  police_station: string;
  district: string;
  state: string;
  registration_date: string;
  act_sections: string | null;
  brief_fact: string;
  io_name: string | null;
  recorded_by: string;
  created_at: string;
};

export type Location = {
  incident_id: string;
  name: string | null;
  location_type: string | null;
  latitude: number;
  longitude: number;
  address: string | null;
  city: string | null;
  district: string | null;
};

export type TimelineEventType =
  | "fir_registered"
  | "incident_reported"
  | "investigation_started"
  | "evidence_collected"
  | "suspect_identified"
  | "arrest_made"
  | "chargesheet_filed"
  | "court_hearing"
  | "conviction"
  | "acquittal"
  | "case_closed"
  | "note_added"
  | "status_change"
  | "other";

export type TimelineEvent = {
  id: string;
  case_id: string;
  event_type: TimelineEventType;
  title: string;
  description: string | null;
  timestamp: string;
  actor: string | null;
  metadata: Record<string, unknown> | null;
};
