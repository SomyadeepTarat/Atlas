import {
  AppShell,
} from "@/components/atlas/app-shell"
import {
  ResearchWorkspace,
} from "@/components/atlas/research-workspace"


export default function HomePage() {
  return (
    <AppShell>
      <ResearchWorkspace />
    </AppShell>
  )
}