"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import ChatWindow from "@/components/ChatWindow"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/contexts/AuthContext"

const DEFAULT_SESSION_ID = "user_session_001"

export default function Home() {
  const [conversationId, setConversationId] = useState(DEFAULT_SESSION_ID)
  const { user, token, isLoading, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [isLoading, user, router])

  if (isLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    )
  }

  return (
    <main className="h-screen flex">
      <Sidebar
        activeId={conversationId}
        onSelect={setConversationId}
        onNewChat={setConversationId}
        token={token!}
        userName={user.name || user.email}
        onLogout={logout}
      />
      <div className="flex-1">
        <ChatWindow conversationId={conversationId} token={token!} />
      </div>
    </main>
  )
}