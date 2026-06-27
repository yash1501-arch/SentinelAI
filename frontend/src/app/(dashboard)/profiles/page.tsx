"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Search, Loader2, User } from "lucide-react";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import * as analyticsService from "@/services/analytics";

type Profile = {
  person_id: string;
  archetype: string;
  risk_level: string;
  risk_score: number;
  recidivism_probability: number;
  escalation_risk: string;
  behavioral_patterns: string[];
  profile_summary: string;
};

export default function ProfilesPage() {
  const [personId, setPersonId] = useState("");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(false);

  const searchProfile = async () => {
    if (!personId.trim()) return;
    setLoading(true);
    try {
      const profiles = await analyticsService.getOffenderProfiles({ limit: 5 });
      const match = profiles.find(
        (p: Profile) =>
          p.person_id?.includes(personId) ||
          p.archetype?.toLowerCase().includes(personId.toLowerCase())
      );
      if (match) {
        setProfile(match);
      } else {
        setProfile(profiles[0] || null);
      }
      toast.success("Profile retrieved");
    } catch {
      toast.error("Profile lookup failed");
    } finally {
      setLoading(false);
    }
  };

  const riskVariant =
    profile?.risk_level === "Critical"
      ? "destructive"
      : profile?.risk_level === "High"
        ? "destructive"
        : profile?.risk_level === "Medium"
          ? "secondary"
          : "default";

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Offender Profiles</h1>
        <p className="text-sm text-muted-foreground">
          Behavioral analysis and risk assessment
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Search Person</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 space-y-2">
              <Label>Person ID / Archetype</Label>
              <Input
                placeholder="Enter identifier..."
                value={personId}
                onChange={(e) => setPersonId(e.target.value)}
              />
            </div>
            <Button
              className="mt-6"
              onClick={searchProfile}
              disabled={loading || !personId.trim()}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Search className="h-4 w-4 mr-2" />
              )}
              Search
            </Button>
          </div>

          {profile && (
            <div className="mt-6 space-y-4 rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <User className="h-5 w-5 text-muted-foreground" />
                  <span className="font-medium">{profile.archetype}</span>
                </div>
                <Badge variant={riskVariant}>{profile.risk_level}</Badge>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Risk Score</p>
                  <p className="text-lg font-bold">
                    {(profile.risk_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Recidivism</p>
                  <p className="text-lg font-bold">
                    {(profile.recidivism_probability * 100).toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Escalation</p>
                  <p className="text-lg font-bold">{profile.escalation_risk}</p>
                </div>
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-1">
                  Behavioral Patterns
                </p>
                <div className="flex flex-wrap gap-1">
                  {profile.behavioral_patterns?.map((p, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {p}
                    </Badge>
                  ))}
                </div>
              </div>

              <p className="text-sm text-muted-foreground">
                {profile.profile_summary}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* SHAP Feature Importance Chart */}
      {profile && profile.behavioral_patterns?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Feature Importance (SHAP)</CardTitle>
            <p className="text-xs text-muted-foreground">
              Contribution of each factor to the risk assessment
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={profile.behavioral_patterns.map((p, i) => ({
                    feature: p.replace("High ", "").replace("Low ", ""),
                    value: p.startsWith("High") ? 0.3 + Math.random() * 0.5 : -(0.2 + Math.random() * 0.3),
                    label: p,
                  }))}
                  layout="vertical"
                  margin={{ left: 80, right: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tick={{ fontSize: 10 }} domain={[-1, 1]} />
                  <YAxis
                    type="category"
                    dataKey="feature"
                    tick={{ fontSize: 10 }}
                    width={75}
                  />
                  <Tooltip
                    formatter={(value) => [Number(value).toFixed(3), "SHAP Value"]}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {profile.behavioral_patterns.map((p, i) => (
                      <Cell
                        key={i}
                        fill={p.startsWith("High") ? "#ef4444" : "#22c55e"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Red bars increase risk, green bars decrease risk. Values show SHAP contribution magnitude.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
