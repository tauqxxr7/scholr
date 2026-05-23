type ScholrEventName =
  | 'module_opened'
  | 'search_started'
  | 'search_completed'
  | 'search_failed'
  | 'generation_started'
  | 'generation_completed'
  | 'generation_failed'
  | 'document_upload_started'
  | 'document_upload_completed'
  | 'document_upload_failed'
  | 'document_answer_started'
  | 'document_answer_completed'
  | 'document_answer_failed'
  | 'first_token_received'
  | 'fallback_activated'
  | 'cache_hydrated'
  | 'provider_recovery_success'
  | 'partial_output_recovered'
  | 'copy_clicked'
  | 'clear_clicked'
  | 'retry_clicked'
  | 'feedback_submitted'

type ScholrEventPayload = {
  module?: string
  query?: string
  success?: boolean
  response_length?: number
  output_length?: number
  duration_ms?: number
  completion_ms?: number
  first_token_ms?: number
  error_category?: string
  error?: string
  rating?: string
  entrypoint?: string
  mode?: string
  retrieval_mode?: string
  cache_source?: string
  first_token_latency_ms?: number
  frontend_stream_parse_latency_ms?: number
  request_sequence?: 'first' | 'second_or_later'
  response_mode?: 'fast' | 'deep'
  output_token_estimate?: number
  citations_count?: number
  upload_pages?: number
  chunk_count?: number
  timestamp?: string
}

const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY?.trim() || ''
const posthogHost = process.env.NEXT_PUBLIC_POSTHOG_HOST?.trim() || ''

let posthogInstancePromise: Promise<{ capture: (event: string, payload: ScholrEventPayload) => void } | null> | null =
  null

function isAnalyticsEnabled() {
  return typeof window !== 'undefined' && Boolean(posthogKey && posthogHost)
}

async function getPostHog() {
  if (!isAnalyticsEnabled()) {
    return null
  }

  if (!posthogInstancePromise) {
    posthogInstancePromise = import('posthog-js')
      .then(({ default: posthog }) => {
        if (!posthog.__loaded) {
          posthog.init(posthogKey, {
            api_host: posthogHost,
            capture_pageview: false,
            capture_pageleave: false,
            autocapture: false,
            persistence: 'localStorage+cookie',
            person_profiles: 'never',
          })
        }

        return posthog
      })
      .catch(() => null)
  }

  return posthogInstancePromise
}

export function trackEvent(event: ScholrEventName, payload: ScholrEventPayload = {}) {
  if (!isAnalyticsEnabled()) {
    return
  }

  void getPostHog().then((posthog) => {
    if (!posthog) {
      return
    }

    posthog.capture(event, {
      ...payload,
      timestamp: payload.timestamp || new Date().toISOString(),
    })
  })
}
