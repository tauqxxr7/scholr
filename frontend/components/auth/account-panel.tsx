'use client'

import Link from 'next/link'
import { UserButton, useAuth, useUser } from '@clerk/nextjs'

export default function AccountPanel() {
  const { isSignedIn } = useAuth()
  const { user, isLoaded } = useUser()

  return (
    <div className="rounded-[1.5rem] border border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.9),rgba(255,255,255,0.98))] p-4 shadow-sm">
      {isSignedIn ? (
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Workspace</p>
            <p className="mt-1 truncate text-sm font-medium text-slate-900">
              {isLoaded
                ? user?.fullName || user?.primaryEmailAddress?.emailAddress || 'Signed in'
                : 'Loading account...'}
            </p>
            <p className="mt-1 text-xs leading-5 text-slate-500">
              Personal history, uploads, and semantic retrieval stay scoped to your account.
            </p>
          </div>
          <UserButton />
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Authentication</p>
          <p className="text-sm leading-6 text-slate-600">
            Sign in to keep your study history, documents, and usage quotas isolated to your workspace.
          </p>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Link
              href="/sign-in"
              className="inline-flex min-h-11 items-center justify-center rounded-2xl bg-slate-950 px-4 text-sm font-medium text-white transition hover:bg-slate-800"
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              className="inline-flex min-h-11 items-center justify-center rounded-2xl border border-slate-200 px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Create account
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
