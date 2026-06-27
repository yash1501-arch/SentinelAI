import api from "@/lib/api"

export async function transcribeAudio(audioBlob: Blob, language = "en") {
  const formData = new FormData()
  formData.append("audio", audioBlob, "recording.webm")
  formData.append("language", language)
  const { data } = await api.post("/voice/transcribe", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export async function transcribeBase64(payload: {
  audio_base64: string
  language?: string
}) {
  const { data } = await api.post("/voice/transcribe-base64", payload)
  return data
}
