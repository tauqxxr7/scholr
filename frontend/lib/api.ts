const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, '') || ''
const API_URL =
  configuredApiUrl || (process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8000' : '')

export type HistoryItem = {
  id: string
  module: string
  query: string
  response: string
  created_at: string
}

export type SearchResultItem = {
  id: string
  module: string
  query: string
  score: number
  created_at: string
}

export type MetricsResult = {
  searches: {
    total: number
    last_24h: number
    last_7d: number
    by_module: Record<string, number>
  }
  feedback: {
    total: number
    helpful: number
    not_helpful: number
    helpful_rate: number | null
  }
}

export type DocumentUploadResult = {
  document_id: string
  title: string
  status: string
  page_count: number
  chunk_count: number
  retrieval_ready: boolean
  warning?: string | null
}

export type DocumentCitation = {
  document_name: string
  page_number: number
  chunk_index: number
  citation_label: string
  snippet: string
}

export type DocumentAnswerResult = {
  document_id: string
  answer: string
  citations: DocumentCitation[]
  retrieval_ready: boolean
  generation_used: boolean
  answer_mode: string
  retrieval_mode: string
  confidence: string
  limitations: string[]
  warning?: string | null
}

export type DocumentHealthResult = {
  status: string
  pdf_parsing_available: boolean
  multipart_available: boolean
  vector_store_available: boolean
  embedding_provider_configured: boolean
  embedding_provider_ready?: boolean
  provider_ready_for_embeddings: boolean
  embedding_provider?: string | null
  embedding_model?: string | null
  semantic_retrieval_ready?: boolean
  lexical_fallback_ready?: boolean
  provider_error_category?: string | null
  embedding_error_category?: string | null
  embedding_health: string
  retrieval_health?: string
  retrieval_default_mode: 'lexical' | 'semantic' | 'hybrid' | string
  documents_storage_path: string
  vector_storage_path: string
}

type StreamEvent =
  | { type: 'chunk'; chunk: string }
  | { type: 'error'; message: string; retryable?: boolean; category?: string }
  | { type: 'empty'; message?: string }
  | { type: 'partial'; message?: string; category?: string }
  | { type: 'meta'; mode?: 'ai' | 'cache' | 'warm_cache' | 'fallback' | 'recovering'; label?: string }

export class StreamModuleError extends Error {
  retryable: boolean
  category: string

  constructor(message: string, retryable = true, category = 'unknown') {
    super(message)
    this.name = 'StreamModuleError'
    this.retryable = retryable
    this.category = category
  }
}

export type StreamModuleResult = {
  hadChunks: boolean
  emptyMessage?: string
  mode?: 'ai' | 'cache' | 'warm_cache' | 'fallback' | 'recovering'
  modeLabel?: string
  partialMessage?: string
  partialCategory?: string
}

function describeHttpFailure(status: number) {
  if (status === 502 || status === 503 || status === 504) {
    return {
      message: 'Backend is waking up. Please retry in 20-30 seconds.',
      retryable: true,
      category: 'cold_start',
    }
  }

  if (status >= 500) {
    return {
      message: 'Scholr backend is running into a server issue right now. Please retry in a moment.',
      retryable: true,
      category: 'backend_error',
    }
  }

  if (status === 429) {
    return {
      message: 'Too many requests. Please wait a minute.',
      retryable: true,
      category: 'rate_limited',
    }
  }

  if (status === 404) {
    return {
      message: 'This Scholr route is unavailable right now. Restart the backend and try again.',
      retryable: false,
      category: 'route_missing',
    }
  }

  if (status === 401 || status === 403) {
    return {
      message: 'Your session is missing or expired. Please sign in again to continue using your Scholr workspace.',
      retryable: false,
      category: 'authentication_required',
    }
  }

  return {
    message: `The request could not be completed right now (status ${status}).`,
    retryable: status >= 500,
    category: 'http_error',
  }
}

function getApiUrl() {
  if (API_URL) {
    return API_URL
  }

  throw new StreamModuleError(
    'The frontend is missing NEXT_PUBLIC_API_URL for this environment. Add the deployed backend URL and redeploy.',
    false,
    'configuration',
  )
}

export function getApiBaseUrl() {
  return getApiUrl()
}

function describeNetworkFailure(error: unknown) {
  if (error instanceof StreamModuleError) {
    return error
  }

  if (error instanceof DOMException && error.name === 'AbortError') {
    return new StreamModuleError(
      "Cannot reach Scholr's AI server. It may be starting up — please wait 30 seconds and try again.",
      true,
      'cold_start',
    )
  }

  if (error instanceof TypeError) {
    return new StreamModuleError(
      "Cannot reach Scholr's AI server. It may be starting up — please wait 30 seconds and try again.",
      true,
      'network_or_cors',
    )
  }

  return new StreamModuleError(
    'Scholr could not complete this request right now. Please try again.',
    true,
    'unexpected',
  )
}

export async function streamModuleResponse(
  path: string,
  payload: Record<string, string>,
  onChunk: (chunk: string) => void,
  onMeta?: (meta: { mode?: StreamModuleResult['mode']; label?: string }) => void,
  onProgress?: (progress: { stage: 'connecting' | 'thinking' | 'writing' | 'finalizing'; elapsedMs: number }) => void,
): Promise<StreamModuleResult> {
  let response: Response
  const controller = new AbortController()
  const startedAt = performance.now()
  const timeout = window.setTimeout(() => controller.abort(), 22000)
  onProgress?.({ stage: 'connecting', elapsedMs: 0 })

  try {
    response = await fetch(`${getApiUrl()}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
  } catch (error) {
    throw describeNetworkFailure(error)
  } finally {
    window.clearTimeout(timeout)
  }
  onProgress?.({ stage: 'thinking', elapsedMs: Math.round(performance.now() - startedAt) })

  if (!response.ok) {
    const failure = describeHttpFailure(response.status)
    throw new StreamModuleError(failure.message, failure.retryable, failure.category)
  }

  if (!response.body) {
    throw new StreamModuleError(
      'The backend returned an empty response stream. Restart the backend and try again.',
      true,
    )
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  const firstTokenTimeout = window.setTimeout(() => controller.abort(), 5000)
  const streamHardTimeout = window.setTimeout(() => controller.abort(), 22000)
  let buffer = ''
  let hadChunks = false
  let malformedEvents = 0
  let emptyMessage = ''
  let mode: StreamModuleResult['mode']
  let modeLabel = ''
  let partialMessage = ''
  let partialCategory = ''

  const processEventBlock = (eventBlock: string) => {
    const normalizedBlock = eventBlock.replace(/\r/g, '')
    const dataLines = normalizedBlock
      .split('\n')
      .map((entry) => entry.trim())
      .filter((entry) => entry.startsWith('data: '))

    if (!dataLines.length) {
      return
    }

    const data = dataLines.map((line) => line.slice(6)).join('\n')
    if (data === '[DONE]') {
      return 'done'
    }

    try {
      const parsed = JSON.parse(data) as StreamEvent

      if (parsed.type === 'chunk' && typeof parsed.chunk === 'string') {
        hadChunks = true
        window.clearTimeout(firstTokenTimeout)
        onProgress?.({ stage: 'writing', elapsedMs: Math.round(performance.now() - startedAt) })
        onChunk(parsed.chunk)
        return
      }

      if (parsed.type === 'error') {
        if (hadChunks) {
          partialMessage =
            parsed.message ||
            'The response was cut short. Here is what was generated so far. Tap retry for a complete answer.'
          partialCategory = parsed.category || 'stream_error_after_tokens'
          return
        }
        throw new StreamModuleError(
          parsed.message || 'Scholr could not complete this request.',
          parsed.retryable ?? true,
          parsed.category || 'backend_error',
        )
      }

      if (parsed.type === 'empty') {
        emptyMessage =
          parsed.message ||
          "The AI didn't generate a response. This sometimes happens with very short topics — try being more specific."
        return
      }

      if (parsed.type === 'partial') {
        partialMessage =
          parsed.message ||
          'The response was cut short. Here is what was generated so far. Tap retry for a complete answer.'
        partialCategory = parsed.category || 'partial_stream'
        onProgress?.({ stage: 'finalizing', elapsedMs: Math.round(performance.now() - startedAt) })
        return
      }

      if (parsed.type === 'meta') {
        mode = parsed.mode
        modeLabel = parsed.label || ''
        onMeta?.({ mode, label: modeLabel || undefined })
      }
      return
    } catch (error) {
      if (error instanceof StreamModuleError) {
        throw error
      }

      malformedEvents += 1
      if (malformedEvents >= 3 && !hadChunks) {
        throw new StreamModuleError(
          'Scholr received unreadable streamed data from the backend. Please retry once the backend is stable.',
          true,
          'malformed_sse',
        )
      }
    }
  }

  try {
    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      buffer += decoder.decode(value, { stream: true })
      buffer = buffer.replace(/\r\n/g, '\n')
      const events = buffer.split('\n\n')
      buffer = events.pop() ?? ''

      for (const event of events) {
        const result = processEventBlock(event)
        if (result === 'done') {
          return {
            hadChunks,
            emptyMessage: emptyMessage || undefined,
            mode,
            modeLabel: modeLabel || undefined,
            partialMessage: partialMessage || undefined,
            partialCategory: partialCategory || undefined,
          }
        }
      }
    }
  } catch (error) {
    if (hadChunks) {
      return {
        hadChunks,
        emptyMessage: emptyMessage || undefined,
        mode,
        modeLabel: modeLabel || undefined,
        partialMessage:
          'The response was cut short. Here is what was generated so far. Tap retry for a complete answer.',
        partialCategory: error instanceof DOMException && error.name === 'AbortError' ? 'frontend_timeout' : 'stream_interrupted',
      }
    }
    throw describeNetworkFailure(error)
  } finally {
    window.clearTimeout(firstTokenTimeout)
    window.clearTimeout(streamHardTimeout)
  }

  if (buffer.trim()) {
    const result = processEventBlock(buffer)
    if (result === 'done') {
      return {
        hadChunks,
        emptyMessage: emptyMessage || undefined,
        mode,
        modeLabel: modeLabel || undefined,
        partialMessage: partialMessage || undefined,
        partialCategory: partialCategory || undefined,
      }
    }
  }

  return {
    hadChunks,
    emptyMessage: emptyMessage || undefined,
    mode,
    modeLabel: modeLabel || undefined,
    partialMessage: partialMessage || undefined,
    partialCategory: partialCategory || undefined,
  }
}

export async function getHistory(limit = 6, page = 1): Promise<HistoryItem[]> {
  const response = await fetch(`${getApiUrl()}/api/history?limit=${limit}&page=${page}`, {
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch history')
  }

  return response.json()
}

export function getHistoryExportUrl(): string {
  return `${getApiUrl()}/api/history/export`
}

export async function getMetrics(): Promise<MetricsResult> {
  const response = await fetch(`${getApiUrl()}/api/metrics`, { cache: 'no-store' })
  if (!response.ok) {
    throw new Error('Failed to fetch metrics')
  }
  return response.json()
}

export async function searchHistory(query: string, limit = 5): Promise<SearchResultItem[]> {
  const response = await fetch(
    `${getApiUrl()}/api/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    { cache: 'no-store' },
  )
  if (!response.ok) {
    throw new Error('Search failed')
  }
  const data = (await response.json()) as { results: SearchResultItem[] }
  return data.results
}

export async function uploadDocument(
  file: File,
  onProgress?: (progress: number) => void,
): Promise<DocumentUploadResult> {
  const url = `${getApiUrl()}/api/documents/upload`

  return new Promise<DocumentUploadResult>((resolve, reject) => {
    const formData = new FormData()
    formData.append('file', file)

    const request = new XMLHttpRequest()
    request.open('POST', url)

    request.upload.onprogress = (event) => {
      if (!event.lengthComputable) {
        return
      }
      onProgress?.(Math.min(100, Math.round((event.loaded / event.total) * 100)))
    }

    request.onerror = () => {
      reject(
        new StreamModuleError(
          'Scholr could not upload this PDF right now. Please check your connection and try again.',
          true,
          'upload_network_error',
        ),
      )
    }

    request.onload = () => {
      let parsed: unknown
      try {
        parsed = request.responseText ? JSON.parse(request.responseText) : {}
      } catch {
        reject(
          new StreamModuleError(
            'The backend returned an unreadable upload response. Please retry.',
            true,
            'upload_malformed_response',
          ),
        )
        return
      }

      if (request.status < 200 || request.status >= 300) {
        const detail =
          typeof parsed === 'object' && parsed && 'detail' in parsed && typeof parsed.detail === 'string'
            ? parsed.detail
            : 'Scholr could not process this PDF right now.'

        reject(new StreamModuleError(detail, request.status >= 500, 'document_upload_failed'))
        return
      }

      resolve(parsed as DocumentUploadResult)
    }

    request.send(formData)
  })
}

export async function answerDocumentQuestion(payload: {
  document_id: string
  question: string
  top_k?: number
}): Promise<DocumentAnswerResult> {
  const response = await fetch(`${getApiUrl()}/api/documents/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const json = (await response.json()) as DocumentAnswerResult | { detail?: string }
  if (!response.ok) {
    const detail = 'detail' in json && typeof json.detail === 'string' ? json.detail : 'Document answer failed.'
    throw new StreamModuleError(detail, response.status >= 500, 'document_answer_failed')
  }

  return json as DocumentAnswerResult
}

export async function submitFeedback(payload: {
  module: string
  query: string
  rating: 'helpful' | 'not_helpful'
  response_length: number
  mode?: 'fast' | 'deep'
  latency_ms?: number
}): Promise<{ received: boolean }> {
  const response = await fetch(`${getApiUrl()}/api/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new StreamModuleError('Feedback could not be saved right now.', true, 'feedback_failed')
  }

  return response.json()
}

export async function getDocumentHealth(): Promise<DocumentHealthResult> {
  const response = await fetch(`${getApiUrl()}/health/documents`, {
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch document health')
  }

  return response.json()
}
