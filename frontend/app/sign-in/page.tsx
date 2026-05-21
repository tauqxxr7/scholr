import Link from 'next/link'
import { SignIn } from '@clerk/nextjs'

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY)

export default function Page() {
  if (!clerkEnabled) {
    return (
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.16),transparent_26%),linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] px-4 py-10">
        <div className="mx-auto flex min-h-[80vh] max-w-2xl items-center justify-center">
          <div className="w-full rounded-[2rem] border border-slate-200 bg-white p-8 text-center shadow-sm sm:p-10">
            <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Scholr</p>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">
              Authentication is ready for configuration
            </h1>
            <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">
              Add Clerk environment variables to enable Google, Microsoft, Apple, and email OTP
              sign-in across Scholr.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Link
                href="/"
                className="inline-flex min-h-12 items-center justify-center rounded-2xl bg-slate-950 px-5 text-sm font-medium text-white transition hover:bg-slate-800"
              >
                Back to landing page
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.16),transparent_26%),linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] px-4 py-10">
      <div className="mx-auto flex min-h-[80vh] max-w-6xl flex-col items-center justify-center gap-8 lg:flex-row lg:items-stretch">
        <div className="w-full max-w-xl rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
          <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Scholr</p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">
            Sign in to your academic workspace
          </h1>
          <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">
            Continue with Google, Microsoft, Apple, or email OTP to unlock personal history,
            document ownership, and tenant-safe AI workflows.
          </p>
          <div className="mt-8 grid gap-3 text-sm text-slate-600">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
              Personal history and document ownership
            </div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
              Isolated retrieval and semantic indexing
            </div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
              Mobile-safe session persistence across study sessions
            </div>
          </div>
        </div>
        <div className="w-full max-w-md rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <SignIn
            path="/sign-in"
            routing="path"
            signUpUrl="/sign-up"
            fallbackRedirectUrl="/dashboard"
            forceRedirectUrl="/dashboard"
          />
        </div>
      </div>
    </div>
  )
}
