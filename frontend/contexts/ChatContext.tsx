"use client"

import { createContext, useContext, useState, useEffect, useRef, useCallback, ReactNode } from "react"
import { useAuth } from "@/contexts/AuthContext"

const API_URL = "http://localhost:8000"
const STORAGE_KEY = "aria_active_conversation"

export type MessageType = {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  type: "message" | "thinking" | "error" | "connected" | "confirm" | "attachment"
  confirmData?: { action: string; details: string; confirm_id: string }
  attachmentData?: {
    filename: string
    file_type: "document" | "image"
    preview?: string
    userMessage?: string
  }
}

type ChatContextType = {
  conversationId: string | null
  setConversationId: (id: string) => void
  messages: MessageType[]
  isConnected: boolean
  isThinking: boolean
  sendMessage: (message: string) => void
  sendContext: (
    filename: string,
    content: string,
    file_type: "document" | "image",
    preview?: string,
    userMessage?: string,
  ) => void
  sendConfirmation: (confirm_id: string, approved: boolean) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: ReactNode }) {
  const { token } = useAuth()
  const [conversationId, setConversationIdState] = useState<string | null>(null)
  const [messages, setMessages] = useState<MessageType[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isThinking, setIsThinking] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const hasInitialized = useRef(false)

  const setConversationId = useCallback((id: string) => {
    localStorage.setItem(STORAGE_KEY, id)
    setConversationIdState(id)
  }, [])

  // Resolve which conversation to open once we have a token
  useEffect(() => {
    if (!token || hasInitialized.current) return
    hasInitialized.current = true

    const resolve = async () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY)
        if (stored) {
          const check = await fetch(`${API_URL}/api/conversations/${stored}`, {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (check.ok) {
            setConversationIdState(stored)
            return
          }
        }

        const listRes = await fetch(`${API_URL}/api/conversations`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        const list = await listRes.json()

        if (Array.isArray(list) && list.length > 0) {
          localStorage.setItem(STORAGE_KEY, list[0].id)
          setConversationIdState(list[0].id)
          return
        }

        const createRes = await fetch(`${API_URL}/api/conversations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ title: "New conversation" }),
        })
        const created = await createRes.json()
        localStorage.setItem(STORAGE_KEY, created.id)
        setConversationIdState(created.id)
      } catch (err) {
        console.error("Failed to resolve conversation:", err)
        hasInitialized.current = false
      }
    }

    resolve()
  }, [token])

  // Own the websocket connection — lives here, not inside any page component
  useEffect(() => {
    if (!token || !conversationId) return

    let isCancelled = false
    setMessages([])
    setIsConnected(false)

    const loadHistoryAndConnect = async () => {
      try {
        const res = await fetch(`${API_URL}/api/conversations/${conversationId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.ok) {
          const data = await res.json()
          if (!isCancelled && Array.isArray(data.messages)) {
            setMessages(
              data.messages.map((m: any) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                type: "message",
              })),
            )
          }
        }
      } catch (err) {
        console.error("Failed to load conversation history:", err)
      }

      if (isCancelled) return

      const ws = new WebSocket(`ws://localhost:8000/ws/chat/${conversationId}?token=${token}`)
      wsRef.current = ws

      ws.onopen = () => setIsConnected(true)

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === "thinking") {
          setIsThinking(true)
          return
        }
        setIsThinking(false)

        if (data.type === "connected") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: data.message, type: "connected" },
          ])
          return
        }
        if (data.type === "confirm") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: "", type: "confirm", confirmData: data.confirmData },
          ])
          return
        }
        if (data.type === "message") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "assistant", content: data.message, type: "message" },
          ])
          return
        }
        if (data.type === "error") {
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: data.message, type: "error" },
          ])
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
    }

    loadHistoryAndConnect()

    return () => {
      isCancelled = true
      wsRef.current?.close()
    }
  }, [conversationId, token])

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString(), role: "user", content: message, type: "message" },
      ])
      wsRef.current.send(JSON.stringify({ type: "message", message }))
    }
  }, [])

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
        ])
        wsRef.current.send(JSON.stringify({ type: "context", filename, content, file_type }))
      }
    },
    [],
  )

  const sendConfirmation = useCallback((confirm_id: string, approved: boolean) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "confirm_response", confirm_id, approved }))
    }
  }, [])

  return (
    <ChatContext.Provider
      value={{ conversationId, setConversationId, messages, isConnected, isThinking, sendMessage, sendContext, sendConfirmation }}
    >
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error("useChat must be used within ChatProvider")
  return ctx
}