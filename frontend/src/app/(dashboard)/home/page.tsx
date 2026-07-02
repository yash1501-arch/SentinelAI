"use client";

import { useState, useEffect } from "react";
import { useAuthStore } from "@/store/auth";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Bot,
  BarChart3,
  Map,
  Share2,
  FileSearch,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Skull,
  ArrowUpRight,
} from "lucide-react";
import Link from "next/link";
import * as analyticsService from "@/services/analytics";
import * as alertsService from "@/services/alerts";
import type { Alert } from "@/services/alerts";

const FALLBACK_ALERTS = [
  {
    id: "1",
    title: "Crime spike predicted in Zone 4 this weekend",
    severity: "critical" as const,
    type: "forecast",
    description: "ML model forecasts 42% increase in theft cases in Koramangala area",
    source: "Forecast Agent",
    created_at: new Date().toISOString(),
    actionable: true,
  },
  {
    id: "2",
    title: "New case matches serial offender pattern #7",
    severity: "critical" as const,
    type: "pattern",
    description: "FIR-201/MNG/2025 shows 87% similarity with 4 previous robbery cases",
    source: "RAG Agent",
    created_at: new Date().toISOString(),
    actionable: true,
  },
  {
    id: "3",
    title: "Suspicious transaction chain: 5 accounts, ₹15L",
    severity: "warning" as const,
    type: "network",
    description: "Layered transfer chain detected across 5 bank accounts in 48 hours",
    source: "Graph Agent",
    created_at: new Date().toISOString(),
    actionable: true,
  },
];

const quickActions = [
  { title: "AI Chat", description: "Ask about cases, trends, suspects", icon: Bot, href: "/chat", color: "text-blue-500" },
  { title: "Cases", description: "Browse crime records", icon: FileSearch, href: "/cases", color: "text-orange-500" },
  { title: "Analytics", description: "Trends and statistics", icon: BarChart3, href: "/analytics", color: "text-green-500" },
  { title: "Map", description: "Crime hotspots", icon: Map, href: "/map", color: "text-red-500" },
  { title: "Network", description: "Criminal connections", icon: Share2, href: "/network", color: "text-purple-500" },
  { title: "Forecasting", description: "Predict patterns", icon: TrendingUp, href: "/forecasting", color: "text-cyan-500" },
];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [stats, setStats] = useState<Record<string, number | string | null>>({});
  const [alerts, setAlerts] = useState<Alert[]>(FALLBACK_ALERTS as Alert[]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsService.getStatistics().then(setStats),
      alertsService.getAlerts(5).then(setAlerts).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const statCards = [
    {
      label: "Total Cases",
      value: stats.total_cases ?? "—",
      icon: FileSearch,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
    },
    {
      label: "Solved Cases",
      value: stats.solved_cases ?? "—",
      icon: CheckCircle2,
      color: "text-green-500",
      bg: "bg-green-500/10",
      trend: stats.total_cases ? `${(((stats.solved_cases as number) / (stats.total_cases as number)) * 100).toFixed(0)}%` : null,
      trendUp: true,
    },
    {
      label: "Heinous Crimes",
      value: stats.heinous_cases ?? "—",
      icon: Skull,
      color: "text-red-500",
      bg: "bg-red-500/10",
    },
    {
      label: "Active Alerts",
      value: alerts.length,
      icon: AlertTriangle,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back, {user?.full_name?.split(" ")[0] || "Officer"}
          </h1>
          <p className="text-muted-foreground mt-1">
            Here&apos;s your intelligence overview for today
          </p>
        </div>
        <Link
          href="/chat"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <Bot className="h-4 w-4" />
          Ask SentinelAI
        </Link>
      </div>

      {/* Stats */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label}>
                <CardContent className="flex items-center gap-4 pt-6">
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                      {stat.trend && (
                        <span className="inline-flex items-center text-xs font-medium text-green-600">
                          <ArrowUpRight className="h-3 w-3" />
                          {stat.trend}
                        </span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Alerts + Quick Actions */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Smart Alerts */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Smart Alerts</CardTitle>
              <Badge variant="destructive" className="text-[10px]">
                {alerts.filter((a) => a.severity === "critical").length} critical
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-start gap-3 rounded-lg border p-3"
              >
                <AlertTriangle
                  className={`h-4 w-4 mt-0.5 shrink-0 ${
                    alert.severity === "critical"
                      ? "text-red-500"
                      : "text-amber-500"
                  }`}
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium leading-tight">
                    {alert.title}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-muted-foreground">
                      {alert.source || alert.type}
                    </span>
                    <Badge variant="outline" className="text-[10px]">
                      {alert.type}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link key={action.href} href={action.href}>
                  <Card className="h-full transition-colors hover:bg-accent/50 cursor-pointer">
                    <CardContent className="flex items-center gap-3 pt-5 pb-4">
                      <div className={`p-2 rounded-lg bg-background ${action.color}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{action.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {action.description}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
