import React, { useState } from "react";
import { v4 as uuid } from "uuid";
import { ChatWidget, Message } from "./ChatWidget";

const ChatWidgetExample: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [typing, setTyping] = useState(false);

  const handleSendMessage = async (text: string) => {
    // Send to backend
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        text,
        sender: "user",
        timestamp: new Date(),
        status: "sent",
      },
    ]);
    setTyping(true);
    try {
      const res = await fetch("/chat/azom", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          id: uuid(),
          text: data.answer ?? data.reply ?? data.response ?? "(inget svar)",
          sender: "bot",
          timestamp: new Date(),
          status: "sent",
          senderName: "Agent",
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: uuid(),
          text: "Fel vid anslutning till server.",
          sender: "bot",
          timestamp: new Date(),
          status: "failed",
        },
      ]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <ChatWidget
      messages={messages}
      onSendMessage={handleSendMessage}
      showTypingIndicator={typing}
      height="500px"
      className="w-full max-w-md shadow-lg"
    />
  );
};

export default ChatWidgetExample;
