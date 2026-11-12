'use client'

import { useEffect } from 'react'
import CookieConsent, { readAnalyticsConsent } from '@/components/CookieConsent'
import { initPostHog, disablePostHog } from '@/lib/posthog'

export default function PostHogProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const applyConsent = () => {
      if (readAnalyticsConsent() === 'accepted') {
        initPostHog()
      } else {
        disablePostHog()
      }
    }
    applyConsent()
    window.addEventListener('scholr:consent-change', applyConsent)
    return () => window.removeEventListener('scholr:consent-change', applyConsent)
  }, [])

  return <>{children}<CookieConsent /></>
}
