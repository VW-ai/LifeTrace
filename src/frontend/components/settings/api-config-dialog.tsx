"use client"

import { useState } from "react"
import { Eye, EyeOff, Loader2, CheckCircle } from "lucide-react"
import { Button } from "../ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "../ui/dialog"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface ApiConfigDialogProps {
  apiType: 'notion' | 'openai' | 'google_calendar'
  apiName?: string
  children?: React.ReactNode
  onConfigured?: () => void
  // Controlled mode props
  open?: boolean
  onOpenChange?: (open: boolean) => void
  onSuccess?: () => void
}

export function ApiConfigDialog({
  apiType,
  apiName,
  children,
  onConfigured,
  open: controlledOpen,
  onOpenChange,
  onSuccess
}: ApiConfigDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false)

  // Use controlled or uncontrolled state
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen
  const setOpen = onOpenChange || setInternalOpen
  const [apiKey, setApiKey] = useState("")
  const [showKey, setShowKey] = useState(false)
  const [testing, setTesting] = useState(false)
  const [saving, setSaving] = useState(false)

  // Additional fields for OpenAI
  const [openaiModel, setOpenaiModel] = useState("gpt-4o-mini")
  const [embedModel, setEmbedModel] = useState("text-embedding-3-small")

  const handleTest = async () => {
    if (!apiKey.trim()) {
      toast.error("Please enter an API key")
      return
    }

    setTesting(true)
    try {
      const result = await apiClient.testApiConnection({
        api_type: apiType,
        api_key: apiKey
      })

      if (result.success) {
        toast.success(result.message)
      } else {
        toast.error(result.message)
      }
    } catch (error) {
      toast.error("Failed to test connection")
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    if (!apiKey.trim()) {
      toast.error("Please enter an API key")
      return
    }

    setSaving(true)
    try {
      const config: any = {}

      if (apiType === 'notion') {
        config.notion_api_key = apiKey
      } else if (apiType === 'openai') {
        config.openai_api_key = apiKey
        config.openai_model = openaiModel
        config.openai_embed_model = embedModel
      } else if (apiType === 'google_calendar') {
        config.google_calendar_key = apiKey
      }

      const result = await apiClient.updateApiConfiguration(config)

      if (result.status === 'success') {
        toast.success(result.message)
        setOpen(false)
        setApiKey("")
        if (onConfigured) onConfigured()
        if (onSuccess) onSuccess()
      } else {
        toast.error(result.message)
      }
    } catch (error) {
      toast.error("Failed to save configuration")
    } finally {
      setSaving(false)
    }
  }

  // Get API name from type if not provided
  const displayName = apiName || (
    apiType === 'notion' ? 'Notion' :
    apiType === 'openai' ? 'OpenAI' :
    'Google Calendar'
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {children && (
        <DialogTrigger asChild>
          {children}
        </DialogTrigger>
      )}
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Configure {displayName}</DialogTitle>
          <DialogDescription>
            Enter your API credentials to connect {displayName}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {apiType === 'google_calendar' ? (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Google Calendar uses OAuth authentication. Please follow these steps:
              </p>
              <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                <li>Download credentials.json from Google Cloud Console</li>
                <li>Place it in the project root directory</li>
                <li>Run the ingestion script to complete OAuth flow</li>
                <li>This will generate token.json automatically</li>
              </ol>
              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-xs text-blue-900">
                  Command: <code className="bg-blue-100 px-1 rounded">python runner/run_ingest.py --start YYYY-MM-DD --end YYYY-MM-DD --cal-ids primary</code>
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="api-key">API Key</Label>
                <div className="relative">
                  <Input
                    id="api-key"
                    type={showKey ? "text" : "password"}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder={`Enter your ${apiName} API key`}
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowKey(!showKey)}
                  >
                    {showKey ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              {apiType === 'openai' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="openai-model">Model</Label>
                    <Input
                      id="openai-model"
                      value={openaiModel}
                      onChange={(e) => setOpenaiModel(e.target.value)}
                      placeholder="gpt-4o-mini"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="embed-model">Embedding Model</Label>
                    <Input
                      id="embed-model"
                      value={embedModel}
                      onChange={(e) => setEmbedModel(e.target.value)}
                      placeholder="text-embedding-3-small"
                    />
                  </div>
                </>
              )}

              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={testing || !apiKey.trim()}
                className="w-full"
              >
                {testing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Test Connection
                  </>
                )}
              </Button>
            </>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          {apiType !== 'google_calendar' && (
            <Button onClick={handleSave} disabled={saving || !apiKey.trim()}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Configuration"
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
