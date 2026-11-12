import posthog from 'posthog-js'

let postHogInitialized = false

export function initPostHog() {
  if (typeof window === 'undefined') return
  if (!process.env.NEXT_PUBLIC_POSTHOG_KEY) return
  if (postHogInitialized) {
    posthog.opt_in_capturing()
    return
  }

  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com',
    capture_pageview: true,
    capture_pageleave: true,
    persistence: 'localStorage',
    opt_out_capturing_by_default: true,
  })
  postHogInitialized = true
  posthog.opt_in_capturing()
}

export function disablePostHog() {
  if (typeof window === 'undefined' || !postHogInitialized) return
  posthog.opt_out_capturing()
}

export function trackEvent(event: string, properties?: Record<string, unknown>) {
  if (typeof window === 'undefined' || !postHogInitialized) return
  if (posthog.has_opted_out_capturing()) return
  posthog.capture(event, properties)
}
