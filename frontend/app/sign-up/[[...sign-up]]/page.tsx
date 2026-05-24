import { SignUp } from '@clerk/nextjs'
import Link from 'next/link'

export default function SignUpPage() {
  if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6">
        <div className="max-w-md rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h1 className="text-2xl font-semibold text-slate-950">Sign up is not configured yet</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Scholr is currently running as a public-access MVP. Add Clerk environment keys to enable accounts.
          </p>
          <Link href="/dashboard" className="mt-6 inline-flex rounded-2xl bg-slate-950 px-5 py-3 text-sm font-medium text-white">
            Continue to dashboard
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50">
      <SignUp />
    </main>
  )
}
