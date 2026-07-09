"use client"

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react"
import { useRouter } from "next/navigation"

type User = {
  id: number
  email: string
  name: string | null
}

type AuthContextType = {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name?: string) => Promise<void>
  logout: () => void
  setTokenAndUser: (token: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)
const API_URL = "http://localhost:8000"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const fetchUser = useCallback(async (authToken: string) => {
    const res = await fetch(`${API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    if (!res.ok) throw new Error("Failed to fetch user")
    return res.json()
  }, [])

  useEffect(() => {
    const stored = localStorage.getItem("aria_token")
    if (stored) {
      fetchUser(stored)
        .then((u) => {
          setToken(stored)
          setUser(u)
        })
        .catch(() => localStorage.removeItem("aria_token"))
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [fetchUser])

  const setTokenAndUser = useCallback(
    async (authToken: string) => {
      const u = await fetchUser(authToken)
      localStorage.setItem("aria_token", authToken)
      setToken(authToken)
      setUser(u)
    },
    [fetchUser],
  )

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || "Login failed")
    }
    const data = await res.json()
    localStorage.setItem("aria_token", data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }, [])

  const signup = useCallback(async (email: string, password: string, name?: string) => {
    const res = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || "Signup failed")
    }
    const data = await res.json()
    localStorage.setItem("aria_token", data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem("aria_token")
    setToken(null)
    setUser(null)
    router.push("/login")
  }, [router])

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, signup, logout, setTokenAndUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}