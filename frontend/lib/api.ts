const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export type HistoryItem = {
  id: string
  module: string
  query: string
  response: string
  created_at: string
}

type StreamEvent =
  | { type: 'chunk'; chunk: string }
  | { type: 'error'; message: string; retryable?: boolean }
  | { type: 'empty'; message?: string }

export class StreamModuleError extends Error {
  retryable: boolean

  constructor(message: string, retryable = true) {
    super(message)
    this.name = 'StreamModuleError'
    this.retryable = retryable
  }
}

export type StreamModuleResult = {
  hadChunks: boolean
  emptyMessage?: string
}

function describeHttpFailure(status: number) {
  if (status >= 500) {
    return 'Scholr backend is running into a server issue right now. Please retry in a moment.'
  }

  if (status === 404) {
    return 'This Scholr route is unavailable right now. Restart the backend and try again.'
  }

  if (status === 401 || status === 403) {
    return 'The backend rejected this request. Check the Gemini configuration and try again.'
  }

  return `The request could not be completed right now (status ${status}).`
}

function describeNetworkFailure(error: unknown) {
  if (error instanceof StreamModuleError) {
    return error
  }

  if (error instanceof TypeError) {
    return new StreamModuleError(
      'Scholr could not reach the backend. Make sure the FastAPI server is running on the expected port.',
      true,
    )
  }

  return new StreamModuleError('Scholr could not complete this request right now. Please try again.', true)
}

export async function streamModuleResponse(
  path: string,
  payload: Record<string, string>,
  onChunk: (chunk: string) => void,
): Promise<StreamModuleResult> {
  let response: Response

  try {
    response = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (error) {
    throw describeNetworkFailure(error)
  }

  if (!response.ok) {
    throw new StreamModuleError(describeHttpFailure(response.status), response.status >= 500)
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

  while (true) {
    const { done, value } = await reader.read()

    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''

    for (const event of events) {
      const line = event
        .split('\n')
        .map((entry) => entry.trim())
        .find((entry) => entry.startsWith('data: '))

      if (!line) {
        continue
      }

      const data = line.slice(6)
      if (data === '[DONE]') {
        return { hadChunks, emptyMessage: emptyMessage || undefined }
      }

      try {
        const parsed = JSON.parse(data) as StreamEvent

        if (parsed.type === 'chunk' && typeof parsed.chunk === 'string') {
          hadChunks = true
          onChunk(parsed.chunk)
          continue
        }

        if (parsed.type === 'error') {
          throw new StreamModuleError(
            parsed.message || 'Scholr could not complete this request.',
            parsed.retryable ?? true,
          )
        }

        if (parsed.type === 'empty') {
          emptyMessage =
            parsed.message ||
            'Scholr did not return any output for this prompt. Try rephrasing it and run again.'
        }
        continue
      } catch (error) {
        if (error instanceof StreamModuleError) {
          throw error
        }

        malformedEvents += 1
        if (malformedEvents >= 3 && !hadChunks) {
          throw new StreamModuleError(
            'Scholr received unreadable streamed data from the backend. Please retry once the backend is stable.',
            true,
          )
        }
      }
    }
  }

  return { hadChunks, emptyMessage: emptyMessage || undefined }
}

export async function getHistory(limit = 6): Promise<HistoryItem[]> {
  const response = await fetch(`${API_URL}/api/history?limit=${limit}`, {
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch history')
  }

  return response.json()
}
