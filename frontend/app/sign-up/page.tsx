import Link from 'next/link'

export default function Page() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(125,211,252,0.16),transparent_26%),linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] px-4 py-10">
      <div className="mx-auto flex min-h-[80vh] max-w-2xl items-center justify-center">
        <div className="w-full rounded-[2rem] border border-slate-200 bg-white p-8 text-center shadow-sm sm:p-10">
          <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Scholr</p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">
            Sign up comes after the core loop
          </h1>
          <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">
            We are keeping Scholr focused on the MVP wedge first. Once deployment and product
            stability are locked in, auth and user accounts will return cleanly.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Link
              href="/dashboard"
              className="inline-flex min-h-12 items-center justify-center rounded-2xl bg-slate-950 px-5 text-sm font-medium text-white transition hover:bg-slate-800"
            >
              Explore the product
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
