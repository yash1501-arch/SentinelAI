"use client";

import { useState, useEffect } from "react";
import * as analyticsService from "@/services/analytics";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { ExportButton } from "@/components/export/export-dialog";
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
} from "recharts";

export default function AnalyticsPage() {
  const [trends, setTrends] = useState([]);
  const [stats, setStats] = useState<Record<string, number | string | null>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsService.getTrends().then(setTrends),
      analyticsService.getStatistics().then(setStats),
    ]).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>
    );
  }

  const statCards = [
    { label: "Total Cases", value: stats.total_cases },
    { label: "Solved", value: stats.solved_cases },
    { label: "Heinous", value: stats.heinous_cases },
    { label: "Avg Loss", value: stats.avg_loss ? `$${stats.avg_loss}` : "-" },
  ];

  const crimeDist =
    trends.length > 0
      ? Object.entries(
          trends.reduce(
            (acc: Record<string, number>, t: { crime_type: string; count: number }) => {
              acc[t.crime_type] = (acc[t.crime_type] || 0) + t.count;
              return acc;
            },
            {}
          )
        )
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 8)
      : [];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-sm text-muted-foreground">
            Crime trends, statistics, and patterns
          </p>
        </div>
        <ExportButton
          sessionId="analytics-page"
          variant="default"
          size="default"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{card.value ?? "-"}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="trends">
        <TabsList>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Crime Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="month"
                      tickFormatter={(v) =>
                        new Date(v).toLocaleDateString("en-US", {
                          month: "short",
                          year: "2-digit",
                        })
                      }
                    />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#2563eb"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Crime Type Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={crimeDist}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
