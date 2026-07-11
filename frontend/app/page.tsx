"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import ChatWindow from "@/components/ChatWindow"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/contexts/AuthContext"
import { useChat } from "@/contexts/ChatContext"

export default function Home() {
  const { user, token, isLoading, logout } = useAuth()
  const { conversationId, setConversationId } = useChat()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [isLoading, user, router])

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
        <ChatWindow />
      </div>
    </main>
  )
}