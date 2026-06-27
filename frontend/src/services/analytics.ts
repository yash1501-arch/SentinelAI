import api from "@/lib/api"
import type { CrimeHotspot, ForecastResponse } from "@/types"

export async function getTrends(params?: Record<string, unknown>) {
  const { data } = await api.get("/analytics/trends", { params })
  return data
}

export async function getStatistics(params?: Record<string, unknown>) {
  const { data } = await api.get("/analytics/statistics", { params })
  return data
}

export async function getHotspots(params?: { days?: number }) {
  const { data } = await api.get<CrimeHotspot[]>("/analytics/hotspots", { params })
  return data
}

export async function getForecast(payload: {
  forecast_type: string
  days_ahead: number
  district?: string
  crime_type_id?: string
}) {
  const { data } = await api.post<ForecastResponse>("/analytics/forecast", payload)
  return data
}

export async function getSociological(params?: Record<string, unknown>) {
  const { data } = await api.get("/analytics/sociological", { params })
  return data
}

export async function getOffenderProfiles(params?: { limit?: number }) {
  const { data } = await api.get("/analytics/offender-profiles", { params })
  return data
}
