"use client";

import { useState } from "react";
import * as analyticsService from "@/services/analytics";
import type { ForecastResponse, ForecastRequest } from "@/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, TrendingUp } from "lucide-react";
import { toast } from "sonner";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";

export default function ForecastingPage() {
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [type, setType] = useState("crime_volume");
  const [days, setDays] = useState(30);

  const generateForecast = async () => {
    setLoading(true);
    try {
      const data = await analyticsService.getForecast({
        forecast_type: type,
        days_ahead: days,
      });
      setForecast(data);
    } catch {
      toast.error("Forecast generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Forecasting</h1>
        <p className="text-sm text-muted-foreground">
          Predictive crime analysis with confidence intervals
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generate Forecast</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end gap-4">
            <div className="space-y-2">
              <Label>Type</Label>
              <Select value={type} onValueChange={(v) => v && setType(v)}>
                <SelectTrigger className="w-44">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="crime_volume">Crime Volume</SelectItem>
                  <SelectItem value="hotspot_risk">Hotspot Risk</SelectItem>
                  <SelectItem value="gang_activity">Gang Activity</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Days Ahead</Label>
              <Input
                type="number"
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value) || 30)}
                className="w-24"
              />
            </div>
            <Button onClick={generateForecast} disabled={loading}>
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <TrendingUp className="h-4 w-4 mr-2" />
              )}
              Generate
            </Button>
          </div>
        </CardContent>
      </Card>

      {forecast && (
        <div className="grid gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Forecast Chart</CardTitle>
              <p className="text-sm text-muted-foreground">
                Model: {forecast.model_used} · Confidence:{" "}
                {(forecast.confidence_level * 100).toFixed(0)}%
              </p>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={forecast.forecast_data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 10 }}
                      tickFormatter={(v: string) => v.slice(5)}
                    />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip
                      labelFormatter={(v) => `Date: ${v}`}
                      formatter={(value) => [
                        Number(value).toFixed(1),
                      ]}
                    />
                    <Area
                      type="monotone"
                      dataKey="upper_bound"
                      stroke="none"
                      fill="#2563eb"
                      fillOpacity={0.1}
                    />
                    <Area
                      type="monotone"
                      dataKey="lower_bound"
                      stroke="none"
                      fill="#ffffff"
                      fillOpacity={1}
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted_value"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="upper_bound"
                      stroke="#93c5fd"
                      strokeWidth={1}
                      strokeDasharray="4 4"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="lower_bound"
                      stroke="#93c5fd"
                      strokeWidth={1}
                      strokeDasharray="4 4"
                      dot={false}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Features Used</CardTitle>
            </CardHeader>
            <CardContent>
              {forecast.features_used?.length ? (
                <ul className="space-y-1">
                  {forecast.features_used.map((f, i) => (
                    <li key={i} className="text-sm">• {f}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No feature data available</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
