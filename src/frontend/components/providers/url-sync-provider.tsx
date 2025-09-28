"use client"

import type React from "react"
import { useUrlSync } from "../../hooks/use-url-sync"

interface UrlSyncProviderProps {
  children: React.ReactNode
}

export function UrlSyncProvider({ children }: UrlSyncProviderProps) {
  // Initialize URL sync
  useUrlSync()

  return <>{children}</>
}
