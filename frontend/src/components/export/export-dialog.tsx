"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Download, FileText, FileSpreadsheet, Loader2 } from "lucide-react"
import { exportPDF, exportCSV, type ExportFormat } from "@/services/export"

export function ExportButton({
  sessionId,
  caseIds,
  variant = "outline",
  size = "sm",
}: {
  sessionId?: string
  caseIds?: string[]
  variant?: "outline" | "default" | "ghost"
  size?: "sm" | "default" | "icon-sm"
}) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [preferredFormat, setPreferredFormat] = useState<ExportFormat>("pdf")

  const handleDropdownSelect = (format: ExportFormat) => {
    setPreferredFormat(format)
    setDialogOpen(true)
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex shrink-0 items-center justify-center gap-2 rounded-md border bg-background px-3 py-1.5 text-sm font-medium hover:bg-accent transition-colors">
            <Download className="h-4 w-4" />
            Export
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => handleDropdownSelect("pdf")}>
            <FileText className="mr-2 h-4 w-4" />
            Export as PDF
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleDropdownSelect("csv")}>
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            Export as CSV
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <ExportDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        format={preferredFormat}
        sessionId={sessionId}
        caseIds={caseIds}
      />
    </>
  )
}

function ExportDialog({
  open,
  onOpenChange,
  format: initialFormat,
  sessionId,
  caseIds,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  format: ExportFormat
  sessionId?: string
  caseIds?: string[]
}) {
  const [format, setFormat] = useState<ExportFormat>(initialFormat)
  const [includeCharts, setIncludeCharts] = useState(true)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setFormat(initialFormat)
  }, [initialFormat, open])

  const handleExport = async () => {
    setLoading(true)
    try {
      if (format === "pdf") {
        await exportPDF({
          session_id: sessionId ?? crypto.randomUUID(),
          case_ids: caseIds,
          include_charts: includeCharts,
        })
        toast.success("PDF export started. Check downloads when ready.")
      } else {
        await exportCSV("cases", caseIds ?? [])
        toast.success("CSV export started. Check downloads when ready.")
      }
      onOpenChange(false)
    } catch {
      toast.error("Export failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Report</DialogTitle>
          <DialogDescription>
            Choose format and options for your export.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <Label htmlFor="format">Format</Label>
            <Select
              value={format}
              onValueChange={(v) => setFormat(v as ExportFormat)}
            >
              <SelectTrigger id="format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">
                  <FileText className="mr-2 inline h-4 w-4" />
                  PDF Document
                </SelectItem>
                <SelectItem value="csv">
                  <FileSpreadsheet className="mr-2 inline h-4 w-4" />
                  CSV Spreadsheet
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {format === "pdf" && (
            <div className="flex items-center justify-between">
              <Label htmlFor="charts">Include charts</Label>
              <Switch
                id="charts"
                checked={includeCharts}
                onCheckedChange={setIncludeCharts}
              />
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Export
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
