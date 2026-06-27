"use client"

import { useState } from "react"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Search, Clock, Loader2, Gavel, FileText, UserCheck, Scale, CheckCircle, XCircle, PlusCircle, AlertCircle, ArrowRight, Ban } from "lucide-react"
import { toast } from "sonner"
import api from "@/lib/api"
import type { TimelineEvent, TimelineEventType } from "@/types"

const eventConfig: Record<TimelineEventType, { icon: typeof Clock; color: string; label: string }> = {
  fir_registered: { icon: FileText, color: "text-blue-500", label: "FIR Registered" },
  incident_reported: { icon: AlertCircle, color: "text-orange-500", label: "Incident Reported" },
  investigation_started: { icon: Search, color: "text-cyan-500", label: "Investigation Started" },
  evidence_collected: { icon: PlusCircle, color: "text-purple-500", label: "Evidence Collected" },
  suspect_identified: { icon: UserCheck, color: "text-yellow-500", label: "Suspect Identified" },
  arrest_made: { icon: Ban, color: "text-red-500", label: "Arrest Made" },
  chargesheet_filed: { icon: Gavel, color: "text-amber-500", label: "Chargesheet Filed" },
  court_hearing: { icon: Scale, color: "text-indigo-500", label: "Court Hearing" },
  conviction: { icon: CheckCircle, color: "text-green-500", label: "Conviction" },
  acquittal: { icon: XCircle, color: "text-slate-500", label: "Acquittal" },
  case_closed: { icon: CheckCircle, color: "text-green-600", label: "Case Closed" },
  note_added: { icon: FileText, color: "text-gray-500", label: "Note Added" },
  status_change: { icon: ArrowRight, color: "text-blue-400", label: "Status Change" },
  other: { icon: Clock, color: "text-muted-foreground", label: "Event" },
}

export default function TimelinePage() {
  const [caseId, setCaseId] = useState("")
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [loading, setLoading] = useState(false)

  const loadTimeline = async () => {
    if (!caseId.trim()) return
    setLoading(true)
    try {
      // Support both UUID and FIR number lookup
      let resolvedId = caseId.trim()

      // If it doesn't look like a UUID, try to find by FIR number first
      const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(resolvedId)
      if (!isUUID) {
        // Search cases by the entered text
        const { data: cases } = await api.get(`/cases/`, { params: { search: resolvedId, per_page: 1 } })
        if (cases && cases.length > 0) {
          resolvedId = cases[0].id
        } else {
          toast.error("Case not found. Try a valid Case ID (UUID) from the Cases page.")
          setLoading(false)
          return
        }
      }

      const { data } = await api.get<TimelineEvent[]>(`/cases/${resolvedId}/timeline`)
      setEvents(data)
      if (data.length === 0) {
        toast.info("No timeline events found for this case.")
      }
    } catch {
      toast.error("Failed to load timeline. Check the Case ID and try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Case Timeline</h1>
        <p className="text-sm text-muted-foreground">
          Chronological case event tracking
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select Case</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1 space-y-2">
              <Label>Case ID</Label>
              <Input
                placeholder="Enter case UUID..."
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
              />
            </div>
            <Button
              className="mt-6"
              onClick={loadTimeline}
              disabled={loading || !caseId.trim()}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Search className="h-4 w-4 mr-2" />
              )}
              Load Timeline
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <Card>
          <CardContent className="p-6 space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-32" />
                  <Skeleton className="h-12 w-full" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {!loading && events.length === 0 && (
        <Card>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium mb-1">No Timeline Data</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Enter a case ID above and click Load Timeline to view case events in chronological order.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {!loading && events.length > 0 && (
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />
          <div className="space-y-6">
            {events.map((event) => {
              const cfg = eventConfig[event.event_type] ?? eventConfig.other
              const Icon = cfg.icon
              return (
                <div key={event.id} className="relative flex gap-4 pl-3">
                  <div className={`relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-background ${cfg.color}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <Card className="flex-1">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="font-medium">{event.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(event.timestamp).toLocaleString()}
                            {event.actor && ` — ${event.actor}`}
                          </p>
                        </div>
                        <Badge variant="outline" className="shrink-0 text-xs">
                          {cfg.label}
                        </Badge>
                      </div>
                      {event.description && (
                        <p className="mt-2 text-sm text-muted-foreground">
                          {event.description}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
