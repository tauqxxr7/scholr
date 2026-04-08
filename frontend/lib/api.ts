const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export type HistoryItem = {
  id: string
  module: string
  query: string
  response: string
  created_at: string
}

export async function streamModuleResponse(
  path: string,
  payload: Record<string, string>,
  onChunk: (chunk: string) => void,
) {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok || !response.body) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''

    for (const event of events) {
      const line = event.split('\n').find((entry) => entry.startsWith('data: '))

      if (!line) {
        continue
      }

      const data = line.slice(6)
      if (data === '[DONE]') {
        return
      }

      const parsed = JSON.parse(data) as { chunk: string }
      onChunk(parsed.chunk)
    }
  }
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
