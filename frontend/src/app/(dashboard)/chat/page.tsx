"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import { Send, Loader2, Plus, History, ChevronDown, ChevronUp, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { toast } from "sonner";
import * as chatService from "@/services/chat";
import type { ConversationResponse } from "@/types";
import { useAuthStore } from "@/store/auth";
import ReactMarkdown from "react-markdown";
import { Visualizations } from "@/components/chat/visualizations";
import { VoiceRecorder } from "@/components/chat/voice-recorder";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  visualizations?: ConversationResponse["visualizations"];
  sources?: ConversationResponse["sources"];
  confidence?: number;
  processing_time_ms?: number;
  reasoning_chain?: string[];
  tokens_used?: number;
  loading?: boolean;
};

function getSessionId() {
  let id = localStorage.getItem("chat_session_id");
  if (!id) {
    id = uuidv4();
    localStorage.setItem("chat_session_id", id);
  }
  return id;
}

function listSessions(): string[] {
  try {
    return JSON.parse(localStorage.getItem("chat_sessions") || "[]");
  } catch {
    return [];
  }
}

function saveSession(id: string) {
  const sessions = listSessions();
  if (!sessions.includes(id)) {
    sessions.unshift(id);
    localStorage.setItem("chat_sessions", JSON.stringify(sessions.slice(0, 20)));
  }
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId, setSessionId] = useState(getSessionId());
  const scrollRef = useRef<HTMLDivElement>(null);
  const user = useAuthStore((s) => s.user);
  const sessions = listSessions();

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  const newSession = useCallback(() => {
    const id = uuidv4();
    localStorage.setItem("chat_session_id", id);
    setSessionId(id);
    setMessages([]);
  }, []);

  const loadSession = useCallback(async (sid: string) => {
    localStorage.setItem("chat_session_id", sid);
    setSessionId(sid);
    try {
      await chatService.getHistory(sid);
    } catch {
      // history may not exist
    }
    setMessages([]);
  }, []);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    const userMsg: Message = { id: uuidv4(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    const loadingId = uuidv4();
    const loadingMsg: Message = { id: loadingId, role: "assistant", content: "", loading: true };
    setMessages((prev) => [...prev, loadingMsg]);
    setSending(true);

    try {
      saveSession(sessionId);
      const data = await chatService.converse({
        session_id: sessionId,
        message: text,
        language: user?.preferred_language || "en",
      });

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== loadingId),
        {
          id: uuidv4(),
          role: "assistant",
          content: data.reply,
          visualizations: data.visualizations ?? undefined,
          sources: data.sources ?? undefined,
          confidence: data.confidence_score ?? undefined,
          processing_time_ms: data.processing_time_ms ?? undefined,
          reasoning_chain: data.reasoning_chain ?? undefined,
        },
      ]);
    } catch {
      toast.error("Failed to get response");
      setMessages((prev) => prev.filter((m) => m.id !== loadingId));
    } finally {
      setSending(false);
    }
  }, [input, sending, sessionId, user?.preferred_language]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTranscript = (text: string) => {
    setInput((prev) => (prev ? `${prev} ${text}` : text));
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">AI Chat</h1>
          <p className="text-sm text-muted-foreground">
            Ask questions in English or Kannada
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Sheet>
            <SheetTrigger className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 border border-input bg-background shadow-xs hover:bg-accent hover:text-accent-foreground h-8 px-3">
              <History className="h-4 w-4" />
              History
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Conversations</SheetTitle>
              </SheetHeader>
              <div className="mt-4 space-y-2">
                {sessions.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No previous sessions</p>
                ) : (
                  sessions.map((sid) => (
                    <Button
                      key={sid}
                      variant={sid === sessionId ? "secondary" : "ghost"}
                      className="w-full justify-start text-xs font-mono truncate"
                      onClick={() => loadSession(sid)}
                    >
                      {sid.slice(0, 8)}...
                    </Button>
                  ))
                )}
              </div>
            </SheetContent>
          </Sheet>
          <Button variant="outline" size="sm" onClick={newSession}>
            <Plus className="h-4 w-4 mr-2" />
            New
          </Button>
        </div>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden">
        <ScrollArea ref={scrollRef} className="flex-1 p-4">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center min-h-[300px]">
              <div className="text-center max-w-md">
                <h3 className="text-lg font-semibold mb-2">
                  How can I help you investigate?
                </h3>
                <p className="text-sm text-muted-foreground">
                  Ask about case statistics, crime trends, suspect connections,
                  or offender profiles. Supports English and Kannada.
                </p>
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  {[
                    "Show crime trends this quarter",
                    "Find similar cases to FIR-2024-123",
                    "Profile suspect Rajesh Kumar",
                    "Predict next month's hotspots",
                  ].map((q) => (
                    <Button
                      key={q}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => {
                        setInput(q);
                      }}
                    >
                      {q}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg px-4 py-2 ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  {msg.loading ? (
                    <div className="space-y-2 py-1">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="inline-block h-2 w-2 rounded-full bg-primary animate-pulse" />
                        Analyzing your query...
                      </div>
                      <Skeleton className="h-4 w-48" />
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-40" />
                    </div>
                  ) : (
                    <>
                      <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>

                      {msg.visualizations && (
                        <Visualizations visualizations={msg.visualizations} />
                      )}

                      {(msg.sources?.length ?? 0) > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {msg.sources?.map((s, i) => (
                            <Badge key={i} variant="outline" className="text-[10px]">
                              {s.type}: {s.detail?.slice(0, 40)}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {msg.confidence !== undefined && (
                        <p className="mt-1 text-[10px] text-muted-foreground">
                          Confidence: {(msg.confidence * 100).toFixed(0)}%
                        </p>
                      )}

                      {msg.processing_time_ms && (
                        <p className="text-[10px] text-muted-foreground">
                          Processed in {msg.processing_time_ms}ms
                        </p>
                      )}

                      {msg.reasoning_chain && msg.reasoning_chain.length > 0 && (
                        <ReasoningChain steps={msg.reasoning_chain} />
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <Separator />

        <div className="flex items-center gap-2 p-4">
          <VoiceRecorder onTranscript={handleTranscript} language={user?.preferred_language || "en"} />
          <Input
            placeholder="Type your question (English or Kannada)..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={sending}
          />
          <Button size="icon" onClick={sendMessage} disabled={!input.trim() || sending}>
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
}

function ReasoningChain({ steps }: { steps: string[] }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-2 border-t pt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-[11px] text-muted-foreground hover:text-foreground transition-colors"
      >
        <Brain className="h-3 w-3" />
        <span>Agent Reasoning ({steps.length} steps)</span>
        {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>
      {expanded && (
        <div className="mt-1.5 space-y-1 pl-3 border-l-2 border-primary/30">
          {steps.map((step, i) => (
            <p key={i} className="text-[11px] text-muted-foreground leading-relaxed">
              <span className="font-medium text-primary">{i + 1}.</span> {step}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
