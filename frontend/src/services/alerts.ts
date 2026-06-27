import api from "@/lib/api";

export type Alert = {
  id: string;
  type: "forecast" | "offender" | "hotspot" | "case" | "network" | "pattern";
  severity: "critical" | "high" | "warning" | "info";
  title: string;
  description: string;
  created_at: string;
  source: string;
  actionable: boolean;
};

export type AlertCounts = {
  critical: number;
  high: number;
  warning: number;
  info: number;
  total: number;
};

export async function getAlerts(limit = 20): Promise<Alert[]> {
  const { data } = await api.get<Alert[]>("/alerts", { params: { limit } });
  return data;
}

export async function getAlertCounts(): Promise<AlertCounts> {
  const { data } = await api.get<AlertCounts>("/alerts/count");
  return data;
}
