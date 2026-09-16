"use client"

import {
  FileUp,
  LoaderCircle,
} from "lucide-react"
import {
  useRef,
  useState,
} from "react"

import { Button } from "@/components/ui/button"
import {
  uploadDocument,
} from "@/lib/api"

export function DocumentUpload() {
  const inputRef =
    useRef<HTMLInputElement>(null)

  const [
    uploading,
    setUploading,
  ] = useState(false)

  const [
    status,
    setStatus,
  ] = useState<string | null>(
    null,
  )

  async function handleFile(
    file: File,
  ) {
    setUploading(true)

    setStatus(null)

    try {
      const result =
        await uploadDocument(file)

      setStatus(
        `${result.filename} · `
        + `${result.chunks_created} chunks`,
      )
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Upload failed.",
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-2">
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        hidden
        onChange={(event) => {
          const file =
            event.target.files?.[0]

          if (file) {
            void handleFile(file)
          }

          event.currentTarget.value = ""
        }}
      />

      <Button
        variant="outline"
        className="w-full justify-start"
        disabled={uploading}
        onClick={() => {
          inputRef.current?.click()
        }}
      >
        {uploading ? (
          <LoaderCircle className="mr-2 size-4 animate-spin" />
        ) : (
          <FileUp className="mr-2 size-4" />
        )}

        Upload research PDF
      </Button>

      {status ? (
        <p className="px-1 text-xs text-muted-foreground">
          {status}
        </p>
      ) : null}
    </div>
  )
}