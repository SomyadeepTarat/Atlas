export type ResearchStage =
  | "starting"
  | "planning"
  | "retrieving"
  | "assessing"
  | "synthesizing"
  | "verifying"
  | "repairing"
  | "complete"

export type ResearchEventType =
  | "started"
  | "status"
  | "retrieval"
  | "answer"
  | "complete"
  | "error"

export interface ResearchStreamEvent {
  type: ResearchEventType
  stage: ResearchStage
  message: string
  sequence: number
  data: Record<string, unknown>
}

export interface GroundedAnswer {
  answer: string
  used_chunk_ids: string[]
  confidence: number
  insufficient_context: boolean
}

export interface ResearchCompleteData {
  answer: GroundedAnswer
  iterations: number
  verification_passed: boolean
  verification_reason: string | null
}

export interface Thread {
  id: string
  title: string | null
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  chunks_created: number
}