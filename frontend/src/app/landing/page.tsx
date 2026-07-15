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
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* Premium Sticky Navigation */}
      <nav className="sticky top-0 z-50 glass border-b border-slate-900/50 backdrop-blur-md px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-blue-500 animate-pulse" />
            <span className="font-bold text-lg text-white tracking-tight">SentinelAI</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button size="sm" variant="ghost" className="text-slate-300 hover:text-white hover:bg-slate-900/50">
                Log In
              </Button>
            </Link>
            <Link href="/register">
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-md shadow-blue-900/35 transition-all duration-300 hover:scale-[1.02]">
                Register
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative overflow-hidden py-24 sm:py-32 bg-slate-950 bg-grid border-b border-slate-900/30">
        <div className="absolute top-0 -left-10 w-[500px] h-[500px] bg-blue-600/10 rounded-full mix-blend-screen filter blur-3xl opacity-30 animate-pulse-slow" />
        <div className="absolute bottom-0 -right-10 w-[500px] h-[500px] bg-indigo-600/10 rounded-full mix-blend-screen filter blur-3xl opacity-30 animate-pulse-slow" />
        
        <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-6 animate-float">
            <Shield className="h-14 w-14 text-blue-500 filter drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
          </div>
          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-purple-400 mb-6 text-glow">
            SentinelAI
          </h1>
          <p className="text-xl sm:text-2xl text-blue-200/90 max-w-3xl mx-auto mb-4 font-light leading-relaxed">
            Intelligent Crime Analytics & Threat Intelligence Platform
          </p>
          <p className="text-sm sm:text-base text-blue-300/60 max-w-xl mx-auto mb-10">
            Connecting Crimes, Predicting Threats, and Empowering Investigations through Multi-Agent AI
          </p>
          
          <div className="flex items-center justify-center gap-4">
            <Link href="/login">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-6 rounded-xl shadow-lg shadow-blue-900/40 hover:shadow-blue-600/30 hover:scale-[1.03] transition-all duration-300">
                Launch Platform
              </Button>
            </Link>
            <a href="#features">
              <Button size="lg" variant="outline" className="border-slate-800 text-slate-300 hover:text-white hover:bg-slate-900/60 px-8 py-6 rounded-xl transition-all duration-300">
                Explore Features
              </Button>
            </a>
          </div>

          <div className="mt-16 flex flex-wrap justify-center gap-2">
            {["Multi-Agent AI", "Neo4j Graph DB", "Qdrant Vector Search", "DBSCAN Clustering", "Prophet Forecasting", "Explainable SHAP AI"].map((tech, idx) => (
              <Badge key={idx} variant="secondary" className="bg-slate-900/80 hover:bg-slate-800 text-blue-400 border border-slate-800/80 px-3.5 py-1.5 rounded-full text-xs font-medium">
                {tech}
              </Badge>
            ))}
          </div>
        </div>
      </header>

      {/* Problem Statement */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">The Challenge</h2>
          <p className="text-slate-400 leading-relaxed">
            Modern police departments handle massive datasets but face core structural hurdles that prevent pro-active, intelligence-driven operations.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { title: "Data Silos", desc: "Records are fragmented in independent databases, limiting comprehensive queries." },
            { title: "Manual Network Building", desc: "Absence of automated link analysis prevents discovering nested gang networks." },
            { title: "Information Gaps", desc: "Supervisors receive delayed reports, delaying critical inter-district investigations." },
            { title: "Reactive Response", desc: "Lack of predictive forecasting models leaves policing reactive rather than preventive." },
          ].map((item, i) => (
            <Card key={i} className="border-red-950/20 bg-red-950/5 hover:border-red-900/40 hover:bg-red-950/10 transition-all duration-300 shadow-md">
              <CardContent className="pt-6">
                <div className="h-2 w-10 bg-red-600 rounded-full mb-4" />
                <h3 className="font-bold text-white text-base mb-2">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="bg-slate-950/60 border-y border-slate-900/40 py-20 relative">
        <div className="absolute inset-0 bg-grid opacity-20 pointer-events-none" />
        <div className="max-w-6xl mx-auto px-6 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">Platform Capabilities</h2>
            <p className="text-slate-400">
              Ten intelligent modules designed to target every dimension of crime data analysis.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <Card key={i} className="bg-slate-900/40 border-slate-900/80 hover:border-blue-900/60 hover:bg-slate-900/80 hover:-translate-y-1 transition-all duration-300 shadow-lg shadow-slate-950/40">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3.5 mb-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-950/50 border border-blue-900/30 text-blue-400 shadow-inner">
                      <f.icon className="h-5 w-5" />
                    </div>
                    <h3 className="font-bold text-slate-200 text-sm">{f.title}</h3>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">Technology Stack</h2>
          <p className="text-slate-400">
            A state-of-the-art tech ecosystem built for performance, intelligence, and safety.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {techStack.map((group, i) => (
            <Card key={i} className="bg-slate-900/20 border-slate-900/60 shadow-md">
              <CardContent className="pt-6">
                <h3 className="font-bold mb-4 text-sm text-blue-400 tracking-wider uppercase">{group.category}</h3>
                <div className="flex flex-wrap gap-2">
                  {group.items.map((item, j) => (
                    <Badge key={j} variant="outline" className="text-xs bg-slate-950/60 border-slate-800 text-slate-300 font-normal px-2.5 py-1">
                      {item}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Architecture Diagram */}
      <section className="bg-slate-950/60 border-t border-slate-900/40 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">Architecture</h2>
            <p className="text-slate-400">
              Scalable system flow displaying frontend user requests passing through LangGraph orchestration to core datastores.
            </p>
          </div>
          <div className="bg-slate-900/40 border border-slate-900 rounded-2xl p-6 sm:p-8 font-mono text-[11px] sm:text-xs leading-relaxed overflow-x-auto shadow-2xl">
            <pre className="whitespace-pre text-blue-400/80">{`
  User Query (English/Kannada/Voice)
         │
  ┌──────▼──────┐
  │  Next.js 15  │  Frontend (TypeScript + React Flow + Recharts)
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
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">About the Creator</h2>
        </div>
        <div className="max-w-3xl mx-auto">
          <Card className="bg-gradient-to-br from-slate-900/60 to-slate-950 border-slate-900 overflow-hidden shadow-2xl relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full filter blur-xl" />
            <CardContent className="pt-8 pb-8 px-6 sm:px-10">
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl bg-blue-600/10 border border-blue-900/30 text-blue-400 text-3xl font-extrabold shadow-inner shadow-blue-500/5">
                  NP
                </div>
                <div className="text-center md:text-left flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                    <h3 className="text-2xl font-bold text-white">Narayan Parab</h3>
                    <div className="flex items-center gap-3 justify-center text-slate-400">
                      <a href="mailto:narayanp1501@gmail.com" className="hover:text-blue-400 transition-colors" title="Email Narayan">
                        <Mail className="h-5 w-5" />
                      </a>
                      <a href="tel:9820513298" className="hover:text-blue-400 transition-colors" title="Call Narayan">
                        <Phone className="h-5 w-5" />
                      </a>
                      <span className="text-xs bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800">Mumbai, India</span>
                    </div>
                  </div>
                  <p className="text-sm text-blue-400 font-medium mb-4">
                    Data Analyst | Frontend Developer | MERN Stack Developer
                  </p>
                  <p className="text-xs sm:text-sm text-slate-400 leading-relaxed mb-6">
                    B.E. in Information Technology from Atharva College of Engineering (2024).
                    Passionate about transforming complex datasets into clear, actionable intelligence frameworks. Combining deep analytical models with highly polished visual interfaces to empower teams and optimize investigations.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                    {["Power BI", "Python", "React.js", "SQL", "Next.js", "Data Visualization", "LangGraph", "Docker"].map((skill, sIdx) => (
                      <Badge key={sIdx} variant="secondary" className="bg-slate-950 border border-slate-900 text-slate-400 text-xs font-normal">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-950 bg-slate-950/80 py-10">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <p className="text-sm text-slate-400">
            SentinelAI — Developed for the Karnataka State Police Hackathon 2026
          </p>
          <p className="text-xs text-slate-500 mt-2">
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
