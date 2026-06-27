import api from "@/lib/api"
import type { CrimeIncident, TimelineEvent } from "@/types"

export async function listCases(params?: {
  page?: number
  per_page?: number
  status?: string
}) {
  const { data } = await api.get<CrimeIncident[]>("/cases", { params })
  return data
}

export async function getCase(caseId: string) {
  const { data } = await api.get<CrimeIncident>(`/cases/${caseId}`)
  return data
}

export async function getTimeline(caseId: string) {
  const { data } = await api.get<TimelineEvent[]>(`/cases/${caseId}/timeline`)
  return data
}

export async function getSimilar(caseId: string, topK = 10) {
  const { data } = await api.get(`/cases/${caseId}/similar`, {
    params: { top_k: topK },
  })
  return data
}

export async function getEvidence(caseId: string) {
  const { data } = await api.get(`/cases/${caseId}/evidence`)
  return data
}
