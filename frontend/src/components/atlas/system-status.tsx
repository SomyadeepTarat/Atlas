import {
  Badge,
} from "@/components/ui/badge"


interface SystemStatusProps {
  degraded?: boolean
}

export function SystemStatus({
  degraded = false,
}: SystemStatusProps) {
  return (
    <Badge
      variant={
        degraded
          ? "outline"
          : "secondary"
      }
    >
      <span className="mr-2 size-2 rounded-full bg-current" />

      {degraded
        ? "Degraded"
        : "Ready"}
    </Badge>
  )
}