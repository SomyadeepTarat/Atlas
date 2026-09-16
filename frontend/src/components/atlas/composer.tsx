"use client"

import {
  ArrowUp,
  Square,
} from "lucide-react"
import {
  useState,
} from "react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface ComposerProps {
  running: boolean

  onSubmit: (
    question: string,
  ) => Promise<void>

  onCancel: () => void
}

export function Composer({
  running,
  onSubmit,
  onCancel,
}: ComposerProps) {
  const [
    question,
    setQuestion,
  ] = useState("")

  async function submit() {
    const value = question.trim()

    if (!value || running) {
      return
    }

    setQuestion("")

    await onSubmit(value)
  }

  return (
    <div className="rounded-2xl border bg-background p-3 shadow-sm">
      <Textarea
        value={question}
        onChange={(event) => {
          setQuestion(
            event.target.value,
          )
        }}
        onKeyDown={(event) => {
          if (
            event.key === "Enter"
            && !event.shiftKey
          ) {
            event.preventDefault()

            void submit()
          }
        }}
        placeholder="Ask Atlas a research question..."
        className="min-h-24 resize-none border-0 shadow-none focus-visible:ring-0"
        disabled={running}
      />

      <div className="flex justify-end pt-2">
        {running ? (
          <Button
            variant="outline"
            size="icon"
            onClick={onCancel}
          >
            <Square className="size-4" />
          </Button>
        ) : (
          <Button
            size="icon"
            onClick={() => {
              void submit()
            }}
          >
            <ArrowUp className="size-4" />
          </Button>
        )}
      </div>
    </div>
  )
}