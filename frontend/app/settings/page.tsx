"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import Link from "next/link"

type Integration = {
  id: string
  name: string
  description: string
  connected: boolean
  icon: string
}

const integrations: Integration[] = [
  {
    id: "gmail",
    name: "Gmail",
    description: "Read and send emails on your behalf",
    connected: true,
    icon: "📧"
  },
  {
    id: "google_calendar",
    name: "Google Calendar",
    description: "View and manage your calendar events",
    connected: true,
    icon: "📅"
  },
  {
    id: "slack",
    name: "Slack",
    description: "Read and post messages to your workspace",
    connected: true,
    icon: "💬"
  },
  {
    id: "jira",
    name: "Jira",
    description: "Create and manage tasks in your project",
    connected: true,
    icon: "📋"
  },
  {
    id: "github",
    name: "GitHub",
    description: "View repositories, issues and pull requests",
    connected: false,
    icon: "🐙"
  },
  {
    id: "notion",
    name: "Notion",
    description: "Read and write to your Notion workspace",
    connected: false,
    icon: "📝"
  }
]

export default function SettingsPage() {
  const [services, setServices] = useState(integrations)

  const toggleConnection = (id: string) => {
    setServices((prev) =>
      prev.map((s) =>
        s.id === id ? { ...s, connected: !s.connected } : s
      )
    )
  }

  const connected = services.filter((s) => s.connected)
  const disconnected = services.filter((s) => !s.connected)

  return (
    <div className="h-screen overflow-y-auto">
    <div className="max-w-3xl mx-auto p-6">

      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b">
        <div>
          <h1 className="text-xl font-semibold">Settings</h1>
          <p className="text-sm text-muted-foreground">Manage your integrations</p>
        </div>
        <Link href="/">
          <Button variant="outline" size="sm">Back to Chat</Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <Card className="p-4">
          <p className="text-2xl font-semibold">{connected.length}</p>
          <p className="text-sm text-muted-foreground">Connected services</p>
        </Card>
        <Card className="p-4">
          <p className="text-2xl font-semibold">{disconnected.length}</p>
          <p className="text-sm text-muted-foreground">Available to connect</p>
        </Card>
      </div>

      {/* Connected */}
      <div className="mb-6">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Connected
        </h2>
        <div className="flex flex-col gap-3">
          {connected.map((service) => (
            <Card key={service.id} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{service.icon}</span>
                <div>
                  <p className="text-sm font-medium">{service.name}</p>
                  <p className="text-xs text-muted-foreground">{service.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="text-green-600 border-green-300">
                  Connected
                </Badge>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-red-500 border-red-200 hover:bg-red-50"
                  onClick={() => toggleConnection(service.id)}
                >
                  Disconnect
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Available */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Available
        </h2>
        <div className="flex flex-col gap-3">
          {disconnected.map((service) => (
            <Card key={service.id} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{service.icon}</span>
                <div>
                  <p className="text-sm font-medium">{service.name}</p>
                  <p className="text-xs text-muted-foreground">{service.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="text-muted-foreground">
                  Not connected
                </Badge>
                <Button
                  size="sm"
                  onClick={() => toggleConnection(service.id)}
                >
                  Connect
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

    </div>
    </div>
  )
}