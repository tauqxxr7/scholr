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
  provider_ready_for_embeddings: boolean
  provider_error_category?: string | null
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
      message: 'AI provider configuration error. Please try again later.',
      retryable: false,
      category: 'provider_configuration',
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

function describeNetworkFailure(error: unknown) {
  if (error instanceof StreamModuleError) {
    return error
  }

  if (error instanceof DOMException && error.name === 'AbortError') {
    return new StreamModuleError('Backend is waking up. Please retry in 20-30 seconds.', true, 'cold_start')
  }

  if (error instanceof TypeError) {
    return new StreamModuleError(
      'Scholr could not reach the backend. This can happen if the backend is waking up, the network is unstable, or the browser blocked the request.',
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
): Promise<StreamModuleResult> {
  let response: Response
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 65000)

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
  let buffer = ''
  let hadChunks = false
  let malformedEvents = 0
  let emptyMessage = ''
  let mode: StreamModuleResult['mode']
  let modeLabel = ''

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
        onChunk(parsed.chunk)
        return
      }

      if (parsed.type === 'error') {
        throw new StreamModuleError(
          parsed.message || 'Scholr could not complete this request.',
          parsed.retryable ?? true,
          parsed.category || 'backend_error',
        )
      }

      if (parsed.type === 'empty') {
        emptyMessage =
          parsed.message ||
          'Scholr did not return any output for this prompt. Try rephrasing it and run again.'
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
        return { hadChunks, emptyMessage: emptyMessage || undefined, mode, modeLabel: modeLabel || undefined }
      }
    }
  }

  if (buffer.trim()) {
    const result = processEventBlock(buffer)
    if (result === 'done') {
      return { hadChunks, emptyMessage: emptyMessage || undefined, mode, modeLabel: modeLabel || undefined }
    }
  }

  return { hadChunks, emptyMessage: emptyMessage || undefined, mode, modeLabel: modeLabel || undefined }
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

export async function getDocumentHealth(): Promise<DocumentHealthResult> {
  const response = await fetch(`${getApiUrl()}/health/documents`, {
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch document health')
  }

  return response.json()
}
