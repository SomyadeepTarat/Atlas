"use client"

import {
  MessageSquareText,
  Plus,
} from "lucide-react"
import {
  useEffect,
  useState,
} from "react"

import { Button } from "@/components/ui/button"

import {
  createThread,
  listThreads,
} from "@/lib/api"
import type {
  Thread,
} from "@/lib/types"

interface ThreadSidebarProps {
  currentThreadId: string | null

  onSelect: (
    thread: Thread,
  ) => void
}

export function ThreadSidebar({
  currentThreadId,
  onSelect,
}: ThreadSidebarProps) {
  const [
    threads,
    setThreads,
  ] = useState<Thread[]>([])

  useEffect(() => {
    let active = true

    void listThreads().then((loadedThreads) => {
      if (active) {
        setThreads(loadedThreads)
      }
    })

    return () => {
      active = false
    }
  }, [])

  async function createNew() {
    const thread =
      await createThread(
        "New research",
      )

    setThreads(
      (current) => [
        thread,
        ...current,
      ],
    )

    onSelect(thread)
  }

  return (
    <div className="space-y-4">
      <Button
        className="w-full justify-start"
        onClick={() => {
          void createNew()
        }}
      >
        <Plus className="mr-2 size-4" />
        New research
      </Button>

      <div className="space-y-1">
        {threads.map((thread) => (
          <button
            type="button"
            key={thread.id}
            onClick={() => {
              onSelect(thread)
            }}
            className={[
              "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition",
              currentThreadId
                === thread.id
                ? "bg-muted font-medium"
                : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
            ].join(" ")}
          >
            <MessageSquareText className="size-4 shrink-0" />

            <span className="truncate">
              {thread.title
                ?? "Untitled research"}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}