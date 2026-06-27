"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import * as casesService from "@/services/cases"
import type { CrimeIncident, TimelineEvent, Evidence } from "@/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, Download, FileText, Table as TableIcon } from "lucide-react"
import { toast } from "sonner"
import * as exportService from "@/services/export"

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    year: "numeric", month: "short", day: "numeric",
  })
}

const EVENT_ICONS: Record<string, string> = {
  fir_registered: "📋",
  incident_reported: "🚨",
  investigation_started: "🔍",
  evidence_collected: "🔬",
  suspect_identified: "👤",
  arrest_made: "⛓️",
  chargesheet_filed: "📄",
  court_hearing: "⚖️",
  conviction: "✅",
  acquittal: "❌",
  case_closed: "🔒",
}

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const caseId = params.id as string

  const [caseData, setCaseData] = useState<CrimeIncident | null>(null)
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!caseId) return
    const load = async () => {
      setLoading(true)
      try {
        const [c, t, e] = await Promise.all([
          casesService.getCase(caseId),
          casesService.getTimeline(caseId),
          casesService.getEvidence(caseId),
        ])
        setCaseData(c)
        setTimeline(t)
        setEvidence(e)
      } catch {
        toast.error("Failed to load case details")
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [caseId])

  const handleExportPDF = async () => {
    try {
      await exportService.exportPDF({ session_id: caseId, case_ids: [caseId], include_charts: false })
      toast.success("PDF export initiated")
    } catch {
      toast.error("Export failed")
    }
  }

  const handleExportCSV = async () => {
    try {
      await exportService.exportCSV("cases", [caseId])
      toast.success("CSV export initiated")
    } catch {
      toast.error("Export failed")
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-lg text-muted-foreground">Case not found</p>
        <Button variant="outline" className="mt-4" onClick={() => router.push("/cases")}>
          Back to Cases
        </Button>
      </div>
    )
  }

  const ct = caseData.crime_type

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/cases")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{ct?.name || "Case"} Detail</h1>
            <p className="text-sm text-muted-foreground font-mono">
              FIR: {caseData.fir_id?.slice(0, 8)} | ID: {caseData.id?.slice(0, 8)}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExportPDF}>
            <FileText className="h-4 w-4 mr-2" />
            PDF
          </Button>
          <Button variant="outline" size="sm" onClick={handleExportCSV}>
            <TableIcon className="h-4 w-4 mr-2" />
            CSV
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Incident Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Date</span>
              <span className="text-sm font-medium">{formatDate(caseData.incident_date)}</span>
            </div>
            {caseData.incident_time && (
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Time</span>
                <span className="text-sm font-medium">{caseData.incident_time}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Status</span>
              <Badge variant={caseData.is_solved ? "default" : "secondary"}>
                {caseData.is_solved ? "Solved" : "Open"}
              </Badge>
            </div>
            <Separator />
            <div>
              <span className="text-sm text-muted-foreground block mb-1">Description</span>
              <p className="text-sm">{caseData.description}</p>
            </div>
            {caseData.modus_operandi && (
              <div>
                <span className="text-sm text-muted-foreground block mb-1">Modus Operandi</span>
                <p className="text-sm">{caseData.modus_operandi}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Crime Classification</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {ct && (
              <>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Type</span>
                  <Badge variant="outline">{ct.name}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Category</span>
                  <span className="text-sm font-medium">{ct.category}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Severity</span>
                  <span className="text-sm font-medium">{ct.severity_level}/5</span>
                </div>
                {ct.description && (
                  <div>
                    <span className="text-sm text-muted-foreground block mb-1">Details</span>
                    <p className="text-sm">{ct.description}</p>
                  </div>
                )}
              </>
            )}
            <Separator />
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Injuries</span>
              <span className="text-sm font-medium">{caseData.injury_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Fatalities</span>
              <span className="text-sm font-medium">{caseData.fatality_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Property Loss</span>
              <span className="text-sm font-medium">₹{caseData.property_value_loss?.toLocaleString() || "0"}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          {timeline.length === 0 ? (
            <p className="text-sm text-muted-foreground">No timeline events</p>
          ) : (
            <div className="space-y-0">
              {timeline.map((event, i) => (
                <div key={event.id} className="flex gap-4 pb-4 relative">
                  {i < timeline.length - 1 && (
                    <div className="absolute left-[17px] top-8 bottom-0 w-px bg-border" />
                  )}
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-sm">
                    {EVENT_ICONS[event.event_type] || "📌"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{event.title}</p>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(event.timestamp)}
                      </span>
                    </div>
                    {event.description && (
                      <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                    )}
                    {event.actor && (
                      <p className="text-xs text-muted-foreground mt-1">By: {event.actor}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Evidence ({evidence.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {evidence.length === 0 ? (
            <p className="text-sm text-muted-foreground">No evidence recorded</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {evidence.map((e) => (
                <Card key={e.id} className="border border-border/50">
                  <CardContent className="p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-[10px]">{e.evidence_type}</Badge>
                      {e.is_forensically_analyzed && (
                        <Badge className="text-[10px] bg-green-100 text-green-800 hover:bg-green-100">Analyzed</Badge>
                      )}
                    </div>
                    <p className="text-sm font-medium">{e.name}</p>
                    {e.description && (
                      <p className="text-xs text-muted-foreground">{e.description}</p>
                    )}
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                      <span>Admissible: {e.is_admissible ? "Yes" : "No"}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-center gap-4 pt-2 pb-8">
        <Button variant="outline" onClick={() => router.push("/cases")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Cases
        </Button>
        <Button onClick={handleExportPDF}>
          <Download className="h-4 w-4 mr-2" />
          Download Report
        </Button>
      </div>
    </div>
  )
}
