import { useEffect, useCallback } from 'react'

interface ShortcutHandlers {
  onSubmit: () => void
  onClear: () => void
  onCopy: () => void
  isLoading: boolean
}

export function useKeyboardShortcuts({
  onSubmit,
  onClear,
  onCopy,
  isLoading,
}: ShortcutHandlers) {
  const handler = useCallback(
    (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey
      if (meta && e.key === 'Enter' && !isLoading) {
        e.preventDefault()
        onSubmit()
      }
      if (e.key === 'Escape') {
        e.preventDefault()
        onClear()
      }
      if (meta && e.key === 'k') {
        e.preventDefault()
        onCopy()
      }
    },
    [onSubmit, onClear, onCopy, isLoading]
  )

  useEffect(() => {
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [handler])
}
