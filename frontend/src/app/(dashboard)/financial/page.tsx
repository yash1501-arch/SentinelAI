"use client";

import { useState, useEffect } from "react";
import {
  Card, CardContent, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { DollarSign, AlertTriangle, TrendingUp } from "lucide-react";
import api from "@/lib/api";

type FinancialData = {
  summary: {
    total_transactions: number;
    suspicious_count: number;
    total_volume: number;
    fraud_rate: number;
  };
  suspicious_transactions: {
    id: string;
    amount: number;
    date: string | null;
    type: string;
    reason: string;
    risk_score: number;
  }[];
  high_value_transactions: {
    id: string;
    amount: number;
    date: string | null;
    type: string;
    is_suspicious: boolean;
  }[];
};

export default function FinancialPage() {
  const [data, setData] = useState<FinancialData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/analytics/financial")
      .then((res) => setData(res.data))
      .catch(() => toast.error("Failed to load financial data"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  const summary = data?.summary;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Financial Crime Intelligence</h1>
        <p className="text-sm text-muted-foreground">
          Suspicious transaction detection and money trail analysis
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Total Volume</p>
            </div>
            <p className="text-xl font-bold mt-1">
              ₹{((summary?.total_volume || 0) / 100000).toFixed(1)}L
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Transactions</p>
            </div>
            <p className="text-xl font-bold mt-1">
              {summary?.total_transactions || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-destructive" />
              <p className="text-xs text-muted-foreground">Suspicious</p>
            </div>
            <p className="text-xl font-bold mt-1 text-destructive">
              {summary?.suspicious_count || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-xs text-muted-foreground">Fraud Rate</p>
            <p className="text-xl font-bold mt-1">
              {((summary?.fraud_rate || 0) * 100).toFixed(2)}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Suspicious Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Suspicious Transactions</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Amount</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Risk</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.suspicious_transactions?.length ? (
                data.suspicious_transactions.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell className="font-medium">
                      ₹{t.amount.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-xs">
                      {t.date ? new Date(t.date).toLocaleDateString() : "-"}
                    </TableCell>
                    <TableCell className="text-xs">{t.type || "-"}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {t.reason || "Anomaly detected"}
                    </TableCell>
                    <TableCell>
                      <Badge variant={t.risk_score > 0.7 ? "destructive" : "secondary"}>
                        {((t.risk_score || 0) * 100).toFixed(0)}%
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground py-8">
                    No suspicious transactions detected
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* High Value Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>High-Value Transactions</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Amount</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Flag</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.high_value_transactions?.length ? (
                data.high_value_transactions.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell className="font-medium">
                      ₹{t.amount.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-xs">
                      {t.date ? new Date(t.date).toLocaleDateString() : "-"}
                    </TableCell>
                    <TableCell className="text-xs">{t.type || "-"}</TableCell>
                    <TableCell>
                      {t.is_suspicious && (
                        <Badge variant="destructive">Flagged</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground py-8">
                    No high-value transactions found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
