import {
  Skeleton,
} from "@/components/ui/skeleton"


export default function Loading() {
  return (
    <main className="mx-auto max-w-4xl space-y-6 px-5 py-10">
      <Skeleton className="h-8 w-32" />

      <Skeleton className="h-28 w-full rounded-2xl" />

      <Skeleton className="h-64 w-full rounded-2xl" />
    </main>
  )
}