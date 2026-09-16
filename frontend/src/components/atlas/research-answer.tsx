import {
  BadgeCheck,
  ShieldAlert,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import type {
  ResearchCompleteData,
} from "@/lib/types"

interface ResearchAnswerProps {
  result: ResearchCompleteData
}

export function ResearchAnswer({
  result,
}: ResearchAnswerProps) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>
          Research answer
        </CardTitle>

        {result.verification_passed ? (
          <Badge variant="secondary">
            <BadgeCheck className="mr-1 size-3" />
            Verified
          </Badge>
        ) : (
          <Badge variant="outline">
            <ShieldAlert className="mr-1 size-3" />
            Verification limited
          </Badge>
        )}
      </CardHeader>

      <CardContent className="space-y-5">
        {result.answer
          .insufficient_context ? (
          <div className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
            Atlas could not find enough
            supporting evidence to answer
            reliably.
          </div>
        ) : null}

        <div className="whitespace-pre-wrap leading-7">
          {result.answer.answer}
        </div>

        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">
            {result.iterations} research
            {result.iterations === 1
              ? " pass"
              : " passes"}
          </Badge>

          <Badge variant="outline">
            confidence{" "}
            {Math.round(
              result.answer.confidence
              * 100,
            )}
            %
          </Badge>

          <Badge variant="outline">
            {
              result.answer
                .used_chunk_ids.length
            }{" "}
            evidence chunks
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}