"use client"

import { useState, useEffect } from "react"
import { Share2, Copy, Check } from "lucide-react"
import { Button } from "../ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover"
import { Input } from "../ui/input"
import { useUrlSync } from "../../hooks/use-url-sync"

export function ShareButton() {
  const [copied, setCopied] = useState(false)
  const { createShareableUrl } = useUrlSync()

  const handleCopy = async () => {
    const shareableUrl = createShareableUrl()

    try {
      await navigator.clipboard.writeText(shareableUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("Failed to copy URL:", error)
    }
  }

  const [shareableUrl, setShareableUrl] = useState("")

  useEffect(() => {
    // Only run on client side
    setShareableUrl(createShareableUrl())
  }, [createShareableUrl])

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          <Share2 className="h-4 w-4 mr-2" />
          Share
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="end">
        <div className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Share Current View</h4>
            <p className="text-sm text-muted-foreground">
              Share this URL to let others see the same filtered view of your data.
            </p>
          </div>

          <div className="flex gap-2">
            <Input value={shareableUrl} readOnly className="text-xs" />
            <Button size="sm" onClick={handleCopy} className="flex-shrink-0">
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>

          {copied && <p className="text-sm text-green-600">URL copied to clipboard!</p>}
        </div>
      </PopoverContent>
    </Popover>
  )
}
