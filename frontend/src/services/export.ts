import api from "@/lib/api"

export type ExportFormat = "pdf" | "csv"

export type ExportOptions = {
  session_id: string
  case_ids?: string[]
  include_charts?: boolean
}

export async function exportPDF(options: ExportOptions) {
  const { data } = await api.post("/export/pdf", {
    session_id: options.session_id,
    case_ids: options.case_ids ?? [],
    include_charts: options.include_charts ?? true,
  })
  return data
}

export async function exportCSV(resourceType: string, resourceIds: string[]) {
  const { data } = await api.post(`/export/csv/${resourceType}`, {
    resource_ids: resourceIds,
  })
  return data
}

export async function downloadBlob(url: string, filename: string) {
  const { data } = await api.get(url, { responseType: "blob" })
  const blob = new Blob([data])
  const link = document.createElement("a")
  link.href = URL.createObjectURL(blob)
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}
