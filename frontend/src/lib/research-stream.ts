import {
  createParser,
  type EventSourceMessage,
} from "eventsource-parser"

import { config } from "@/lib/config"
import type {
  ResearchStreamEvent,
} from "@/lib/types"

interface StreamResearchOptions {
  threadId: string
  question: string

  signal?: AbortSignal

  onEvent: (
    event: ResearchStreamEvent,
  ) => void
}

export async function streamResearch({
  threadId,
  question,
  signal,
  onEvent,
}: StreamResearchOptions): Promise<void> {
  const response = await fetch(
    `${config.apiUrl}/research/threads/${threadId}/stream`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },

      body: JSON.stringify({
        question,
      }),

      signal,
    },
  )

  if (!response.ok) {
    throw new Error(
      `Research stream failed (${response.status})`,
    )
  }

  if (!response.body) {
    throw new Error(
      "Research stream has no response body.",
    )
  }

  const decoder = new TextDecoder()

  const parser = createParser({
    maxBufferSize: 1024 * 1024,

    onEvent(
      message: EventSourceMessage,
    ) {
      try {
        const event =
          JSON.parse(
            message.data,
          ) as ResearchStreamEvent

        onEvent(event)
      } catch {
        throw new Error(
          "Received malformed research event.",
        )
      }
    },
  })

  const reader =
    response.body.getReader()

  try {
    while (true) {
      const {
        value,
        done,
      } = await reader.read()

      if (done) {
        break
      }

      parser.feed(
        decoder.decode(
          value,
          {
            stream: true,
          },
        ),
      )
    }

    parser.reset({
      consume: true,
    })
  } finally {
    reader.releaseLock()
  }
}