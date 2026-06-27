"use client";

import { useState, useEffect } from "react";
import * as alertsService from "@/services/alerts";
import type { Alert } from "@/services/alerts";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  AlertTriangle,
  Bell,
  TrendingUp,
  User,
  MapPin,
  FileSearch,
  RefreshCw,
} from "lucide-react";

const severityConfig = {
  critical: { color: "bg-red-500/10 text-red-600 border-red-200", icon: AlertTriangle },
  high: { color: "bg-orange-500/10 text-orange-600 border-orange-200", icon: AlertTriangle },
  warning: { color: "bg-amber-500/10 text-amber-600 border-amber-200", icon: Bell },
  info: { color: "bg-blue-500/10 text-blue-600 border-blue-200", icon: Bell },
};

const typeIcons: Record<string, typeof AlertTriangle> = {
  forecast: TrendingUp,
  offender: User,
  hotspot: MapPin,
  case: FileSearch,
  network: AlertTriangle,
  pattern: AlertTriangle,
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await alertsService.getAlerts(30);
      setAlerts(data);
    } catch {
      // If backend isn't running, show empty state
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const criticalCount = alerts.filter((a) => a.severity === "critical").length;
  const highCount = alerts.filter((a) => a.severity === "high").length;

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Smart Alerts</h1>
          <p className="text-sm text-muted-foreground">
            AI-generated intelligence alerts from forecasting, profiling, and
            pattern analysis
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {criticalCount > 0 && (
              <Badge variant="destructive">{criticalCount} critical</Badge>
            )}
            {highCount > 0 && (
              <Badge className="bg-orange-500 text-white">
                {highCount} high
              </Badge>
            )}
          </div>
          <Button variant="outline" size="sm" onClick={loadAlerts}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-5">
            <p className="text-3xl font-bold text-red-600">{criticalCount}</p>
            <p className="text-sm text-muted-foreground">Critical</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-3xl font-bold text-orange-600">{highCount}</p>
            <p className="text-sm text-muted-foreground">High Priority</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-3xl font-bold text-amber-600">
              {alerts.filter((a) => a.severity === "warning").length}
            </p>
            <p className="text-sm text-muted-foreground">Warnings</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-3xl font-bold">{alerts.length}</p>
            <p className="text-sm text-muted-foreground">Total Alerts</p>
          </CardContent>
        </Card>
      </div>

      {/* Alert list */}
      {alerts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Bell className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold">No active alerts</h3>
            <p className="text-sm text-muted-foreground mt-1">
              All systems normal. Alerts will appear when anomalies are detected.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const config = severityConfig[alert.severity] || severityConfig.info;
            const TypeIcon = typeIcons[alert.type] || Bell;
            const SevIcon = config.icon;

            return (
              <Card key={alert.id} className="transition-colors hover:bg-accent/30">
                <CardContent className="flex items-start gap-4 pt-5">
                  <div className={`p-2.5 rounded-lg shrink-0 ${config.color}`}>
                    <SevIcon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-sm">{alert.title}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {alert.description}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                      <Badge variant="outline" className="text-[10px]">
                        <TypeIcon className="h-3 w-3 mr-1" />
                        {alert.type}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        Source: {alert.source}
                      </span>
                    </div>
                  </div>
                  {alert.actionable && (
                    <Button variant="outline" size="sm" className="shrink-0">
                      Investigate
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
