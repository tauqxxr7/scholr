'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  NotebookPen,
  Activity,
  Clock3,
  Database,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import type { HistoryItem } from '@/lib/api'
import { getHistory } from '@/lib/api'

const modules = [
  {
    href: '/research',
    title: 'Research',
    description: 'Papers, reading order, and practical research gaps.',
    icon: BookOpen,
  },
  {
    href: '/notes',
    title: 'Notes',
    description: 'Exam-ready notes with revision structure built in.',
    icon: NotebookPen,
  },
  {
    href: '/doubt',
    title: 'Doubt',
    description: 'Step-by-step explanations for hard engineering concepts.',
    icon: BrainCircuit,
  },
]

export default function DashboardPage() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [historyError, setHistoryError] = useState('')
  const [historyLoading, setHistoryLoading] = useState(true)

  useEffect(() => {
    getHistory(6)
      .then(setHistory)
      .catch(() => setHistoryError('History will appear here once the backend is reachable.'))
      .finally(() => setHistoryLoading(false))
  }, [])

  return (
    <div className="space-y-8 lg:space-y-10">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-[linear-gradient(135deg,rgba(254,243,199,0.9),rgba(255,255,255,0.98),rgba(224,242,254,0.95))] p-6 shadow-sm sm:p-8">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] xl:items-end">
          <div>
            <Badge className="rounded-full bg-white/90 px-3 py-1 text-slate-700 shadow-sm">
              India-first academic operating system
            </Badge>
            <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
              Build a lovable wedge first: research, notes, and doubt solving for BTech students.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
              Scholr is now live locally with streaming answers and saved history. This dashboard
              is our operating room for polishing the product into something demo-worthy.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
            <div className="rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-900">
                  <Activity className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Status</p>
                  <p className="mt-1 text-sm font-medium text-slate-900">Streaming MVP live</p>
                </div>
              </div>
            </div>
            <div className="rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-900">
                  <Database className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Storage</p>
                  <p className="mt-1 text-sm font-medium text-slate-900">SQLite history active</p>
                </div>
              </div>
            </div>
            <div className="rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-900">
                  <Clock3 className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Goal</p>
                  <p className="mt-1 text-sm font-medium text-slate-900">Pitch-ready polish</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {modules.map((module) => {
          const Icon = module.icon
          return (
            <Link
              key={module.href}
              href={module.href}
              className="group rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md sm:p-6"
            >
              <div className="flex items-center justify-between">
                <div className="rounded-2xl bg-amber-50 p-3 text-amber-800 transition group-hover:bg-slate-950 group-hover:text-white">
                  <Icon className="h-5 w-5" />
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400 transition group-hover:text-slate-900" />
              </div>
              <h2 className="mt-4 text-xl font-semibold text-slate-950">{module.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{module.description}</p>
              <p className="mt-5 text-sm font-medium text-slate-900">Open module</p>
            </Link>
          )
        })}
      </section>

      <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Recent history</h2>
            <p className="mt-1 text-sm text-slate-500">
              Every finished response is now stored locally in SQLite.
            </p>
          </div>
          <Badge variant="outline">{history.length} items</Badge>
        </div>

        {historyError ? (
          <div className="mt-6 rounded-[1.5rem] border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            {historyError}
          </div>
        ) : null}

        {historyLoading ? (
          <div className="mt-6 grid gap-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4"
              >
                <div className="h-4 w-20 rounded-full bg-slate-200" />
                <div className="mt-4 h-4 w-3/4 rounded-full bg-slate-200" />
                <div className="mt-3 space-y-2">
                  <div className="h-3 w-full rounded-full bg-slate-200" />
                  <div className="h-3 w-[88%] rounded-full bg-slate-200" />
                </div>
              </div>
            ))}
          </div>
        ) : history.length ? (
          <div className="mt-6 space-y-3">
            {history.map((item) => (
              <div
                key={item.id}
                className="rounded-[1.5rem] border border-slate-200 bg-slate-50/45 p-4 transition hover:border-slate-300 hover:bg-white"
              >
                <div className="flex flex-wrap items-center gap-3">
                  <Badge variant="outline" className="capitalize">
                    {item.module}
                  </Badge>
                  <span className="text-xs text-slate-400">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="mt-3 font-medium text-slate-900">{item.query}</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {item.response.length > 220 ? `${item.response.slice(0, 220)}...` : item.response}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-6 rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
            Generate your first research, notes, or doubt answer and it will appear here.
          </div>
        )}
      </section>
    </div>
  )
}
