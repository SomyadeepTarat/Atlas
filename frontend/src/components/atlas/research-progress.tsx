import {
  CheckCircle2,
  Circle,
  LoaderCircle,
} from "lucide-react"

import type {
  ResearchStage,
  ResearchStreamEvent,
} from "@/lib/types"

interface ResearchProgressProps {
  events: ResearchStreamEvent[]
  active: boolean
}

const stageOrder: ResearchStage[] = [
  "planning",
  "retrieving",
  "assessing",
  "synthesizing",
  "verifying",
  "complete",
]

export function ResearchProgress({
  events,
  active,
}: ResearchProgressProps) {
  const seenStages = new Set(
    events.map((event) => event.stage),
  )

  const currentStage =
    events.at(-1)?.stage

  if (
    events.length === 0
    && !active
  ) {
    return null
  }

  return (
    <div className="space-y-3">
      <div className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
        Research progress
      </div>

      <div className="space-y-2">
        {stageOrder.map((stage) => {
          const complete =
            seenStages.has(stage)

          const current =
            stage === currentStage
            && active

          return (
            <div
              key={stage}
              className="flex items-center gap-3 text-sm"
            >
              {current ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : complete ? (
                <CheckCircle2 className="size-4" />
              ) : (
                <Circle className="size-4 text-muted-foreground/50" />
              )}

              <span
                className={
                  complete || current
                    ? "text-foreground"
                    : "text-muted-foreground/50"
                }
              >
                {formatStage(stage)}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function formatStage(
  stage: ResearchStage,
): string {
  const labels: Record<
    ResearchStage,
    string
  > = {
    starting: "Starting",
    planning: "Planning research",
    retrieving: "Retrieving evidence",
    assessing: "Evaluating evidence",
    synthesizing: "Synthesizing answer",
    verifying: "Verifying claims",
    repairing: "Repairing answer",
    complete: "Complete",
  }

  return labels[stage]
}