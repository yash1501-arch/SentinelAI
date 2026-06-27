"use client"

import { useRef, useEffect } from "react"
import type { Visualization } from "@/types"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

type Props = {
  visualizations: Visualization[]
}

export function Visualizations({ visualizations }: Props) {
  if (!visualizations?.length) return null

  return (
    <div className="space-y-3 mt-3">
      {visualizations.map((viz, i) => (
        <div key={i}>
          <p className="text-xs font-medium text-muted-foreground mb-1">
            {viz.title}
          </p>
          {renderViz(viz)}
        </div>
      ))}
    </div>
  )
}

function renderViz(viz: Visualization) {
  switch (viz.type) {
    case "table":
      return <VizTable data={viz.data} />
    case "line":
      return <VizLine data={viz.data} />
    case "bar":
      return <VizBar data={viz.data} />
    case "map":
      return <VizMap data={viz.data} />
    case "gauge":
      return <VizGauge data={viz.data} />
    case "network":
    case "graph":
      return <VizNetwork data={viz.data} />
    default:
      return null
  }
}

function VizTable({ data }: { data: Record<string, unknown>[] }) {
  if (!data.length) return null
  const keys = Object.keys(data[0])
  return (
    <Card className="overflow-hidden">
      <div className="max-h-48 overflow-y-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {keys.map((k) => (
                <TableHead key={k} className="text-xs">
                  {k}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, i) => (
              <TableRow key={i}>
                {keys.map((k) => (
                  <TableCell key={k} className="text-xs py-1">
                    {String(row[k] ?? "-").slice(0, 30)}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  )
}

function VizLine({ data }: { data: Record<string, unknown>[] }) {
  if (!data.length) return null
  const keys = Object.keys(data[0])
  const xKey = keys[0]
  const yKey = keys[1]
  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data as unknown as Record<string, number>[]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey={xKey}
            tickFormatter={(v: unknown) =>
              isNaN(Date.parse(v as string)) ? String(v).slice(0, 7) : new Date(v as string).toLocaleDateString("en-US", { month: "short", year: "2-digit" })
            }
            tick={{ fontSize: 10 }}
          />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function VizBar({ data }: { data: Record<string, unknown>[] }) {
  if (!data.length) return null
  const keys = Object.keys(data[0])
  const xKey = keys[0]
  const yKey = keys[1] || "count"
  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data as unknown as Record<string, number>[]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip />
          <Bar dataKey={yKey} fill="#2563eb" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function VizMap({ data }: { data: Record<string, unknown>[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !data.length) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    const w = canvas.clientWidth
    const h = canvas.clientHeight
    canvas.width = w * dpr
    canvas.height = h * dpr
    ctx.scale(dpr, dpr)

    ctx.fillStyle = "hsl(var(--card))"
    ctx.fillRect(0, 0, w, h)

    const points = data
      .map((d) => ({
        lat: Number((d as Record<string, number>).latitude),
        lng: Number((d as Record<string, number>).longitude),
        count: Number((d as Record<string, number>).crime_count || (d as Record<string, number>).count || 1),
      }))
      .filter((p) => !isNaN(p.lat) && !isNaN(p.lng))

    if (points.length === 0) return

    const lats = points.map((p) => p.lat)
    const lngs = points.map((p) => p.lng)
    const minLat = Math.min(...lats)
    const maxLat = Math.max(...lats)
    const minLng = Math.min(...lngs)
    const maxLng = Math.max(...lngs)
    const pad = 0.02
    const latRange = maxLat - minLat + pad * 2 || 1
    const lngRange = maxLng - minLng + pad * 2 || 1

    const margin = 20
    const plotW = w - margin * 2
    const plotH = h - margin * 2

    const toX = (lng: number) => margin + ((lng - (minLng - pad)) / lngRange) * plotW
    const toY = (lat: number) => margin + plotH - ((lat - (minLat - pad)) / latRange) * plotH

    const maxCount = Math.max(...points.map((p) => p.count), 1)

    ctx.strokeStyle = "hsl(var(--border))"
    ctx.lineWidth = 0.5
    ctx.strokeRect(margin, margin, plotW, plotH)

    points.forEach((p) => {
      const x = toX(p.lng)
      const y = toY(p.lat)
      const radius = 4 + (p.count / maxCount) * 14

      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius)
      const alpha = 0.3 + (p.count / maxCount) * 0.5
      gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha})`)
      gradient.addColorStop(0.5, `rgba(239, 68, 68, ${alpha * 0.5})`)
      gradient.addColorStop(1, "rgba(239, 68, 68, 0)")

      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fillStyle = gradient
      ctx.fill()

      ctx.beginPath()
      ctx.arc(x, y, 3, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(239, 68, 68, ${0.5 + (p.count / maxCount) * 0.5})`
      ctx.fill()
    })
  }, [data])

  if (!data.length) return null

  return (
    <Card className="overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-36"
        style={{ aspectRatio: "16/9" }}
      />
      <div className="max-h-32 overflow-y-auto space-y-1 px-2 pb-2">
        {data.map((point, i) => (
          <div
            key={i}
            className="flex items-center justify-between text-xs border-b pb-1"
          >
            <span className="font-mono">
              ({Number((point as Record<string, number>).latitude).toFixed(4)},{" "}
              {Number((point as Record<string, number>).longitude).toFixed(4)})
            </span>
            <Badge variant="outline" className="text-[10px]">
              {(point as Record<string, number>).crime_count || (point as Record<string, number>).count || "1"} incidents
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  )
}

function VizGauge({ data }: { data: Record<string, unknown>[] | Record<string, unknown> }) {
  const item = Array.isArray(data) ? data[0] || {} : data
  const score = Number(item.risk_score ?? 0)
  const pct = (score * 100).toFixed(0)
  const color =
    score > 0.7
      ? "text-destructive"
      : score > 0.4
        ? "text-yellow-500"
        : "text-green-500"
  return (
    <div className="flex items-center gap-4 p-2 rounded-lg border">
      <div className={`text-2xl font-bold ${color}`}>{pct}%</div>
      <div className="text-xs text-muted-foreground">
        <p>Risk: {item.risk_level as string}</p>
        <p>Archetype: {item.archetype as string}</p>
      </div>
    </div>
  )
}


function VizNetwork({ data }: { data: Record<string, unknown>[] | Record<string, unknown> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    const w = canvas.clientWidth
    const h = canvas.clientHeight
    canvas.width = w * dpr
    canvas.height = h * dpr
    ctx.scale(dpr, dpr)

    ctx.fillStyle = "hsl(var(--card))"
    ctx.fillRect(0, 0, w, h)

    // Parse network data - could be array of records or {nodes, edges}
    const records = Array.isArray(data) ? data : [data]
    const nodeSet = new Map<string, { x: number; y: number; label: string }>()
    const edgeList: { from: string; to: string }[] = []

    // Extract nodes and edges from graph result records
    for (const record of records) {
      // Handle various formats from Neo4j/Graph Agent
      const nodes = (record as Record<string, unknown>).nodes as Record<string, unknown>[] | undefined
      const edges = (record as Record<string, unknown>).edges as Record<string, unknown>[] | undefined
      const connections = (record as Record<string, unknown>).connections as Record<string, unknown>[] | undefined

      if (nodes) {
        for (const n of nodes) {
          const id = String((n as Record<string, string>).id || (n as Record<string, string>).name || Math.random())
          if (!nodeSet.has(id)) {
            nodeSet.set(id, { x: 0, y: 0, label: String((n as Record<string, string>).name || (n as Record<string, string>).label || id).slice(0, 12) })
          }
        }
      }
      if (edges) {
        for (const e of edges) {
          edgeList.push({ from: String((e as Record<string, string>).source || (e as Record<string, string>).from), to: String((e as Record<string, string>).target || (e as Record<string, string>).to) })
        }
      }
      if (connections) {
        for (const c of connections) {
          const name = String((c as Record<string, string>).name || (c as Record<string, string>).first_name || "Node")
          const id = String((c as Record<string, string>).id || name)
          if (!nodeSet.has(id)) {
            nodeSet.set(id, { x: 0, y: 0, label: name.slice(0, 12) })
          }
          // Connect to first node
          const firstNode = nodeSet.keys().next().value
          if (firstNode && firstNode !== id) {
            edgeList.push({ from: firstNode, to: id })
          }
        }
      }
    }

    // If no structured data, try to extract person names from flat records
    if (nodeSet.size === 0) {
      for (const record of records) {
        const rec = record as Record<string, string>
        const name = rec.first_name ? `${rec.first_name} ${rec.last_name || ""}` : rec.name || rec.label
        if (name) {
          nodeSet.set(String(rec.id || name), { x: 0, y: 0, label: String(name).slice(0, 12) })
        }
      }
    }

    if (nodeSet.size === 0) return

    // Layout: circular
    const cx = w / 2
    const cy = h / 2
    const radius = Math.min(w, h) * 0.35
    const nodeArr = Array.from(nodeSet.entries())
    nodeArr.forEach(([id, node], i) => {
      const angle = (2 * Math.PI * i) / nodeArr.length
      node.x = cx + radius * Math.cos(angle)
      node.y = cy + radius * Math.sin(angle)
    })

    // Draw edges
    ctx.strokeStyle = "hsl(var(--border))"
    ctx.lineWidth = 1
    for (const edge of edgeList) {
      const from = nodeSet.get(edge.from)
      const to = nodeSet.get(edge.to)
      if (from && to) {
        ctx.beginPath()
        ctx.moveTo(from.x, from.y)
        ctx.lineTo(to.x, to.y)
        ctx.stroke()
      }
    }

    // Draw nodes
    nodeArr.forEach(([id, node], i) => {
      ctx.beginPath()
      ctx.arc(node.x, node.y, 8, 0, Math.PI * 2)
      ctx.fillStyle = i === 0 ? "#2563eb" : "#6366f1"
      ctx.fill()
      ctx.strokeStyle = "hsl(var(--background))"
      ctx.lineWidth = 2
      ctx.stroke()

      // Label
      ctx.fillStyle = "hsl(var(--foreground))"
      ctx.font = "9px sans-serif"
      ctx.textAlign = "center"
      ctx.fillText(node.label, node.x, node.y + 18)
    })
  }, [data])

  const records = Array.isArray(data) ? data : [data]
  const count = records.length

  return (
    <Card className="overflow-hidden">
      <canvas ref={canvasRef} className="w-full h-48" />
      <p className="text-xs text-muted-foreground px-2 pb-2">
        Network: {count} record(s) visualized
      </p>
    </Card>
  )
}
