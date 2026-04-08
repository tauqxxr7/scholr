import Link from 'next/link'
import { ArrowRight, BookOpen, BrainCircuit, NotebookPen } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const modules = [
  {
    title: 'Research',
    description: 'Get papers, reading order, and project-worthy research gaps in under a minute.',
    icon: BookOpen,
  },
  {
    title: 'Notes',
    description: 'Generate clean revision notes that actually help for internal exams and viva prep.',
    icon: NotebookPen,
  },
  {
    title: 'Doubt',
    description: 'Turn confusing concepts into step-by-step explanations with examples.',
    icon: BrainCircuit,
  },
]

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.22),_transparent_28%),linear-gradient(180deg,#fffdf7_0%,#ffffff_55%,#f8fafc_100%)]">
      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <nav className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Scholr</p>
            <p className="mt-2 text-lg font-semibold text-slate-950">Academic operating system for BTech students</p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/sign-in">
              <Button variant="outline">Sign in</Button>
            </Link>
            <Link href="/dashboard">
              <Button className="bg-slate-950 text-white hover:bg-slate-800">Open dashboard</Button>
            </Link>
          </div>
        </nav>

        <section className="grid gap-10 py-20 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <Badge className="rounded-full bg-white px-3 py-1 text-slate-700 shadow-sm">
              Zero-money MVP, built for real student workflows
            </Badge>
            <h1 className="mt-6 max-w-4xl text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl">
              Turn any BTech topic into exam-ready notes, research direction, and doubt solving in
              under 60 seconds.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
              Scholr focuses on the wedge that matters first: one fast, polished academic tool that
              feels trustworthy enough to demo, share, and pitch.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/research">
                <Button size="lg" className="bg-slate-950 text-white hover:bg-slate-800">
                  Try the live research flow
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="outline">
                  See the product workspace
                </Button>
              </Link>
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-white/90 p-6 shadow-xl shadow-amber-100/30">
            <div className="rounded-[1.5rem] bg-slate-950 p-6 text-white">
              <p className="text-sm text-slate-300">Promise</p>
              <p className="mt-3 text-2xl font-semibold">India-first academic operating system</p>
              <p className="mt-4 text-sm leading-6 text-slate-300">
                Start with research, notes, and doubt solving. Add history, auth, placements, and
                monetization only after the core feels solid.
              </p>
            </div>
            <div className="mt-6 space-y-4">
              {modules.map((module) => {
                const Icon = module.icon
                return (
                  <div key={module.title} className="rounded-2xl border border-slate-200 p-4">
                    <div className="flex items-center gap-3">
                      <div className="rounded-xl bg-amber-100 p-2 text-amber-800">
                        <Icon className="h-4 w-4" />
                      </div>
                      <p className="font-medium text-slate-900">{module.title}</p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-600">{module.description}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
