import { useState, useEffect, useRef, useCallback } from "react";

export type MessageType = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  type:
    | "message"
    | "thinking"
    | "error"
    | "connected"
    | "confirm"
    | "attachment";
  confirmData?: {
    action: string;
    details: string;
    confirm_id: string;
  };
  attachmentData?: {
    filename: string;
    file_type: "document" | "image";
    preview?: string;
    userMessage?: string;
  };
};

export function useWebSocket(sessionId: string, token: string) {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let isCancelled = false;
    setMessages([]);
    setIsConnected(false);

    const loadHistoryAndConnect = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/conversations/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          if (!isCancelled && Array.isArray(data.messages)) {
            setMessages(
              data.messages.map((m: any) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                type: "message",
              }))
            );
          }
        }
      } catch (err) {
        console.error("Failed to load conversation history:", err);
      }

      if (isCancelled) return;

      const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => setIsConnected(true);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "thinking") {
          setIsThinking(true);
          return;
        }

        setIsThinking(false);

        if (data.type === "connected") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: data.message, type: "connected" },
          ]);
          return;
        }

        if (data.type === "confirm") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: "", type: "confirm", confirmData: data.confirmData },
          ]);
          return;
        }

        if (data.type === "message") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "assistant", content: data.message, type: "message" },
          ]);
          return;
        }

        if (data.type === "error") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: data.message, type: "error" },
          ]);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsThinking(false);
      };
      ws.onerror = () => {
        setIsConnected(false);
        setIsThinking(false);
      };
    };

    loadHistoryAndConnect();

    return () => {
      isCancelled = true;
      wsRef.current?.close();
    };
  }, [sessionId, token]);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString(), role: "user", content: message, type: "message" },
      ]);
      wsRef.current.send(JSON.stringify({ type: "message", message }));
    }
  }, []);

  const sendContext = useCallback(
    (filename: string, content: string, file_type: "document" | "image", preview?: string, userMessage?: string) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "user" as const,
            content: "",
            type: "attachment" as const,
            attachmentData: { filename, file_type, preview, userMessage },
          },
        ]);
        wsRef.current.send(JSON.stringify({ type: "context", filename, content, file_type }));
      }
    },
    [],
  );

  const sendConfirmation = useCallback((confirm_id: string, approved: boolean) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "confirm_response", confirm_id, approved }));
    }
  }, []);

  return { messages, isConnected, isThinking, sendMessage, sendContext, sendConfirmation };
}