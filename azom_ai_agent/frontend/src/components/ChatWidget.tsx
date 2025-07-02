import React, { useEffect, useRef, useState } from "react";
import { Send, Loader2, User, AlertCircle } from "lucide-react";
import clsx from "clsx";
import { v4 as uuid } from "uuid";

/*
 * NOTE: This component relies on shadcn/ui primitives.
 *   Install them (inside frontend/) via for example:
 *   npx shadcn@latest add button input avatar badge alert scroll-area
 */
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Alert } from "@/components/ui/Alert";
import { ScrollArea } from "@/components/ui/ScrollArea";

export interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  status: "sending" | "sent" | "failed";
  senderName?: string;
}

export interface ChatWidgetProps {
  messages?: Message[];
  onSendMessage?: (text: string) => Promise<void>;
  placeholder?: string;
  maxLength?: number;
  showTypingIndicator?: boolean;
  height?: string;
  className?: string;
}

const TypingIndicator: React.FC = () => (
  <div className="flex items-center space-x-2 p-3 bg-muted/50 rounded-lg animate-pulse">
    <Avatar className="h-6 w-6">
      <div className="h-full w-full bg-primary/20 rounded-full flex items-center justify-center">
        <User className="h-3 w-3 text-primary" />
      </div>
    </Avatar>
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
      <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
      <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
    </div>
  </div>
);

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  messages: initial = [],
  onSendMessage,
  placeholder = "Skriv ett meddelande...",
  maxLength = 500,
  showTypingIndicator = false,
  height = "400px",
  className,
}) => {
  const [messages, setMessages] = useState<Message[]>(initial);
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);

  // auto-scroll
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, showTypingIndicator]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;
    setInput("");

    const tempMsg: Message = {
      id: uuid(),
      text,
      sender: "user",
      timestamp: new Date(),
      status: "sending",
    };
    setMessages((prev) => [...prev, tempMsg]);

    if (onSendMessage) {
      try {
        await onSendMessage(text);
        setMessages((prev) => prev.map((m) => (m.id === tempMsg.id ? { ...m, status: "sent" } : m)));
      } catch (e) {
        setMessages((prev) => prev.map((m) => (m.id === tempMsg.id ? { ...m, status: "failed" } : m)));
      }
    }
  };

  return (
    <div className={clsx("flex flex-col border rounded-lg bg-background", className)} style={{ height }}>
      {/* messages */}
      <ScrollArea className="flex-1 p-4" ref={listRef as any}>
        {messages.map((m) => (
          <div key={m.id} className={clsx("mb-3 flex", m.sender === "user" ? "justify-end" : "justify-start")}>
            {m.sender === "bot" && (
              <Avatar className="mr-2 h-8 w-8">
                <User className="h-4 w-4" />
              </Avatar>
            )}
            <div>
              <div
                className={clsx(
                  "px-3 py-2 rounded-lg text-sm whitespace-pre-wrap",
                  m.sender === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                )}
              >
                {m.text}
              </div>
              <div className="flex items-center space-x-1 text-xs text-muted-foreground mt-0.5">
                <span>{m.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                {m.status === "sending" && <Loader2 className="h-3 w-3 animate-spin" />}
                {m.status === "failed" && <AlertCircle className="h-3 w-3 text-destructive" />}
              </div>
            </div>
          </div>
        ))}
        {showTypingIndicator && <TypingIndicator />}
      </ScrollArea>

      {/* input */}
      <div className="border-t p-3 flex items-center space-x-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={placeholder}
          maxLength={maxLength}
          className="flex-1"
        />
        <Button size="icon" variant="secondary" onClick={handleSend} disabled={!input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

