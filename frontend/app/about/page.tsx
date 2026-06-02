import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About Scholr — AI Study Tool for BTech Students',
  description:
    'The story behind Scholr, a free AI study tool for BTech students built by Tauqeer Bharde.',
}

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#fffdf7_0%,#ffffff_55%,#f8fafc_100%)] px-6 py-16">
      <section className="mx-auto max-w-3xl">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">About Scholr</p>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
          Built for BTech students who need useful academic help fast.
        </h1>
        <p className="mt-5 text-base leading-7 text-slate-600">
          Scholr is a free AI study tool for engineering students. It turns topics, doubts, and PDFs
          into structured research direction, exam-ready notes, and cited document answers without
          forcing students through signup before they can learn.
        </p>
      </section>

      <section className="mx-auto mt-12 grid max-w-4xl gap-5 md:grid-cols-2">
        <div className="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Why it exists</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Most students bounce between search results, random videos, and generic chatbot answers.
            Scholr focuses on BTech workflows: research papers, high-yield revision notes, doubt
            solving, and document-grounded answers with citations.
          </p>
        </div>
        <div className="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Who built it</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Scholr was created by Tauqeer Bharde, a BTech AI and Data Science student building
            production AI systems for real student problems across India.
          </p>
        </div>
        <div className="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Technical focus</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The platform uses a Next.js frontend, FastAPI backend, SSE streaming, OpenRouter AI
            generation, fallback recovery, response caching, and document retrieval with citations.
          </p>
        </div>
        <div className="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">What comes next</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The roadmap is PostgreSQL persistence, stronger semantic retrieval, student validation,
            syllabus-aware generation, and Azure-backed production infrastructure.
          </p>
        </div>
      </section>

      <section className="mx-auto mt-12 max-w-3xl rounded-[1.5rem] border border-amber-200 bg-amber-50 p-6">
        <h2 className="text-lg font-semibold text-amber-950">Try the product</h2>
        <p className="mt-2 text-sm leading-6 text-amber-900">
          Scholr is public-access today. Start with a topic, generate a short answer, and send
          feedback if something feels confusing.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            href="/research"
            className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Try Scholr free
          </Link>
          <Link
            href="/feedback"
            className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium text-amber-950 transition hover:border-amber-400"
          >
            Share feedback
          </Link>
        </div>
      </section>
    </main>
  )
}
