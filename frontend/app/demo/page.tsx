import Link from 'next/link'
import { Metadata } from 'next'
import { ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Scholr Live Demo',
  description: 'Curated Scholr demo flows for hackathons, investors, and college faculty.',
}

const scenarios = [
  {
    label: 'Research',
    title: 'Find research papers instantly',
    prompt: 'Machine learning techniques for diabetes prediction using patient data',
    href: `/research?topic=${encodeURIComponent(
      'Machine learning techniques for diabetes prediction using patient data',
    )}`,
  },
  {
    label: 'Notes',
    title: 'Generate exam-ready notes',
    prompt: 'Operating System process scheduling algorithms',
    href: `/notes?topic=${encodeURIComponent('Operating System process scheduling algorithms')}`,
  },
  {
    label: 'Doubt',
    title: 'Solve an engineering doubt',
    prompt: 'What is the difference between process and thread in operating systems?',
    href: `/doubt?question=${encodeURIComponent(
      'What is the difference between process and thread in operating systems?',
    )}`,
  },
]

const stack = ['Next.js', 'FastAPI', 'Python', 'TypeScript', 'Gemini', 'OpenRouter']

export default function DemoPage() {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#fffdf7_0%,#ffffff_55%,#f8fafc_100%)] px-5 py-12 text-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <section className="rounded-[2rem] border border-slate-200 bg-white/90 p-6 shadow-sm sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-amber-700">
            Curated pitch flow
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
            Scholr - Live Demo
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
            AI academic platform for BTech students. Built by Tauqeer Bharde.
          </p>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-3">
          {scenarios.map((scenario) => (
            <article
              key={scenario.label}
              className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800">
                {scenario.label}
              </span>
              <h2 className="mt-4 text-xl font-semibold text-slate-950">{scenario.title}</h2>
              <p className="mt-3 min-h-20 text-sm leading-6 text-slate-600">{scenario.prompt}</p>
              <Link
                href={scenario.href}
                className="mt-5 inline-flex min-h-11 items-center rounded-xl bg-slate-950 px-4 text-sm font-medium text-white transition hover:bg-slate-800"
              >
                Run this demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </article>
          ))}
        </section>

        <section className="mt-8 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Technical Architecture</h2>
            <pre className="mt-4 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-sm leading-7 text-slate-100">
{`Frontend -> SSE stream -> runtime mode detector
  -> AI provider / fallback engine
  -> history/cache -> document intelligence`}
            </pre>
          </div>
          <div className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Live endpoints</h2>
            <div className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
              <p>
                Frontend:{' '}
                <a className="font-medium text-slate-950 underline" href="https://scholr-coral.vercel.app">
                  scholr-coral.vercel.app
                </a>
              </p>
              <p>
                Backend health:{' '}
                <a className="font-medium text-slate-950 underline" href="https://scholr-k9sj.onrender.com/health">
                  /health
                </a>
              </p>
              <p>
                Evidence:{' '}
                <a className="font-medium text-slate-950 underline" href="https://scholr-k9sj.onrender.com/api/evidence">
                  /api/evidence
                </a>
              </p>
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap gap-2">
            {stack.map((item) => (
              <span key={item} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-700">
                {item}
              </span>
            ))}
          </div>
          <p className="mt-5 text-sm font-medium text-slate-600">
            29 backend tests passing. CI green. Deployed on Vercel + Render.
          </p>
        </section>
      </div>
    </main>
  )
}
