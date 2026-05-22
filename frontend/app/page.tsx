import Link from 'next/link'
import { ArrowRight, BookOpen, BrainCircuit, NotebookPen, CheckCircle2, Sparkles } from 'lucide-react'

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
    <main className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.22),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(125,211,252,0.18),_transparent_26%),linear-gradient(180deg,#fffdf7_0%,#ffffff_55%,#f8fafc_100%)]">
      <div className="mx-auto max-w-6xl px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
        <nav className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Scholr</p>
            <p className="mt-1.5 max-w-[20rem] text-sm font-semibold leading-5 text-slate-950 sm:mt-2 sm:max-w-none sm:text-lg">
              Academic operating system for BTech students
            </p>
          </div>
          <div className="grid w-full min-w-0 grid-cols-2 gap-2 sm:flex sm:w-auto sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
            <Link href="/research" className="min-w-0">
              <Button variant="outline" className="min-h-10 w-full rounded-xl px-3 text-sm sm:min-h-11 sm:w-auto">
                Try research
              </Button>
            </Link>
            <Link href="/privacy" className="min-w-0">
              <Button variant="ghost" className="min-h-10 w-full rounded-xl px-3 text-sm text-slate-600 hover:text-slate-950 sm:min-h-11 sm:w-auto">
                Privacy
              </Button>
            </Link>
            <Link href="/dashboard" className="col-span-2 min-w-0 sm:col-span-1">
              <Button className="min-h-10 w-full rounded-xl bg-slate-950 px-3 text-sm text-white hover:bg-slate-800 sm:min-h-11 sm:w-auto">
                Open dashboard
              </Button>
            </Link>
          </div>
        </nav>

        <section className="grid gap-6 py-8 sm:gap-8 sm:py-12 md:py-14 lg:grid-cols-[1.08fr_0.92fr] lg:items-center lg:gap-10 lg:py-20">
          <div className="min-w-0">
            <Badge className="inline-flex max-w-full rounded-full bg-white px-3 py-1 text-left text-[0.72rem] leading-5 text-slate-700 shadow-sm sm:text-xs">
              <span className="min-w-0 whitespace-normal break-words sm:hidden">Multi-provider academic workspace</span>
              <span className="hidden whitespace-nowrap sm:inline">
                Multi-provider academic workspace, built for real student workflows
              </span>
            </Badge>
            <h1 className="mt-4 max-w-[18ch] text-balance text-[clamp(2rem,8vw,2.45rem)] font-semibold leading-[1.05] text-slate-950 sm:mt-5 sm:max-w-4xl sm:text-[clamp(3rem,6vw,4.35rem)] sm:leading-[1.02] lg:text-[clamp(3.55rem,5vw,4.75rem)]">
              Turn any BTech topic into exam-ready notes, research direction, and doubt solving.
            </h1>
            <p className="mt-4 max-w-[34rem] text-pretty text-[clamp(0.95rem,3.6vw,1.05rem)] leading-6 text-slate-600 sm:mt-5 sm:text-[1.08rem] sm:leading-7">
              Scholr focuses on the wedge that matters first: one fast, polished academic platform
              with streaming AI, document grounding, and resilient fallback behavior.
            </p>
            <div className="mt-5 grid gap-2.5 sm:mt-6 sm:max-w-xl sm:grid-cols-2 sm:gap-3">
              <div className="min-w-0 rounded-2xl border border-white/70 bg-white/80 p-3.5 shadow-sm sm:p-4">
                <div className="flex items-center gap-3">
                  <Sparkles className="h-4 w-4 shrink-0 text-amber-700" />
                  <p className="text-sm font-medium leading-5 text-slate-900">Streaming AI responses</p>
                </div>
              </div>
              <div className="min-w-0 rounded-2xl border border-white/70 bg-white/80 p-3.5 shadow-sm sm:p-4">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-700" />
                  <p className="text-sm font-medium leading-5 text-slate-900">Public-access study workspace</p>
                </div>
              </div>
            </div>
            <div className="mt-6 flex flex-col gap-2.5 sm:mt-8 sm:flex-row sm:flex-wrap sm:gap-3">
              <Link href="/research">
                <Button className="min-h-11 w-full rounded-xl bg-slate-950 px-4 text-sm text-white hover:bg-slate-800 sm:min-h-12 sm:w-auto sm:text-base">
                  Try the live research flow
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline" className="min-h-11 w-full rounded-xl px-4 text-sm sm:min-h-12 sm:w-auto sm:text-base">
                  See the product workspace
                </Button>
              </Link>
            </div>
          </div>

          <div className="min-w-0 rounded-3xl border border-slate-200 bg-white/90 p-4 shadow-xl shadow-amber-100/30 sm:rounded-[2rem] sm:p-7">
            <div className="rounded-2xl bg-slate-950 p-4 text-white sm:rounded-[1.5rem] sm:p-6">
              <p className="text-sm text-slate-300">Promise</p>
              <p className="mt-2 text-lg font-semibold leading-6 sm:mt-3 sm:text-2xl sm:leading-8">
                India-first academic operating system
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-300 sm:mt-4">
                Start with research, notes, doubt solving, and document intelligence. Layer in
                accounts, governance, and monetization only after the core feels solid.
              </p>
            </div>
            <div className="mt-4 space-y-3 sm:mt-6 sm:space-y-4">
              {modules.map((module) => {
                const Icon = module.icon
                return (
                  <div
                    key={module.title}
                    className="min-w-0 rounded-2xl border border-slate-200 p-3.5 transition hover:-translate-y-0.5 hover:shadow-sm sm:rounded-[1.5rem] sm:p-4"
                  >
                    <div className="flex items-center gap-3">
                      <div className="shrink-0 rounded-xl bg-amber-100 p-2 text-amber-800">
                        <Icon className="h-4 w-4" />
                      </div>
                      <p className="font-medium leading-5 text-slate-900">{module.title}</p>
                    </div>
                    <p className="mt-2.5 text-sm leading-6 text-slate-600 sm:mt-3">{module.description}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </section>

        <footer className="border-t border-slate-200/80 py-6 text-sm leading-6 text-slate-500 sm:py-8">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
            <p className="max-w-3xl text-pretty">
              Scholr is an academic AI assistant for BTech students. Always verify outputs before
              using them in exams, projects, or submissions.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <Link href="/privacy" className="transition hover:text-slate-900">
                Privacy
              </Link>
              <Link href="/terms" className="transition hover:text-slate-900">
                Terms
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </main>
  )
}
