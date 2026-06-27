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
import { Search, Loader2 } from "lucide-react"
import { toast } from "sonner"
import * as analyticsService from "@/services/analytics"
import type { CrimeHotspot } from "@/types"
import { HotspotMap } from "@/components/map/hotspot-map"

export default function MapPage() {
  const [hotspots, setHotspots] = useState<CrimeHotspot[]>([])
  const [loading, setLoading] = useState(false)
  const [days, setDays] = useState(30)

  const loadHotspots = async () => {
    setLoading(true)
    try {
      const data = await analyticsService.getHotspots({ days })
      setHotspots(data as CrimeHotspot[])
    } catch {
      toast.error("Failed to load hotspots")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Crime Map</h1>
        <p className="text-sm text-muted-foreground">
          Geospatial crime hotspot analysis
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Hotspot Analysis</CardTitle>
            <div className="flex items-end gap-4">
              <div className="space-y-2">
                <Label>Days</Label>
                <Input
                  type="number"
                  value={days}
                  onChange={(e) => setDays(parseInt(e.target.value) || 30)}
                  className="w-24"
                />
              </div>
              <Button onClick={loadHotspots} disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Search className="h-4 w-4 mr-2" />
                )}
                Load Hotspots
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[600px]">
            <HotspotMap hotspots={hotspots} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
