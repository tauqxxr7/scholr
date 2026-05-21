'use client'

import { ClerkProvider } from '@clerk/nextjs'

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY)

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  if (!clerkEnabled) {
    return <>{children}</>
  }

  return (
    <ClerkProvider
      dynamic
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
    >
      {children}
    </ClerkProvider>
  )
}
