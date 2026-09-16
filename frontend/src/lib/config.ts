const apiUrl =
  process.env.NEXT_PUBLIC_ATLAS_API_URL

if (!apiUrl) {
  throw new Error(
    "NEXT_PUBLIC_ATLAS_API_URL is not configured",
  )
}

export const config = {
  apiUrl,
} as const
