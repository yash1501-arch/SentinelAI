"use client";

import { useState } from "react";
import * as networkService from "@/services/network";
import type { NetworkResponse, NetworkQuery } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Loader2, Search } from "lucide-react";
import { toast } from "sonner";
import { NetworkGraph, NetworkStats } from "@/components/network/network-graph";

export default function NetworkPage() {
  const [query, setQuery] = useState<NetworkQuery>({
    person_id: "",
    case_id: "",
    depth: 2,
  });
  const [data, setData] = useState<NetworkResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    try {
      const payload: NetworkQuery = { depth: query.depth };
      if (query.person_id?.trim()) payload.person_id = query.person_id;
      if (query.case_id?.trim()) payload.case_id = query.case_id;

      const result = await networkService.analyzeNetwork(payload);
      setData(result);
    } catch {
      toast.error("Network analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Network Analysis</h1>
        <p className="text-sm text-muted-foreground">
          Visualize criminal connections with interactive graph
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Search Network</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <Label>Person ID</Label>
              <Input
                placeholder="Person ID"
                value={query.person_id || ""}
                onChange={(e) =>
                  setQuery({ ...query, person_id: e.target.value || "" })
                }
              />
            </div>
            <div className="space-y-2">
              <Label>Case ID</Label>
              <Input
                placeholder="Case ID"
                value={query.case_id || ""}
                onChange={(e) =>
                  setQuery({ ...query, case_id: e.target.value || "" })
                }
              />
            </div>
            <div className="space-y-2">
              <Label>Depth (1-6)</Label>
              <Input
                type="number"
                min={1}
                max={6}
                value={query.depth}
                onChange={(e) =>
                  setQuery({ ...query, depth: Math.min(6, Math.max(1, parseInt(e.target.value) || 2)) })
                }
              />
            </div>
            <div className="flex items-end">
              <Button onClick={analyze} disabled={loading} className="w-full">
                {loading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Search className="h-4 w-4 mr-2" />
                )}
                Analyze
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {data && (
        <div className="space-y-4">
          <NetworkStats data={data} />
          <Card>
            <CardContent className="p-4">
              <NetworkGraph data={data} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
