"use client"

import { useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"

export default function AuthCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { setTokenAndUser } = useAuth()

  useEffect(() => {
    const token = searchParams.get("token")
    if (!token) {
      router.push("/login")
      return
    }

    setTokenAndUser(token)
      .then(() => router.push("/"))
      .catch(() => router.push("/login"))
  }, [searchParams, router, setTokenAndUser])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-sm text-muted-foreground">Signing you in...</p>
    </div>
  )
}