import posthog from 'posthog-js'

let postHogInitialized = false

export function initPostHog() {
  if (typeof window === 'undefined') return
  if (!process.env.NEXT_PUBLIC_POSTHOG_KEY) return
  if (postHogInitialized) return

  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com',
    capture_pageview: true,
    capture_pageleave: true,
  })
  postHogInitialized = true
}

export function trackEvent(event: string, properties?: Record<string, unknown>) {
  if (typeof window === 'undefined') return
  posthog.capture(event, properties)
}
