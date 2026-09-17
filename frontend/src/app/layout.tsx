import type { Metadata } from "next"

import "./globals.css"


export const metadata: Metadata = {
  title: "Atlas — Evidence-Driven Research Agent",

  description:
    "A locally deployable, evaluation-driven AI research agent with hybrid retrieval, citations, controlled tools, persistent memory, observability, and adversarial testing.",
}


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}