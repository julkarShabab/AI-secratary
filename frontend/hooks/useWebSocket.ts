import { useState, useEffect, useRef, useCallback } from "react"

export type MessageType = {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  type: "message" | "thinking" | "error" | "connected" | "confirm"
  confirmData?: {
    action: string
    details: string
    confirm_id: string
  }
}

export function useWebSocket(sessionId: string) {
  const [messages, setMessages] = useState<MessageType[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isThinking, setIsThinking] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === "thinking") {
        setIsThinking(true)
        return
      }

      setIsThinking(false)

      if (data.type === "connected") {
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: "system",
          content: data.message,
          type: "connected"
        }])
        return
      }

      if (data.type === "confirm") {
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: "system",
          content: "",
          type: "confirm",
          confirmData: data.confirmData
        }])
        return
      }

      if (data.type === "message") {
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: "assistant",
          content: data.message,
          type: "message"
        }])
        return
      }

      if (data.type === "error") {
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: "system",
          content: data.message,
          type: "error"
        }])
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
      setIsThinking(false)
    }

    ws.onerror = () => {
      setIsConnected(false)
      setIsThinking(false)
    }

    return () => {
      ws.close()
    }
  }, [sessionId])

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: "user",
        content: message,
        type: "message"
      }])
      wsRef.current.send(JSON.stringify({ message }))
    }
  }, [])

  const sendConfirmation = useCallback((confirm_id: string, approved: boolean) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "confirm_response",
        confirm_id,
        approved
      }))
    }
  }, [])

  return { messages, isConnected, isThinking, sendMessage, sendConfirmation }
}