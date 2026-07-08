"use client"

import { useEffect, useState, useCallback } from "react"
import { Button } from "@/components/ui/button"

type Conversation = {
  id: string
  title: string
  created_at: string
  updated_at: string
}

type SidebarProps = {
  activeId: string
  onSelect: (id: string) => void
  onNewChat: (id: string) => void
}

export default function Sidebar({ activeId, onSelect, onNewChat }: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchConversations = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/conversations")
      const data = await res.json()
      setConversations(data)
    } catch (err) {
      console.error("Failed to load conversations:", err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations, activeId])

  const handleNewChat = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "New conversation" }),
      })
      const data = await res.json()
      onNewChat(data.id)
    } catch (err) {
      console.error("Failed to create conversation:", err)
    }
  }

  return (
    <div className="w-64 h-screen border-r flex flex-col bg-muted/30">
      <div className="p-3 border-b">
        <Button onClick={handleNewChat} className="w-full" size="sm">
          + New chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
        {isLoading && (
          <div className="text-xs text-muted-foreground text-center py-4">Loading...</div>
        )}

        {!isLoading && conversations.length === 0 && (
          <div className="text-xs text-muted-foreground text-center py-4">No conversations yet</div>
        )}

        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`text-left text-sm px-3 py-2 rounded-lg truncate transition-colors ${
              conv.id === activeId
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted text-foreground"
            }`}
            title={conv.title}
          >
            {conv.title}
          </button>
        ))}
      </div>
    </div>
  )
}