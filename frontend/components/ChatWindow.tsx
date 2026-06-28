"use client"

import { useState, useRef, useEffect } from "react"
import { useWebSocket } from "@/hooks/useWebSocket"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import ConfirmAction from "@/components/ConfirmAction"
import Link from "next/link"

export default function ChatWindow() {
  const sessionId = "user_session_001"
  const { messages, isConnected, isThinking, sendMessage, sendConfirmation } = useWebSocket(sessionId)
  const [input, setInput] = useState("")
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isThinking])

  const handleSend = () => {
    if (!input.trim() || !isConnected) return
    sendMessage(input.trim())
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">

      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b">
        <div>
          <h1 className="text-xl font-semibold">Aria</h1>
          <p className="text-sm text-muted-foreground">AI Personal Secretary</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Link href="/settings">
            <Button variant="outline" size="sm">Settings</Button>
          </Link>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 pr-4">
        <div className="flex flex-col gap-4 pb-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.type === "confirm" && msg.confirmData ? (
                <ConfirmAction
                  action={msg.confirmData.action}
                  details={msg.confirmData.details}
                  onApprove={() => sendConfirmation(msg.confirmData!.confirm_id, true)}
                  onReject={() => sendConfirmation(msg.confirmData!.confirm_id, false)}
                />
              ) : msg.role === "system" ? (
                <div className="text-xs text-muted-foreground text-center w-full py-1">
                  {msg.content}
                </div>
              ) : (
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-sm"
                      : "bg-muted text-foreground rounded-bl-sm"
                  }`}
                >
                  {msg.content}
                </div>
              )}
            </div>
          ))}

          {isThinking && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1 items-center h-4">
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="flex gap-2 mt-4 pt-4 border-t">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isConnected ? "Message Aria..." : "Connecting..."}
          disabled={!isConnected}
          className="flex-1"
        />
        <Button
          onClick={handleSend}
          disabled={!isConnected || !input.trim()}
        >
          Send
        </Button>
      </div>

    </div>
  )
}