import { UserButton } from '@clerk/nextjs'
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

import DisclaimerBanner from '@/components/DisclaimerBanner'
import Sidebar from '@/components/Sidebar'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  if (clerkKey) {
    const { userId } = await auth()
    if (!userId) {
      redirect('/sign-in')
    }
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top_left,rgba(251,191,36,0.14),transparent_24%),linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] text-slate-950 lg:flex">
      <Sidebar />
      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8">
          {clerkKey ? (
            <div className="mb-4 flex justify-end">
              <UserButton />
            </div>
          ) : null}
          <DisclaimerBanner />
          {children}
        </div>
      </main>
    </div>
  )
}
