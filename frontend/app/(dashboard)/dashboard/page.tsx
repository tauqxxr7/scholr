'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowRight, BookOpen, BrainCircuit, NotebookPen } from 'lucide-react'

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

  useEffect(() => {
    getHistory(6)
      .then(setHistory)
      .catch(() => setHistoryError('History will appear here once the backend is reachable.'))
  }, [])

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-slate-200 bg-gradient-to-br from-amber-100 via-white to-sky-100 p-8 shadow-sm">
        <Badge className="rounded-full bg-white/90 px-3 py-1 text-slate-700 shadow-sm">
          India-first academic operating system
        </Badge>
        <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-slate-950">
          Build a lovable wedge first: research, notes, and doubt solving for BTech students.
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-600">
          Scholr is now live locally with streaming answers and saved history. This dashboard is
          our operating room for polishing the product into something demo-worthy.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {modules.map((module) => {
          const Icon = module.icon
          return (
            <Link
              key={module.href}
              href={module.href}
              className="group rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <div className="rounded-2xl bg-slate-100 p-3 text-slate-900">
                  <Icon className="h-5 w-5" />
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400 transition group-hover:text-slate-900" />
              </div>
              <h2 className="mt-4 text-xl font-semibold text-slate-950">{module.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{module.description}</p>
            </Link>
          )
        })}
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
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
          <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            {historyError}
          </div>
        ) : null}

        {history.length ? (
          <div className="mt-6 space-y-3">
            {history.map((item) => (
              <div key={item.id} className="rounded-2xl border border-slate-200 p-4">
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
          <div className="mt-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
            Generate your first research, notes, or doubt answer and it will appear here.
          </div>
        )}
      </section>
    </div>
  )
}
