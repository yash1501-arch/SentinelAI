"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  MessageSquare,
  BarChart3,
  Map,
  Network,
  TrendingUp,
  Shield,
  FileText,
  Settings,
  Users,
  Bell,
  Clock,
  Search,
} from "lucide-react";

interface CommandItem {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  keywords: string[];
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();

  const commands: CommandItem[] = [
    {
      id: "chat",
      label: "AI Chat",
      description: "Open conversational AI interface",
      icon: <MessageSquare className="h-4 w-4" />,
      action: () => router.push("/chat"),
      keywords: ["chat", "ai", "ask", "query", "converse"],
    },
    {
      id: "analytics",
      label: "Analytics",
      description: "Crime trends and statistics",
      icon: <BarChart3 className="h-4 w-4" />,
      action: () => router.push("/analytics"),
      keywords: ["analytics", "trends", "statistics", "charts"],
    },
    {
      id: "map",
      label: "Crime Map",
      description: "Geospatial hotspot visualization",
      icon: <Map className="h-4 w-4" />,
      action: () => router.push("/map"),
      keywords: ["map", "hotspot", "location", "geo"],
    },
    {
      id: "network",
      label: "Network Graph",
      description: "Criminal network analysis",
      icon: <Network className="h-4 w-4" />,
      action: () => router.push("/network"),
      keywords: ["network", "graph", "connections", "relationships"],
    },
    {
      id: "forecasting",
      label: "Forecasting",
      description: "Crime predictions and forecasts",
      icon: <TrendingUp className="h-4 w-4" />,
      action: () => router.push("/forecasting"),
      keywords: ["forecast", "predict", "future", "prophet"],
    },
    {
      id: "cases",
      label: "Cases",
      description: "Browse and search crime cases",
      icon: <FileText className="h-4 w-4" />,
      action: () => router.push("/cases"),
      keywords: ["cases", "fir", "incidents", "crimes"],
    },
    {
      id: "profiles",
      label: "Offender Profiles",
      description: "Behavioral profiling and risk scores",
      icon: <Shield className="h-4 w-4" />,
      action: () => router.push("/profiles"),
      keywords: ["profiles", "offender", "risk", "profiling"],
    },
    {
      id: "alerts",
      label: "Alerts",
      description: "Smart alerts and notifications",
      icon: <Bell className="h-4 w-4" />,
      action: () => router.push("/alerts"),
      keywords: ["alerts", "notifications", "warnings"],
    },
    {
      id: "timeline",
      label: "Timeline",
      description: "Case timeline view",
      icon: <Clock className="h-4 w-4" />,
      action: () => router.push("/timeline"),
      keywords: ["timeline", "history", "events"],
    },
    {
      id: "admin",
      label: "Admin Panel",
      description: "User management and system settings",
      icon: <Users className="h-4 w-4" />,
      action: () => router.push("/admin"),
      keywords: ["admin", "users", "manage", "settings"],
    },
    {
      id: "settings",
      label: "Settings",
      description: "Application settings",
      icon: <Settings className="h-4 w-4" />,
      action: () => router.push("/settings"),
      keywords: ["settings", "preferences", "config"],
    },
  ];

  const filteredCommands = commands.filter((cmd) => {
    if (!query) return true;
    const q = query.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(q) ||
      cmd.description.toLowerCase().includes(q) ||
      cmd.keywords.some((k) => k.includes(q))
    );
  });

  // Global keyboard shortcut: Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
        setQuery("");
        setSelectedIndex(0);
      }
      // Escape to close
      if (e.key === "Escape" && open) {
        setOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  // Navigate with arrow keys
  const handleKeyNavigation = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredCommands.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : filteredCommands.length - 1
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action();
          setOpen(false);
        }
      }
    },
    [filteredCommands, selectedIndex]
  );

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-w-lg p-0 gap-0 overflow-hidden">
        <DialogHeader className="sr-only">
          <DialogTitle>Command Palette</DialogTitle>
        </DialogHeader>
        <div className="flex items-center border-b px-3">
          <Search className="h-4 w-4 shrink-0 opacity-50" />
          <Input
            placeholder="Search commands..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyNavigation}
            className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            autoFocus
          />
          <kbd className="pointer-events-none h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 hidden sm:inline-flex">
            ESC
          </kbd>
        </div>
        <div className="max-h-80 overflow-y-auto p-2">
          {filteredCommands.length === 0 && (
            <p className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </p>
          )}
          {filteredCommands.map((cmd, index) => (
            <button
              key={cmd.id}
              onClick={() => {
                cmd.action();
                setOpen(false);
              }}
              className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                index === selectedIndex
                  ? "bg-accent text-accent-foreground"
                  : "hover:bg-accent/50"
              }`}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-md border bg-background">
                {cmd.icon}
              </span>
              <div className="flex flex-col items-start">
                <span className="font-medium">{cmd.label}</span>
                <span className="text-xs text-muted-foreground">
                  {cmd.description}
                </span>
              </div>
            </button>
          ))}
        </div>
        <div className="border-t px-3 py-2 text-xs text-muted-foreground flex items-center gap-4">
          <span>
            <kbd className="rounded border px-1">↑↓</kbd> Navigate
          </span>
          <span>
            <kbd className="rounded border px-1">↵</kbd> Open
          </span>
          <span>
            <kbd className="rounded border px-1">Esc</kbd> Close
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
