export const clerkPublishableKey =
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim() || ''

export const clerkEnabled = Boolean(clerkPublishableKey)
