import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/privacy',
  '/terms',
])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    // Only protect if Clerk is configured.
    if (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
      await auth.protect()
    }
  }
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
