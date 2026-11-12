'use client'

import { useEffect, useState } from 'react'

const CONSENT_KEY = 'scholr.analytics-consent.v1'

type Consent = 'accepted' | 'rejected'

export function readAnalyticsConsent(): Consent | null {
  if (typeof window === 'undefined') return null
  try {
    const value = window.localStorage.getItem(CONSENT_KEY)
    return value === 'accepted' || value === 'rejected' ? value : null
  } catch {
    return null
  }
}

export default function CookieConsent() {
  const [choice, setChoice] = useState<Consent | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setChoice(readAnalyticsConsent())
    setReady(true)
  }, [])

  function decide(value: Consent) {
    try {
      window.localStorage.setItem(CONSENT_KEY, value)
    } catch {
      // Consent is still respected for this session when storage is blocked.
    }
    setChoice(value)
    window.dispatchEvent(new Event('scholr:consent-change'))
  }

  if (!ready || choice) return null

  return (
    <aside
      role="dialog"
      aria-modal="false"
      aria-label="Analytics privacy choices"
      className="fixed bottom-4 left-4 right-4 z-[100] mx-auto max-w-xl rounded-2xl border border-slate-700 bg-slate-950 p-5 text-slate-100 shadow-2xl"
    >
      <p className="text-base font-semibold">Your privacy matters</p>
      <p className="mt-2 text-sm text-slate-300">
        Scholr uses essential storage to operate. Optional analytics help us improve
        the study experience. Analytics stay off unless you accept.
      </p>
      <div className="mt-4 flex flex-wrap gap-3">
        <button type="button" onClick={() => decide('rejected')} className="rounded-lg border border-slate-500 px-4 py-2 text-sm">
          Reject optional analytics
        </button>
        <button type="button" onClick={() => decide('accepted')} className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950">
          Accept analytics
        </button>
      </div>
    </aside>
  )
}
