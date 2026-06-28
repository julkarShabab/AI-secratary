"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export type ConfirmActionProps = {
  action: string
  details: string
  onApprove: () => void
  onReject: () => void
}

export default function ConfirmAction({
  action,
  details,
  onApprove,
  onReject
}: ConfirmActionProps) {
  const [decided, setDecided] = useState(false)

  const handleApprove = () => {
    setDecided(true)
    onApprove()
  }

  const handleReject = () => {
    setDecided(true)
    onReject()
  }

  return (
    <Card className="p-4 border border-yellow-200 bg-yellow-50 dark:bg-yellow-950 dark:border-yellow-800 max-w-[75%]">

      <div className="flex items-center gap-2 mb-3">
        <Badge variant="outline" className="text-yellow-700 border-yellow-400 dark:text-yellow-300">
          Action Required
        </Badge>
      </div>

      <p className="text-sm font-medium mb-1">{action}</p>
      <p className="text-xs text-muted-foreground mb-4">{details}</p>

      {!decided ? (
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={handleApprove}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            Approve
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleReject}
            className="border-red-300 text-red-600 hover:bg-red-50"
          >
            Cancel
          </Button>
        </div>
      ) : (
        <p className="text-xs text-muted-foreground italic">Decision recorded.</p>
      )}

    </Card>
  )
}