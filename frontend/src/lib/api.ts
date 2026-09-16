import { config } from "./config"
import type {
  DocumentUploadResponse,
  Thread,
} from "@/lib/types"

async function assertOk(
  response: Response,
): Promise<void> {
  if (response.ok) {
    return
  }

  let message = "Atlas request failed."

  try {
    const body = await response.json()

    if (typeof body?.detail === "string") {
      message = body.detail
    } else if (body?.detail) {
      message = JSON.stringify(body.detail)
    }
  } catch {
    // Keep fallback message.
  }

  throw new Error(message)
}

export async function createThread(
  title?: string,
): Promise<Thread> {
  const response = await fetch(
    `${config.apiBaseUrl}/threads`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: title ?? null,
      }),
    },
  )

  await assertOk(response)

  return response.json()
}

export async function uploadDocument(
  file: File,
): Promise<DocumentUploadResponse> {
  const form = new FormData()

  form.append("file", file)

  const response = await fetch(
    `${config.apiBaseUrl}/documents/upload`,
    {
      method: "POST",
      body: form,
    },
  )

  await assertOk(response)

  return response.json()
}