'use client'

import { ClerkProvider } from '@clerk/nextjs'
import { clerkEnabled } from '@/lib/auth-config'


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
