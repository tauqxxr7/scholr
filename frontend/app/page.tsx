'use client'

import { FormEvent, useState } from 'react'
import Link from 'next/link'
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const studentBenefits = [
  {
    title: 'Saves 3 hours per topic',
    description: 'No more searching through 10 tabs. Get structured research guidance in one place.',
  },
  {
    title: 'Exam-ready in minutes',
    description: 'Notes formatted for university exams, not generic summaries.',
  },
  {
    title: 'Free, always',
    description: 'Core features are free forever. No credit card. No hidden limits.',
  },
]

export default function LandingPage() {
  const [waitlistEmail, setWaitlistEmail] = useState('')
  const [waitlistHoneypot, setWaitlistHoneypot] = useState('')
  const [waitlistStatus, setWaitlistStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const handleWaitlistSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!waitlistEmail.trim()) {
      return
    }

    setWaitlistStatus('loading')
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '')
      if (!apiUrl) {
        throw new Error('Missing API URL')
      }

      const response = await fetch(`${apiUrl}/api/waitlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: waitlistEmail.trim(), honeypot: waitlistHoneypot }),
      })

      if (!response.ok) {
        throw new Error('Waitlist request failed')
      }

      setWaitlistStatus('success')
    } catch {
      setWaitlistStatus('error')
    }
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.22),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(125,211,252,0.18),_transparent_26%),linear-gradient(180deg,#fffdf7_0%,#ffffff_55%,#f8fafc_100%)]">
      <div className="mx-auto max-w-6xl px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
        <nav className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Scholr</p>
            <p className="mt-1.5 max-w-[20rem] text-sm font-semibold leading-5 text-slate-950 sm:mt-2 sm:max-w-none sm:text-lg">
              AI study workspace for BTech students
            </p>
          </div>
          <div className="grid w-full min-w-0 grid-cols-2 gap-2 sm:flex sm:w-auto sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
            <Link href="/research" className="min-w-0">
              <Button variant="outline" className="min-h-10 w-full rounded-xl px-3 text-sm sm:min-h-11 sm:w-auto">
                Try Scholr free — no signup needed
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
            <h1 className="mt-4 max-w-[18ch] text-balance text-[clamp(2rem,8vw,2.45rem)] font-semibold leading-[1.05] text-slate-950 sm:mt-5 sm:max-w-4xl sm:text-[clamp(3rem,6vw,4.35rem)] sm:leading-[1.02] lg:text-[clamp(3.55rem,5vw,4.75rem)]">
              Turn any BTech topic into exam-ready notes, research direction, and doubt solving.
            </h1>
            <p className="mt-4 max-w-[34rem] text-pretty text-[clamp(0.95rem,3.6vw,1.05rem)] leading-6 text-slate-600 sm:mt-5 sm:text-[1.08rem] sm:leading-7">
              Free for every BTech student. Get research papers, exam notes, and doubt solving in 60 seconds.
            </p>
            <div className="mt-5 grid gap-2.5 sm:mt-6 sm:max-w-xl sm:grid-cols-2 sm:gap-3">
              <div className="min-w-0 rounded-2xl border border-white/70 bg-white/80 p-3.5 shadow-sm sm:p-4">
                <div className="flex items-center gap-3">
                  <Sparkles className="h-4 w-4 shrink-0 text-amber-700" />
                  <p className="text-sm font-medium leading-5 text-slate-900">No signup needed</p>
                </div>
              </div>
              <div className="min-w-0 rounded-2xl border border-white/70 bg-white/80 p-3.5 shadow-sm sm:p-4">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-700" />
                  <p className="text-sm font-medium leading-5 text-slate-900">Results in 60 seconds</p>
                </div>
              </div>
            </div>
            <div className="mt-6 flex flex-col gap-2.5 sm:mt-8 sm:flex-row sm:flex-wrap sm:gap-3">
              <Link href="/research">
                <Button className="min-h-11 w-full rounded-xl bg-slate-950 px-4 text-sm text-white hover:bg-slate-800 sm:min-h-12 sm:w-auto sm:text-base">
                  Try Scholr free — no signup needed
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline" className="min-h-11 w-full rounded-xl px-4 text-sm sm:min-h-12 sm:w-auto sm:text-base">
                  Open dashboard
                </Button>
              </Link>
            </div>
          </div>

          <div className="min-w-0 rounded-3xl border border-slate-200 bg-white/90 p-4 shadow-xl shadow-amber-100/30 sm:rounded-[2rem] sm:p-7">
            <div className="rounded-2xl bg-slate-950 p-4 text-white sm:rounded-[1.5rem] sm:p-6">
              <p className="text-sm text-slate-300">Why students use Scholr</p>
              <p className="mt-2 text-lg font-semibold leading-6 sm:mt-3 sm:text-2xl sm:leading-8">
                Study faster without losing academic structure.
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-300 sm:mt-4">
                Designed for BTech students who need fast, exam-useful answers instead of generic
                chatbot paragraphs.
              </p>
            </div>
            <div className="mt-4 space-y-3 sm:mt-6 sm:space-y-4">
              {studentBenefits.map((benefit) => (
                <div
                  key={benefit.title}
                  className="min-w-0 rounded-2xl border border-slate-200 p-3.5 transition hover:-translate-y-0.5 hover:shadow-sm sm:rounded-[1.5rem] sm:p-4"
                >
                  <p className="font-medium leading-5 text-slate-900">{benefit.title}</p>
                  <p className="mt-2.5 text-sm leading-6 text-slate-600 sm:mt-3">{benefit.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16 px-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold text-gray-900 text-center mb-10">Why students use Scholr</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="bg-white border rounded-xl p-6">
              <p className="font-medium text-gray-900 mb-2">Saves 3 hours per topic</p>
              <p className="text-sm text-gray-500">No more searching through 10 tabs. Get structured research guidance in one place.</p>
            </div>
            <div className="bg-white border rounded-xl p-6">
              <p className="font-medium text-gray-900 mb-2">Exam-ready in minutes</p>
              <p className="text-sm text-gray-500">Notes formatted for university exams, not generic summaries.</p>
            </div>
            <div className="bg-white border rounded-xl p-6">
              <p className="font-medium text-gray-900 mb-2">Free, always</p>
              <p className="text-sm text-gray-500">Core features are free forever. No credit card. No hidden limits.</p>
            </div>
          </div>
        </section>

        <section className="grid gap-3 pb-8 sm:grid-cols-3 sm:gap-4 sm:pb-12">
          {[
            {
              step: '1',
              title: 'Type your topic',
              description: 'Enter any BTech subject, concept, or question.',
            },
            {
              step: '2',
              title: 'AI generates instantly',
              description: 'Scholr streams a structured academic answer in seconds.',
            },
            {
              step: '3',
              title: 'Copy, save, or export',
              description: 'Use the output in your notes, report, or revision.',
            },
          ].map((item) => (
            <div key={item.step} className="rounded-2xl border border-white/70 bg-white/80 p-4 shadow-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-950 text-sm font-semibold text-white">
                {item.step}
              </div>
              <h2 className="mt-4 text-lg font-semibold text-slate-950">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
            </div>
          ))}
        </section>

        <section className="pb-8 sm:pb-12">
          <p className="mb-4 text-sm font-medium text-slate-500">What students say</p>
          <div className="grid gap-3 sm:grid-cols-3 sm:gap-4">
            {
              // TODO: Replace with real student quotes after validation
              [
                {
                  quote:
                    'Finally a tool that gives me actual paper recommendations, not just Google Scholar links.',
                  byline: 'BTech CS student, Mumbai',
                },
                {
                  quote: 'Generated revision notes for my OS exam in 3 minutes. Actually useful.',
                  byline: 'BTech IT student, Pune',
                },
                {
                  quote: 'The doubt solver explained virtual memory better than my textbook.',
                  byline: 'BTech ECE student, Bangalore',
                },
              ].map((item) => (
                <div key={item.byline} className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
                  <p className="text-sm italic leading-6 text-slate-700">&ldquo;{item.quote}&rdquo;</p>
                  <p className="mt-4 text-xs font-medium text-slate-500">{item.byline}</p>
                </div>
              ))
            }
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm sm:rounded-[2rem] sm:p-7">
          <div className="grid gap-5 lg:grid-cols-[1fr_0.95fr] lg:items-center">
            <div>
              <Badge className="rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-800">
                Product updates
              </Badge>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
                Get notified when we launch new features
              </h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
                Join the early Scholr list for document intelligence, export workflows, and better exam-prep tools.
              </p>
            </div>
            {waitlistStatus === 'success' ? (
              <div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4 text-sm font-medium leading-6 text-emerald-800">
                You&apos;re on the list! We&apos;ll keep you updated.
              </div>
            ) : (
              <form onSubmit={handleWaitlistSubmit} className="space-y-3">
                <div className="flex flex-col gap-2 sm:flex-row">
                  <input
                    name="honeypot"
                    value={waitlistHoneypot}
                    onChange={(event) => setWaitlistHoneypot(event.target.value)}
                    tabIndex={-1}
                    autoComplete="off"
                    className="absolute -left-[9999px] h-px w-px"
                    aria-hidden="true"
                  />
                  <input
                    type="email"
                    value={waitlistEmail}
                    onChange={(event) => setWaitlistEmail(event.target.value)}
                    placeholder="you@example.com"
                    className="min-h-11 flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:bg-white"
                    required
                  />
                  <Button
                    type="submit"
                    disabled={waitlistStatus === 'loading'}
                    className="min-h-11 rounded-xl bg-slate-950 px-5 text-sm text-white hover:bg-slate-800"
                  >
                    {waitlistStatus === 'loading' ? 'Joining...' : 'Notify me'}
                  </Button>
                </div>
                {waitlistStatus === 'error' ? (
                  <p className="text-sm text-red-600">Something went wrong. Please try again.</p>
                ) : null}
              </form>
            )}
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
              <Link href="/status" className="transition hover:text-slate-900">
                Status
              </Link>
              <Link href="/changelog" className="transition hover:text-slate-900">
                Changelog
              </Link>
              <Link href="/feedback" className="transition hover:text-slate-900">
                Feedback
              </Link>
              <Link href="/topics" className="transition hover:text-slate-900">
                Browse topics
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </main>
  )
}


