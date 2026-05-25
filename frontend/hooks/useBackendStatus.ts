import { useEffect, useState } from 'react'

type Status = 'checking' | 'ready' | 'slow' | 'down'

export function useBackendStatus(apiUrl: string): Status {
  const [status, setStatus] = useState<Status>('checking')

  useEffect(() => {
    let cancelled = false
    const timer = window.setTimeout(() => {
      if (!cancelled) {
        setStatus((current) => (current === 'checking' ? 'slow' : current))
      }
    }, 3000)

    fetch(`${apiUrl}/health`, { signal: AbortSignal.timeout(5000) })
      .then((response) => {
        if (!cancelled) {
          setStatus(response.ok ? 'ready' : 'slow')
        }
      })
      .catch(() => {
        if (!cancelled) {
          setStatus('down')
        }
      })
      .finally(() => window.clearTimeout(timer))

    return () => {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [apiUrl])

  return status
}
