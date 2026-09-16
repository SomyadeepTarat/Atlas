import {
  DocumentUpload,
} from "@/components/atlas/document-upload"

interface AppShellProps {
  children: React.ReactNode
}

export function AppShell({
  children,
}: AppShellProps) {
  return (
    <div className="grid min-h-screen md:grid-cols-[280px_1fr]">
      <aside className="hidden border-r bg-muted/20 p-5 md:block">
        <div className="mb-8">
          <div className="text-lg font-semibold">
            Atlas
          </div>

          <div className="text-xs text-muted-foreground">
            Research workspace
          </div>
        </div>

        <DocumentUpload />
      </aside>

      <section className="min-w-0">
        {children}
      </section>
    </div>
  )
}