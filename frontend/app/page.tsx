"use client"

import { useState } from "react"
import ChatWindow from "@/components/ChatWindow"
import Sidebar from "@/components/Sidebar"

const DEFAULT_SESSION_ID = "user_session_001"

export default function Home() {
  const [conversationId, setConversationId] = useState(DEFAULT_SESSION_ID)

  return (
    <main className="h-screen flex">
      <Sidebar
        activeId={conversationId}
        onSelect={setConversationId}
        onNewChat={setConversationId}
      />
      <div className="flex-1">
        <ChatWindow conversationId={conversationId} />
      </div>
    </main>
  )
}