"use client"

import { useEffect, useRef, useState } from "react"
import type { CrimeHotspot } from "@/types"

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

type HotspotMapProps = {
  hotspots: CrimeHotspot[]
}

export function HotspotMap({ hotspots }: HotspotMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<unknown>(null)
  const markersRef = useRef<{ remove: () => void }[]>([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (!MAPBOX_TOKEN) return
    let cancelled = false
    import("mapbox-gl").then((mod) => {
      if (cancelled) return
      mod.default.accessToken = MAPBOX_TOKEN
      setLoaded(true)
    })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    if (!loaded || !containerRef.current || mapRef.current) return
    let cancelled = false

    import("mapbox-gl").then((mod) => {
      if (cancelled || !containerRef.current) return
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const mbgl: any = mod.default

      const map = new mbgl.Map({
        container: containerRef.current,
        style: "mapbox://styles/mapbox/dark-v11",
        center: [76.5, 12.3],
        zoom: 10,
      })
      map.addControl(new mbgl.NavigationControl(), "top-right")
      mapRef.current = map

      map.on("load", () => {
        map.resize()
      })
    })

    return () => {
      cancelled = true
      if (mapRef.current) {
        ;(mapRef.current as { remove: () => void }).remove()
        mapRef.current = null
      }
    }
  }, [loaded])

  useEffect(() => {
    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []

    if (hotspots.length === 0) return

    const map = mapRef.current as {
      loaded: () => boolean
      fitBounds: (b: unknown, o?: unknown) => void
    } | null
    if (!map || !map.loaded()) return

    import("mapbox-gl").then((mod) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const mbgl: any = mod.default
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const curMap: any = mapRef.current

      const bounds = new mbgl.LngLatBounds()
      hotspots.forEach((h, i) => {
        const el = document.createElement("div")
        el.className =
          "flex h-6 w-6 items-center justify-center rounded-full bg-destructive/80 text-[10px] font-bold text-destructive-foreground shadow-md ring-2 ring-background cursor-pointer hover:scale-110 transition-transform"
        el.textContent = String(i + 1)

        const marker = new mbgl.Marker({ element: el })
          .setLngLat([h.longitude, h.latitude])
          .setPopup(
            new mbgl.Popup({ offset: 25 }).setHTML(
              `<div class="text-xs space-y-1">
                <p class="font-semibold">Cluster ${h.cluster_id ?? "N/A"}</p>
                <p>Risk: ${((h.risk_score ?? 0) * 100).toFixed(0)}%</p>
                <p>Density: ${h.crime_density?.toFixed(2) ?? "-"}</p>
                <p>Radius: ${h.radius_meters?.toFixed(0) ?? "-"}m</p>
              </div>`
            )
          )
          .addTo(curMap)
        markersRef.current.push(marker)
        bounds.extend([h.longitude, h.latitude])
      })

      if (!bounds.isEmpty()) {
        curMap.fitBounds(bounds, { padding: 60, maxZoom: 14 })
      }
    })
  }, [hotspots, loaded])

  if (!MAPBOX_TOKEN) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border bg-muted/30">
        <div className="text-center max-w-sm">
          <p className="text-sm font-medium mb-1">Mapbox token not configured</p>
          <p className="text-xs text-muted-foreground">
            Set <code className="rounded bg-muted px-1">NEXT_PUBLIC_MAPBOX_TOKEN</code> in{" "}
            <code className="rounded bg-muted px-1">.env.local</code>
          </p>
          {hotspots.length > 0 && (
            <div className="mt-4 text-left max-h-48 overflow-y-auto space-y-1">
              <p className="text-xs font-medium text-muted-foreground">
                {hotspots.length} hotspot(s) loaded:
              </p>
              {hotspots.map((h, i) => (
                <p key={h.id} className="text-xs text-muted-foreground">
                  #{i + 1} ({h.latitude.toFixed(4)}, {h.longitude.toFixed(4)})
                  {h.risk_score != null && ` — Risk: ${(h.risk_score * 100).toFixed(0)}%`}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (!loaded) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border bg-muted/30">
        <p className="text-sm text-muted-foreground">Loading map…</p>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="h-full w-full rounded-lg overflow-hidden"
    />
  )
}
