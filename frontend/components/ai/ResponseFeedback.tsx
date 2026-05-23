'use client'

import { useState } from 'react'
import { ThumbsDown, ThumbsUp } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { trackEvent } from '@/lib/analytics'
import { submitFeedback } from '@/lib/api'

type ResponseFeedbackProps = {
  module: 'research' | 'notes' | 'doubt'
  query: string
  responseLength: number
}

export default function ResponseFeedback({ module, query, responseLength }: ResponseFeedbackProps) {
  const [submitted, setSubmitted] = useState(false)
  const [sending, setSending] = useState(false)

  const handleFeedback = async (rating: 'helpful' | 'not_helpful') => {
    if (submitted || sending) {
      return
    }

    setSending(true)
    try {
      await submitFeedback({
        module,
        query,
        rating,
        response_length: responseLength,
      })
      trackEvent('feedback_submitted', {
        module,
        rating,
        response_length: responseLength,
      })
      setSubmitted(true)
    } finally {
      setSending(false)
    }
  }

  if (submitted) {
    return (
      <p className="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
        Thanks for the feedback
      </p>
    )
  }

  return (
    <div className="mt-5 flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-slate-600">Was this response useful?</p>
      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={sending}
          onClick={() => handleFeedback('helpful')}
          className="rounded-xl border-slate-200 bg-white text-slate-700"
        >
          <ThumbsUp className="mr-2 h-3.5 w-3.5" />
          Helpful
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={sending}
          onClick={() => handleFeedback('not_helpful')}
          className="rounded-xl border-slate-200 bg-white text-slate-700"
        >
          <ThumbsDown className="mr-2 h-3.5 w-3.5" />
          Not helpful
        </Button>
      </div>
    </div>
  )
}
