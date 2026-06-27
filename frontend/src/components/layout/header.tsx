"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { LogOut, Settings, User, Bell, Search } from "lucide-react";
import Link from "next/link";
import { getAlertCounts } from "@/services/alerts";

export function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    getAlertCounts()
      .then((counts) => setAlertCount(counts.total))
      .catch(() => setAlertCount(3)); // fallback
  }, []);

  const initials = user?.full_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-6">
      <div className="flex items-center gap-2">
        <h2 className="text-sm text-muted-foreground">
          SentinelAI Crime Intelligence Platform
        </h2>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => document.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))}
          className="hidden sm:flex items-center gap-2 rounded-md border bg-muted/50 px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent transition-colors"
        >
          <Search className="h-3.5 w-3.5" />
          <span>Search</span>
          <kbd className="pointer-events-none rounded border bg-background px-1.5 py-0.5 font-mono text-[10px]">
            Ctrl+K
          </kbd>
        </button>
        <Link
          href="/alerts"
          className="relative inline-flex items-center justify-center h-8 w-8 rounded-full hover:bg-accent transition-colors"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-destructive text-[9px] font-bold text-white flex items-center justify-center">
            {alertCount > 9 ? "9+" : alertCount}
          </span>
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger className="cursor-pointer rounded-full outline-none">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="text-xs">{initials}</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <div className="px-2 py-1.5">
              <p className="text-sm font-medium">{user?.full_name}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push("/settings")}>
              <User className="h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push("/settings")}>
              <Settings className="h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={handleLogout}
              className="text-destructive focus:text-destructive"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
