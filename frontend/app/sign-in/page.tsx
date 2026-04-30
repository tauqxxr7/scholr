import Link from 'next/link'

export default function Page() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.16),transparent_26%),linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] px-4 py-10">
      <div className="mx-auto flex min-h-[80vh] max-w-2xl items-center justify-center">
        <div className="w-full rounded-[2rem] border border-slate-200 bg-white p-8 text-center shadow-sm sm:p-10">
          <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Scholr</p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">
            Sign in is intentionally paused
          </h1>
          <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">
            We removed auth for this milestone so the product demo stays stable. The current focus
            is the working Scholr Core flow: research, notes, doubt solving, and saved history.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Link
              href="/dashboard"
              className="inline-flex min-h-12 items-center justify-center rounded-2xl bg-slate-950 px-5 text-sm font-medium text-white transition hover:bg-slate-800"
            >
              Open dashboard
            </Link>
            <Link
              href="/"
              className="inline-flex min-h-12 items-center justify-center rounded-2xl border border-slate-200 px-5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Back to landing page
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
