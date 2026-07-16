"use client"

import { createContext, useContext, useState, useEffect, useRef, useCallback, ReactNode } from "react"
import { useAuth } from "@/contexts/AuthContext"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || API_URL.replace(/^http/, "ws")
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
  const [messagesByConversation, setMessagesByConversation] = useState<Record<string, MessageType[]>>({})
  const [loadedConversations, setLoadedConversations] = useState<Set<string>>(new Set())
  const [isConnected, setIsConnected] = useState(false)
  const [thinkingSet, setThinkingSet] = useState<Set<string>>(new Set())
  const wsRef = useRef<WebSocket | null>(null)
  const hasInitialized = useRef(false)

  const appendMessage = useCallback((convId: string, msg: MessageType) => {
    setMessagesByConversation((prev) => ({
      ...prev,
      [convId]: [...(prev[convId] || []), msg],
    }))
  }, [])

  const setConversationId = useCallback((id: string) => {
    localStorage.setItem(STORAGE_KEY, id)
    setConversationIdState(id)
  }, [])

  // Resolve which conversation to open on first load
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

  // Open the websocket exactly once per login — survives conversation switches
  useEffect(() => {
    if (!token) return

    const ws = new WebSocket(`${WS_URL}/ws/chat?token=${token}`)
    wsRef.current = ws

    ws.onopen = () => setIsConnected(true)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      const convId = data.conversation_id

      if (data.type === "thinking") {
        if (convId) {
          setThinkingSet((prev) => new Set(prev).add(convId))
        }
        return
      }

      if (convId) {
        setThinkingSet((prev) => {
          const next = new Set(prev)
          next.delete(convId)
          return next
        })
      }

      if (data.type === "connected") {
        // Global system message, not tied to a specific conversation yet
        return
      }

      if (!convId) return

      if (data.type === "confirm") {
        appendMessage(convId, {
          id: Date.now().toString(),
          role: "system",
          content: "",
          type: "confirm",
          confirmData: data.confirmData,
        })
        return
      }

      if (data.type === "message") {
        appendMessage(convId, {
          id: Date.now().toString(),
          role: "assistant",
          content: data.message,
          type: "message",
        })
        return
      }

      if (data.type === "error") {
        appendMessage(convId, {
          id: Date.now().toString(),
          role: "system",
          content: data.message,
          type: "error",
        })
      }
    }

    ws.onclose = () => setIsConnected(false)
    ws.onerror = () => setIsConnected(false)

    return () => {
      ws.close()
    }
  }, [token, appendMessage])

  // Lazily load history the first time a conversation is opened
  useEffect(() => {
    if (!token || !conversationId) return
    if (loadedConversations.has(conversationId)) return

    const loadHistory = async () => {
      try {
        const res = await fetch(`${API_URL}/api/conversations/${conversationId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.ok) {
          const data = await res.json()
          const history: MessageType[] = Array.isArray(data.messages)
            ? data.messages.map((m: any) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                type: "message",
              }))
            : []
          setMessagesByConversation((prev) => ({ ...prev, [conversationId]: history }))
        }
      } catch (err) {
        console.error("Failed to load conversation history:", err)
      } finally {
        setLoadedConversations((prev) => new Set(prev).add(conversationId))
      }
    }

    loadHistory()
  }, [conversationId, token, loadedConversations])

  const sendMessage = useCallback(
    (message: string) => {
      if (!conversationId) return
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        appendMessage(conversationId, {
          id: Date.now().toString(),
          role: "user",
          content: message,
          type: "message",
        })
        wsRef.current.send(JSON.stringify({ type: "message", message, conversation_id: conversationId }))
      }
    },
    [conversationId, appendMessage],
  )

  const sendContext = useCallback(
    (filename: string, content: string, file_type: "document" | "image", preview?: string, userMessage?: string) => {
      if (!conversationId) return
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        appendMessage(conversationId, {
          id: Date.now().toString(),
          role: "user",
          content: "",
          type: "attachment",
          attachmentData: { filename, file_type, preview, userMessage },
        })
        wsRef.current.send(
          JSON.stringify({ type: "context", filename, content, file_type, conversation_id: conversationId }),
        )
      }
    },
    [conversationId, appendMessage],
  )

  const sendConfirmation = useCallback(
    (confirm_id: string, approved: boolean) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "confirm_response", confirm_id, approved }))
      }
    },
    [],
  )

  const messages = conversationId ? messagesByConversation[conversationId] || [] : []
  const isThinking = conversationId ? thinkingSet.has(conversationId) : false

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