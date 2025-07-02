import React, { useState, useCallback } from "react";
import { v4 as uuid } from "uuid";
import { ChatWidget, Message } from "./ChatWidget";

type ChatResponse = {
  answer?: string;
  reply?: string;
  response?: string;
  status?: string;
  error?: string;
  metadata?: {
    model?: string;
    latency_ms?: number;
    token_count?: number;
    session_id?: string;
  };
};

// Utöka ImportMeta-typen för att stödja Vite-miljövariabler
declare global {
  interface ImportMeta {
    env: Record<string, string>;
  }
}

/**
 * Example implementation av ChatWidget med backend-integration.
 * Demonstrerar hur man kan integrera med AZOM AI Agent API.
 */
const ChatWidgetExample: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [typing, setTyping] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Skickar meddelande till backend och hanterar svaret.
   * 
   * @param text - Användarens meddelande
   */
  const handleSendMessage = useCallback(async (text: string): Promise<void> => {
    // Lägg till användarens meddelande i chatt-historiken
    const userMessageId = uuid();
    
    setMessages((prev) => [
      ...prev,
      {
        id: userMessageId,
        text,
        sender: "user",
        timestamp: new Date(),
        status: "sent",
      },
    ]);
    
    // Visa typing-indikator
    setTyping(true);
    setError(null);
    
    try {
      // Hämta API-basurl från environment eller använd default
      const apiBaseUrl = import.meta.env.VITE_API_URL || '';
      const chatEndpoint = `${apiBaseUrl}/chat/azom`;
      
      const res = await fetch(chatEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          message: text,
          session_id: localStorage.getItem("azom_session_id") || uuid() 
        }),
      });
      
      if (!res.ok) {
        throw new Error(`Server svarade med ${res.status}: ${res.statusText}`);
      }
      
      const data: ChatResponse = await res.json();
      
      // Spara session-ID om den finns i svaret
      if (data.metadata?.session_id) {
        localStorage.setItem("azom_session_id", data.metadata.session_id);
      }
      
      // Hitta svarstext från olika möjliga fält i API-svaret
      const responseText = data.answer ?? data.reply ?? data.response ?? "(Inget svar från servern)";
      
      setMessages((prev) => [
        ...prev,
        {
          id: uuid(),
          text: responseText,
          sender: "bot",
          timestamp: new Date(),
          status: "sent",
          senderName: "AZOM",
        },
      ]);
      
      // Logga metadata för diagnostik (endast i utvecklingsmode)
      if (import.meta.env.DEV && data.metadata) {
        console.log("Chat response metadata:", data.metadata);
      }
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "Oväntat fel vid anslutning till servern";
      setError(errorMessage);
      
      setMessages((prev) => [
        ...prev,
        {
          id: uuid(),
          text: "Kunde inte ansluta till AZOM servern. Vänligen försök igen senare.",
          sender: "bot",
          timestamp: new Date(),
          status: "failed",
        },
      ]);
      
      // Logga felet för diagnostik
      console.error("Chat error:", e);
    } finally {
      setTyping(false);
    }
  }, []);

  return (
    <div className="flex flex-col w-full max-w-2xl">
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-800 rounded">
          {error}
        </div>
      )}
      
      <ChatWidget
        messages={messages}
        onSendMessage={handleSendMessage}
        showTypingIndicator={typing}
        height="500px"
        className="w-full shadow-lg"
        placeholder="Ställ en fråga om AZOM installation..."
      />
      
      <div className="mt-2 text-xs text-gray-500 text-center">
        AZOM AI Agent v1.0 | Powered by OpenWebUI
      </div>
    </div>
  );
};

export default ChatWidgetExample;
