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
  FileText,
  Share2,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { SkeletonCard } from '@/components/ui/skeleton-card'
import { trackEvent } from '@/lib/analytics'
import type { HistoryItem, MetricsResult, SearchResultItem } from '@/lib/api'
import { getHistory, getHistoryExportUrl, getMetrics, searchHistory } from '@/lib/api'

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
  {
    href: '/documents',
    title: 'Documents',
    description: 'Upload PDFs, ask grounded questions, and study from cited evidence.',
    icon: FileText,
  },
]

function DashboardPageContent() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [historyError, setHistoryError] = useState('')
  const [historyLoading, setHistoryLoading] = useState(true)
  const [hasUsedBefore, setHasUsedBefore] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [metrics, setMetrics] = useState<MetricsResult | null>(null)
  const [metricsLoading, setMetricsLoading] = useState(true)
  const [shareStatus, setShareStatus] = useState('')
  const isSearching = searchQuery.trim().length > 0
  const historyExportUrl = history.length > 0 ? getHistoryExportUrl() : ''

  useEffect(() => {
    setHasUsedBefore(localStorage.getItem('scholr_has_used') === 'true')
  }, [])

  useEffect(() => {
    const recordValidationSession = async () => {
      if (localStorage.getItem('scholr_validation_recorded') === 'true') {
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, '')
      if (!apiUrl) {
        return
      }

      try {
        const response = await fetch(`${apiUrl}/api/validation/session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ referred_by: document.referrer || 'direct' }),
        })

        if (response.ok) {
          localStorage.setItem('scholr_validation_recorded', 'true')
        }
      } catch {
        // Silent validation tracking should never interrupt the dashboard.
      }
    }

    void recordValidationSession()
  }, [])

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const items = await getHistory(6, 1)
        setHistory(items)
      } catch {
        setHistoryError('History will appear here once the backend is reachable.')
      } finally {
        setHistoryLoading(false)
      }
    }

    void loadHistory()
  }, [])

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        setMetrics(await getMetrics())
      } catch {
        setMetrics(null)
      } finally {
        setMetricsLoading(false)
      }
    }

    void loadMetrics()
  }, [])

  useEffect(() => {
    const query = searchQuery.trim()
    if (!query) {
      setSearchResults([])
      setSearchLoading(false)
      return
    }

    setSearchLoading(true)
    const timer = window.setTimeout(async () => {
      try {
        const results = await searchHistory(query)
        setSearchResults(results)
      } catch {
        setSearchResults([])
      } finally {
        setSearchLoading(false)
      }
    }, 400)

    return () => window.clearTimeout(timer)
  }, [searchQuery])

  const showOnboarding = !historyLoading && history.length === 0 && hasUsedBefore === false
  const showHistoryList = !historyLoading && !showOnboarding

  const handleShareScholr = async () => {
    const shareData = {
      title: 'Scholr — AI study tool',
      text: 'Free AI tool for BTech students — research papers, notes, and doubt solving in 60 seconds. No signup needed.',
      url: 'https://scholr-coral.vercel.app',
    }

    try {
      if (navigator.share) {
        await navigator.share(shareData)
        setShareStatus('Shared!')
      } else {
        await navigator.clipboard.writeText(shareData.url)
        setShareStatus('Link copied!')
      }
    } catch {
      await navigator.clipboard.writeText(shareData.url)
      setShareStatus('Link copied!')
    }

    window.setTimeout(() => setShareStatus(''), 1800)
  }

  const onboardingCards = (
    <div className="mt-6 rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50 p-5 sm:p-7">
      <div className="text-center">
        <h3 className="text-2xl font-semibold tracking-tight text-slate-950">Welcome to Scholr</h3>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Here is how to get started in 60 seconds
        </p>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {[
          {
            href: '/research',
            title: 'Find research papers',
            description: 'Discover key papers, reading order, and research gaps for your project',
            label: 'Research',
          },
          {
            href: '/notes',
            title: 'Generate study notes',
            description: 'Create structured revision notes for any BTech topic in seconds',
            label: 'Notes',
          },
          {
            href: '/doubt',
            title: 'Solve a doubt',
            description: 'Get step-by-step explanations for any engineering concept',
            label: 'Doubt',
          },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="rounded-[1.5rem] border border-slate-200 bg-white p-4 transition hover:-translate-y-0.5 hover:shadow-sm"
          >
            <Badge variant="outline">{item.label}</Badge>
            <h4 className="mt-4 text-lg font-semibold text-slate-950">{item.title}</h4>
            <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )

  return (
    <div className="space-y-8 lg:space-y-10">
      <section className="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-[linear-gradient(135deg,rgba(254,243,199,0.9),rgba(255,255,255,0.98),rgba(224,242,254,0.95))] p-5 shadow-sm sm:rounded-[2rem] sm:p-8">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] xl:items-end">
          <div>
            <Badge className="rounded-full bg-white/90 px-3 py-1 text-slate-700 shadow-sm">
              India-first academic operating system
            </Badge>
            <h1 className="mt-4 max-w-3xl text-[2.2rem] font-semibold tracking-tight text-slate-950 sm:text-5xl">
              Build a lovable wedge first: research, notes, and doubt solving for BTech students.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
              Scholr is live across devices with streaming answers and saved history. This
              dashboard is our operating room for keeping the product fast, readable, and
              demo-worthy.
            </p>
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={handleShareScholr}
                className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:text-slate-950"
              >
                <Share2 className="h-4 w-4" />
                Share Scholr
              </button>
              {shareStatus ? (
                <span className="text-sm font-medium text-emerald-700">{shareStatus}</span>
              ) : null}
            </div>
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
                  <p className="mt-1 text-sm font-medium text-slate-900">History storage active</p>
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

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {modules.map((module) => {
          const Icon = module.icon
          return (
            <Link
              key={module.href}
              href={module.href}
              onClick={() =>
                trackEvent('module_opened', {
                  module: module.title.toLowerCase(),
                  entrypoint: 'dashboard',
                })
              }
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

      {metricsLoading ? (
        <section className="flex flex-wrap gap-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <span
              key={index}
              className="h-8 w-32 animate-pulse rounded-full border border-slate-200 bg-white"
            />
          ))}
        </section>
      ) : metrics ? (
        <section className="flex flex-wrap gap-2">
          <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-600">
            {metrics.searches.total} total queries
          </span>
          <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-600">
            {metrics.searches.last_7d} this week
          </span>
          <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-600">
            {metrics.feedback.total} feedback given
          </span>
        </section>
      ) : null}

      <section className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm sm:rounded-[2rem] sm:p-7">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Recent history</h2>
            <p className="mt-1 text-sm text-slate-500">
              Every finished response is stored in the active backend database for quick review.
            </p>
          </div>
          {showHistoryList && history.length > 0 ? <Badge variant="outline">{history.length} items</Badge> : null}
        </div>

        <div className="mt-5">
          <div className="relative">
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search your history..."
              className="min-h-11 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 pr-11 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:bg-white"
            />
            {searchLoading ? (
              <span className="absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
            ) : null}
          </div>
        </div>

        {historyError ? (
          <div className="mt-6 rounded-[1.5rem] border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            {historyError}
          </div>
        ) : null}

        {isSearching ? (
          <div className="mt-6 space-y-3">
            {searchLoading ? (
              <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                Searching history...
              </div>
            ) : searchResults.length ? (
              searchResults.map((item) => (
                <div
                  key={item.id}
                  className="rounded-[1.5rem] border border-slate-200 bg-slate-50/45 p-4 transition hover:border-slate-300 hover:bg-white"
                >
                  <div className="flex flex-wrap items-center gap-3">
                    <Badge variant="outline" className="capitalize">
                      {item.module}
                    </Badge>
                    <span className="text-xs text-slate-400">
                      {Math.round(item.score * 100)}% match
                    </span>
                  </div>
                  <p className="mt-3 font-medium text-slate-900">{item.query}</p>
                </div>
              ))
            ) : (
              <div className="rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
                No matching history found
              </div>
            )}
          </div>
        ) : historyLoading ? (
          <div className="mt-6 grid gap-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <SkeletonCard key={index} lines={3} />
            ))}
          </div>
        ) : showHistoryList ? (
          <div className="mt-6 space-y-3">
            {history.length ? (
              <>
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
                <a
                  href={historyExportUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex text-sm font-medium text-slate-500 transition hover:text-slate-900"
                >
                  Export history as CSV
                </a>
              </>
            ) : (
              <div className="rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
                Generate your next research, notes, or doubt answer and it will appear here.
              </div>
            )}
          </div>
        ) : onboardingCards}
      </section>
    </div>
  )
}

export default function DashboardPage() {
  return <DashboardPageContent />
}
