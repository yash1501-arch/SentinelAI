"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Global keyboard shortcuts for SentinelAI.
 *
 * Ctrl+K / Cmd+K: Command palette (handled by CommandPalette component)
 * Ctrl+/ : Focus chat input
 * Ctrl+Shift+N: New chat session
 * Ctrl+Shift+E: Export current view
 */
export function useGlobalShortcuts() {
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+/ → Navigate to chat
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault();
        router.push("/chat");
      }

      // Ctrl+Shift+N → New chat
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "N") {
        e.preventDefault();
        router.push("/chat?new=true");
      }

      // Ctrl+Shift+D → Dashboard
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "D") {
        e.preventDefault();
        router.push("/");
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [router]);
}
