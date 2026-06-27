"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";
import {
  Bot,
  BarChart3,
  Map,
  Share2,
  FileSearch,
  TrendingUp,
  User,
  Shield,
  Settings,
  Timeline,
  ChevronLeft,
  Bell,
  Banknote,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useState } from "react";

type NavItem = {
  label: string;
  href: string;
  icon: React.ElementType;
  roles: string[];
};

const navItems: NavItem[] = [
  {
    label: "AI Chat",
    href: "/chat",
    icon: Bot,
    roles: ["investigator", "analyst", "supervisor", "policymaker", "admin"],
  },
  {
    label: "Cases",
    href: "/cases",
    icon: FileSearch,
    roles: ["investigator", "analyst", "supervisor", "policymaker", "admin"],
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    roles: ["analyst", "supervisor", "policymaker", "admin"],
  },
  {
    label: "Map",
    href: "/map",
    icon: Map,
    roles: ["analyst", "supervisor", "policymaker", "admin"],
  },
  {
    label: "Network",
    href: "/network",
    icon: Share2,
    roles: ["investigator", "analyst", "supervisor", "admin"],
  },
  {
    label: "Forecasting",
    href: "/forecasting",
    icon: TrendingUp,
    roles: ["analyst", "supervisor", "policymaker", "admin"],
  },
  {
    label: "Financial",
    href: "/financial",
    icon: Banknote,
    roles: ["analyst", "supervisor", "admin"],
  },
  {
    label: "Profiles",
    href: "/profiles",
    icon: User,
    roles: ["investigator", "analyst", "supervisor", "admin"],
  },
  {
    label: "Alerts",
    href: "/alerts",
    icon: Bell,
    roles: ["investigator", "analyst", "supervisor", "policymaker", "admin"],
  },
  {
    label: "Timeline",
    href: "/timeline",
    icon: Timeline,
    roles: ["investigator", "analyst", "supervisor", "admin"],
  },
  {
    label: "Admin",
    href: "/admin",
    icon: Shield,
    roles: ["admin", "supervisor"],
  },
  {
    label: "Settings",
    href: "/settings",
    icon: Settings,
    roles: ["investigator", "analyst", "supervisor", "policymaker", "admin"],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const [collapsed, setCollapsed] = useState(false);

  const userRoles = user?.roles?.map((r) => r.name) ?? [];
  const visible = navItems.filter(
    (item) =>
      !item.roles.length ||
      item.roles.some((r) => userRoles.includes(r))
  );

  const initials = user?.full_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <aside
      className={cn(
        "flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex items-center justify-between p-4">
        {!collapsed && (
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <Shield className="h-6 w-6 text-primary" />
            <span>SentinelAI</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/" className="mx-auto">
            <Shield className="h-6 w-6 text-primary" />
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          className={cn("h-6 w-6", collapsed && "mx-auto mt-2")}
          onClick={() => setCollapsed(!collapsed)}
        >
          <ChevronLeft
            className={cn(
              "h-4 w-4 transition-transform",
              collapsed && "rotate-180"
            )}
          />
        </Button>
      </div>

      <Separator />

      <ScrollArea className="flex-1 px-2 py-2">
        <nav className="flex flex-col gap-1">
          {visible.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </ScrollArea>

      <Separator />

      <div className="p-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs">{initials}</AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">
                {user?.full_name}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {user?.roles?.[0]?.name ?? "User"}
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
