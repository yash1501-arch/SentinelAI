import api from "@/lib/api"
import type { NetworkResponse } from "@/types"

export async function analyzeNetwork(payload: {
  person_id?: string | null
  case_id?: string | null
  depth: number
}) {
  const { data } = await api.post<NetworkResponse>("/network/analyze", payload)
  return data
}

export async function getPersonCentrality(personId: string) {
  const { data } = await api.get(`/network/centrality/${personId}`)
  return data
}

export async function getCommunities() {
  const { data } = await api.get("/network/communities")
  return data
}

export async function getConnectionPath(personA: string, personB: string) {
  const { data } = await api.get(`/network/paths/${personA}/${personB}`)
  return data
}

export async function getSuspiciousPatterns() {
  const { data } = await api.get("/network/suspicious-patterns")
  return data
}
