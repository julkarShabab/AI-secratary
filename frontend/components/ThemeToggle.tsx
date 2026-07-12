"use client"

import { useEffect, useState } from "react"
import { useTheme } from "next-themes"
import { Sun, Moon, Monitor } from "lucide-react"

const options = [
  { value: "light", icon: Sun },
  { value: "dark", icon: Moon },
  { value: "system", icon: Monitor },
] as const

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])
  if (!mounted) return <div className="w-28 h-9" />

  return (
    <div className="flex items-center gap-0.5 p-1 rounded-full bg-muted/60 border border-border w-fit">
      {options.map((opt) => {
        const Icon = opt.icon
        const isActive = theme === opt.value
        return (
          <button
            key={opt.value}
            onClick={() => setTheme(opt.value)}
            className={`w-8 h-7 flex items-center justify-center rounded-full transition-colors ${
              isActive
                ? "bg-background shadow-sm text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
            title={opt.value}
          >
            <Icon className="w-4 h-4" />
          </button>
        )
      })}
    </div>
  )
}