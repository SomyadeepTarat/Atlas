"use client"

import {
  useEffect,
  useRef,
  useState,
} from "react"

import {
  createThread,
} from "@/lib/api"
import {
  streamResearch,
} from "@/lib/research-stream"

import type {
  ResearchCompleteData,
  ResearchStreamEvent,
} from "@/lib/types"

import {
  Composer,
} from "@/components/atlas/composer"
import {
  ResearchAnswer,
} from "@/components/atlas/research-answer"
import {
  ResearchProgress,
} from "@/components/atlas/research-progress"

export function ResearchWorkspace() {
  const [
    threadId,
    setThreadId,
  ] = useState<string | null>(
    null,
  )

  const [
    events,
    setEvents,
  ] = useState<
    ResearchStreamEvent[]
  >([])

  const [
    result,
    setResult,
  ] = useState<
    ResearchCompleteData | null
  >(null)

  const [
    running,
    setRunning,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  )

  const abortController =
    useRef<AbortController | null>(
      null,
    )

  useEffect(() => {
    async function initialize() {
      const thread =
        await createThread(
          "New research",
        )

      setThreadId(thread.id)
    }

    void initialize()
  }, [])

  async function runResearch(
    question: string,
  ) {
    if (!threadId) {
      return
    }

    setEvents([])
    setResult(null)
    setError(null)
    setRunning(true)

    const controller =
      new AbortController()

    abortController.current =
      controller

    try {
      await streamResearch({
        threadId,
        question,

        signal:
          controller.signal,

        onEvent(event) {
          setEvents(
            (current) => [
              ...current,
              event,
            ],
          )

          if (
            event.type
            === "complete"
          ) {
            setResult(
              event.data as unknown as ResearchCompleteData,
            )
          }

          if (
            event.type
            === "error"
          ) {
            setError(
              event.message,
            )
          }
        },
      })
    } catch (streamError) {
      if (
        streamError
        instanceof DOMException
        && streamError.name
        === "AbortError"
      ) {
        return
      }

      setError(
        streamError
        instanceof Error
          ? streamError.message
          : "Research failed.",
      )
    } finally {
      setRunning(false)

      abortController.current =
        null
    }
  }

  function cancel() {
    abortController.current?.abort()
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-8 px-5 py-10 md:px-8">
      <header className="space-y-2">
        <p className="text-sm font-medium text-muted-foreground">
          Evidence-driven research
        </p>

        <h1 className="text-3xl font-semibold tracking-tight">
          Atlas
        </h1>
      </header>

      <div className="space-y-6">
        <Composer
          running={running}
          onSubmit={runResearch}
          onCancel={cancel}
        />

        <ResearchProgress
          events={events}
          active={running}
        />

        {error ? (
          <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        {result ? (
          <ResearchAnswer
            result={result}
          />
        ) : null}
      </div>
    </main>
  )
}