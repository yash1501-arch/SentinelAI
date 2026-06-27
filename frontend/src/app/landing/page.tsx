"use client";

import Link from "next/link";
import {
  Shield,
  MessageSquare,
  Network,
  BarChart3,
  Map,
  TrendingUp,
  Brain,
  Banknote,
  Users,
  Lock,
  Mic,
  FileText,
  Mail,
  Phone,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero Section */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-950 via-indigo-950 to-slate-950" />
        <div className="relative z-10 max-w-6xl mx-auto px-6 py-20 text-center">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Shield className="h-12 w-12 text-blue-400" />
            <h1 className="text-5xl font-bold text-white tracking-tight">
              SentinelAI
            </h1>
          </div>
          <p className="text-xl text-blue-200 max-w-2xl mx-auto mb-4">
            Intelligent Crime Intelligence & Analytical Platform
          </p>
          <p className="text-sm text-blue-300/80 max-w-xl mx-auto mb-8">
            Connecting Crimes, Predicting Threats, Empowering Investigations
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/login">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
                Launch Platform
              </Button>
            </Link>
            <a href="#features">
              <Button size="lg" variant="outline" className="border-blue-400 text-blue-200 hover:bg-blue-900/50">
                Explore Features
              </Button>
            </a>
          </div>
          <div className="mt-12 flex flex-wrap justify-center gap-3">
            <Badge variant="secondary" className="bg-blue-900/50 text-blue-200">Multi-Agent AI</Badge>
            <Badge variant="secondary" className="bg-blue-900/50 text-blue-200">Neo4j Graph DB</Badge>
            <Badge variant="secondary" className="bg-blue-900/50 text-blue-200">Vector Search</Badge>
            <Badge variant="secondary" className="bg-blue-900/50 text-blue-200">Crime Forecasting</Badge>
            <Badge variant="secondary" className="bg-blue-900/50 text-blue-200">Explainable AI</Badge>
          </div>
        </div>
      </header>

      {/* Problem Statement */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-4">The Challenge</h2>
        <p className="text-center text-muted-foreground max-w-3xl mx-auto mb-10">
          Karnataka State Police maintains extensive crime records but faces critical hurdles
          that prevent effective intelligence-driven policing.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { title: "Data Silos", desc: "Records managed in independent silos, reliant on Excel-based reporting" },
            { title: "No Advanced Analytics", desc: "Absence of AI-driven approaches leaving criminal networks undiscovered" },
            { title: "Information Gaps", desc: "SCRB receives limited, fragmented information for state-wide analysis" },
            { title: "Reactive Policing", desc: "Investigators lack tools for proactive strategies and evidence-based prevention" },
          ].map((item, i) => (
            <Card key={i} className="border-destructive/20 bg-destructive/5">
              <CardContent className="pt-4">
                <h3 className="font-semibold text-sm mb-1">{item.title}</h3>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="bg-muted/30 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-4">Platform Capabilities</h2>
          <p className="text-center text-muted-foreground max-w-2xl mx-auto mb-10">
            10 core modules addressing every aspect of the hackathon challenge
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <Card key={i} className="hover:shadow-lg transition-shadow">
                <CardContent className="pt-5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                      <f.icon className="h-5 w-5 text-primary" />
                    </div>
                    <h3 className="font-semibold text-sm">{f.title}</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-10">Technology Stack</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {techStack.map((group, i) => (
            <Card key={i}>
              <CardContent className="pt-5">
                <h3 className="font-semibold mb-3 text-sm text-primary">{group.category}</h3>
                <div className="flex flex-wrap gap-2">
                  {group.items.map((item, j) => (
                    <Badge key={j} variant="outline" className="text-xs">
                      {item}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Architecture */}
      <section className="bg-muted/30 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-10">Architecture</h2>
          <div className="bg-background rounded-lg border p-6 font-mono text-xs leading-relaxed overflow-x-auto">
            <pre className="whitespace-pre text-muted-foreground">{`
  User Query (English/Kannada/Voice)
         │
  ┌──────▼──────┐
  │  Next.js 15  │  Frontend (TailwindCSS + Shadcn + React Flow + Mapbox)
  └──────┬──────┘
         │ REST API
  ┌──────▼──────┐
  │   FastAPI    │  Backend (Python 3.12 + JWT Auth + Rate Limiting)
  └──────┬──────┘
         │
  ┌──────▼──────────────────────────────────────────┐
  │         LangGraph Multi-Agent Orchestrator       │
  │  Coordinator → SQL │ Graph │ RAG │ Analytics     │
  │                    │ Profiling │ Forecast         │
  │                    └─────────► Summarizer         │
  └──────┬──────────────────────────────────────────┘
         │
  ┌──────▼──────────────────────────────────────────┐
  │  PostgreSQL │ Neo4j Aura │ Qdrant │ Redis        │
  │  (Crimes)   │ (Graph)    │(Vectors)│ (Cache)     │
  └─────────────────────────────────────────────────┘
         │
  ┌──────▼──────────────────────────────────────────┐
  │  ML: Prophet │ XGBoost │ DBSCAN │ SHAP           │
  │  NLP: Sentence Transformers │ Whisper ASR        │
  └─────────────────────────────────────────────────┘
            `}</pre>
          </div>
        </div>
      </section>

      {/* About Me */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-10">About the Creator</h2>
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row items-center gap-6">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-primary text-2xl font-bold">
                  NP
                </div>
                <div className="text-center sm:text-left flex-1">
                  <h3 className="text-xl font-bold">Narayan Parab</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Data Analyst | Frontend Developer | MERN Stack Developer
                  </p>
                  <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                    B.E. in Information Technology from Atharva College of Engineering (2024).
                    Passionate about transforming complex data into actionable insights with a strong
                    foundation in analytics, visualization, and full-stack development.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center sm:justify-start mb-4">
                    <Badge variant="outline">Power BI</Badge>
                    <Badge variant="outline">Python</Badge>
                    <Badge variant="outline">React.js</Badge>
                    <Badge variant="outline">SQL</Badge>
                    <Badge variant="outline">Next.js</Badge>
                    <Badge variant="outline">Data Visualization</Badge>
                  </div>
                  <div className="flex items-center gap-4 justify-center sm:justify-start text-muted-foreground">
                    <a href="mailto:narayanp1501@gmail.com" className="hover:text-primary transition-colors">
                      <Mail className="h-4 w-4" />
                    </a>
                    <a href="tel:9820513298" className="hover:text-primary transition-colors">
                      <Phone className="h-4 w-4" />
                    </a>
                    <span className="text-xs">Mumbai, India</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <p className="text-sm text-muted-foreground">
            SentinelAI — Built for the Karnataka State Police Hackathon 2026
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            © 2026 Narayan Parab. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: MessageSquare,
    title: "1. Conversational AI Interface",
    desc: "Natural language queries in English & Kannada with voice input, context-aware follow-ups, and PDF export of conversations.",
  },
  {
    icon: Network,
    title: "2. Criminal Network Analysis",
    desc: "Neo4j knowledge graph revealing hidden links between suspects, victims, locations, and financial accounts with interactive visualization.",
  },
  {
    icon: BarChart3,
    title: "3. Crime Pattern & Trend Analytics",
    desc: "Spatiotemporal hotspot detection, emerging trend alerts, and statistical analysis across time, geography, and crime type.",
  },
  {
    icon: Users,
    title: "4. Sociological Crime Insights",
    desc: "Correlate crime with urbanization, education, income, and demographics to understand the 'why' behind patterns.",
  },
  {
    icon: Brain,
    title: "5. Offender Profiling (XGBoost + SHAP)",
    desc: "Behavioral analysis, risk scoring, archetype classification, and recidivism prediction with explainable AI reasoning.",
  },
  {
    icon: FileText,
    title: "6. Investigator Decision Support",
    desc: "Automated case summaries, investigation timelines, similar case retrieval, and recommended investigative leads.",
  },
  {
    icon: Banknote,
    title: "7. Financial Crime Intelligence",
    desc: "Money trail analysis, circular transaction detection, Isolation Forest anomaly detection, and suspicious network mapping.",
  },
  {
    icon: TrendingUp,
    title: "8. Crime Forecasting & Early Warning",
    desc: "Prophet-based predictions with confidence intervals, hotspot forecasting, and early warning alerts for gang activity.",
  },
  {
    icon: Brain,
    title: "9. Explainable AI & Transparency",
    desc: "Every answer includes evidence trails, confidence scores, SHAP reasoning chains, and source document references.",
  },
  {
    icon: Lock,
    title: "10. Secure RBAC & Governance",
    desc: "Role-based access for 5 roles, complete audit logging, JWT authentication, and data protection compliance.",
  },
];

const techStack = [
  {
    category: "Frontend",
    items: ["Next.js 15", "TypeScript", "TailwindCSS", "Shadcn/UI", "React Flow", "Recharts", "Mapbox GL"],
  },
  {
    category: "Backend & AI",
    items: ["FastAPI", "Python 3.12", "LangGraph", "LangChain", "OpenAI/Groq", "Whisper ASR"],
  },
  {
    category: "Databases",
    items: ["PostgreSQL", "Neo4j Aura", "Qdrant Cloud", "Redis"],
  },
  {
    category: "ML/NLP Models",
    items: ["Prophet", "XGBoost", "DBSCAN", "Isolation Forest", "SHAP", "Sentence Transformers"],
  },
  {
    category: "DevOps & Cloud",
    items: ["Zoho Catalyst", "Docker", "GitHub Actions", "Alembic"],
  },
  {
    category: "Security",
    items: ["JWT Auth", "bcrypt", "Rate Limiting", "Audit Logging", "TLS 1.3", "RBAC"],
  },
];
