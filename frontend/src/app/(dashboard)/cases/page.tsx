"use client";

import { useState, useEffect } from "react";
import * as casesService from "@/services/cases";
import type { CrimeIncident } from "@/types";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ExportButton } from "@/components/export/export-dialog";
import { Search } from "lucide-react";

export default function CasesPage() {
  const router = useRouter();
  const [cases, setCases] = useState<CrimeIncident[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const data = await casesService.listCases({
          status: status || undefined,
          page: 1,
          per_page: 50,
        });
        setCases(data);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [status]);

  const filtered = cases.filter((c) =>
    c.description?.toLowerCase().includes(search.toLowerCase()) ||
    c.crime_type?.name?.toLowerCase().includes(search.toLowerCase()) ||
    c.fir_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Cases</h1>
        <p className="text-sm text-muted-foreground">Browse crime cases</p>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search cases..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select value={status || "all"} onValueChange={(v) => { if (v) setStatus(v === "all" ? "" : v); }}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="solved">Solved</SelectItem>
          </SelectContent>
        </Select>
        <ExportButton sessionId="cases-page" />
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="space-y-3 p-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Case ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Injuries</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((c) => (
                  <TableRow
                    key={c.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => router.push(`/cases/${c.id}`)}
                  >
                    <TableCell className="font-mono text-xs">
                      {c.fir_id?.slice(0, 8)}
                    </TableCell>
                    <TableCell>{c.crime_type?.name}</TableCell>
                    <TableCell>
                      {new Date(c.incident_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={c.is_solved ? "default" : "secondary"}
                      >
                        {c.is_solved ? "Solved" : "Open"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {c.injury_count > 0 ? c.injury_count : "-"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
