"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import ChatWindow from "@/components/ChatWindow"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/contexts/AuthContext"

export default function Home() {
  const [conversationId, setConversationId] = useState<string | null>(null)
  const { user, token, isLoading, logout } = useAuth()
  const router = useRouter()
  const hasInitialized = useRef(false)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [isLoading, user, router])

  useEffect(() => {
    if (!token || hasInitialized.current) return
    hasInitialized.current = true

    const createOrLoadConversation = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/conversations", {
          headers: { Authorization: `Bearer ${token}` }
        })
        const data = await res.json()

        if (Array.isArray(data) && data.length > 0) {
          setConversationId(data[0].id)
        } else {
          const createRes = await fetch("http://localhost:8000/api/conversations", {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ title: "New conversation" })
          })
          const newConv = await createRes.json()
          setConversationId(newConv.id)
        }
      } catch (err) {
        console.error("Failed to load conversation:", err)
        hasInitialized.current = false
      }
    }

    createOrLoadConversation()
  }, [token])

  if (isLoading || !user || !conversationId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    )
  }

  return (
    <main className="h-screen flex overflow-hidden">
      <Sidebar
        activeId={conversationId}
        onSelect={setConversationId}
        onNewChat={setConversationId}
        token={token!}
        userName={user.name || user.email}
        onLogout={logout}
      />
      <div className="flex-1 min-h-0 h-full">
        <ChatWindow conversationId={conversationId} token={token!} />
      </div>
    </main>
  )
}