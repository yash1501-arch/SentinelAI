import api from "@/lib/api"

export async function converse(payload: {
  session_id: string
  message: string
  language?: string
}) {
  const { data } = await api.post("/chat/converse", payload)
  return data
}

export async function getHistory(sessionId: string) {
  const { data } = await api.get(`/chat/history/${sessionId}`)
  return data
}

export async function deleteHistory(sessionId: string) {
  const { data } = await api.delete(`/chat/history/${sessionId}`)
  return data
}
