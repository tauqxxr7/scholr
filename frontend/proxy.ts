import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse, type NextRequest } from 'next/server'

const clerkEnabled = Boolean(
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY,
)

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/research(.*)',
  '/notes(.*)',
  '/doubt(.*)',
  '/documents(.*)',
])

const enabledMiddleware = clerkMiddleware(
  async (auth, request) => {
    if (isProtectedRoute(request)) {
      await auth.protect()
    }
  },
  {
    frontendApiProxy: { enabled: true },
  },
)

const disabledMiddleware = (_request: NextRequest) => {
  void _request
  return NextResponse.next()
}

export default clerkEnabled ? enabledMiddleware : disabledMiddleware

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
