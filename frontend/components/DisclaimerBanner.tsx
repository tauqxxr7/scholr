'use client'

import { useEffect, useState } from 'react'

const STORAGE_KEY = 'scholr_ai_disclaimer_dismissed'

export default function DisclaimerBanner() {
  const [visible, setVisible] = useState<boolean | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setVisible(sessionStorage.getItem(STORAGE_KEY) !== 'true')
    }, 0)

    return () => window.clearTimeout(timer)
  }, [])

  if (visible !== true) {
    return null
  }

  const dismiss = () => {
    sessionStorage.setItem(STORAGE_KEY, 'true')
    setVisible(false)
  }

  return (
    <div className="mb-4 flex items-start justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm">
      <p className="leading-6">
        Scholr uses AI to generate academic content. Always verify before submitting to exams or
        projects.
      </p>
      <button
        type="button"
        onClick={dismiss}
        aria-label="Dismiss AI disclaimer"
        className="rounded-full px-2 text-base leading-6 text-amber-800 transition hover:bg-amber-100 hover:text-amber-950"
      >
        ×
      </button>
    </div>
  )
}
