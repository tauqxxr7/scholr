'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'

import AiModulePage from '@/components/ai/ai-module-page'

const subjectChips = [
  'Mathematics',
  'Data Structures',
  'Operating Systems',
  'Computer Networks',
  'DBMS',
  'Machine Learning',
  'Digital Electronics',
  'Signals & Systems',
]

function NotesPageContent() {
  const searchParams = useSearchParams()
  const linkedTopic = searchParams.get('topic')?.trim() || ''
  const hasLinkedTopic = linkedTopic.length > 3
  const [topic, setTopic] = useState(hasLinkedTopic ? linkedTopic : '')
  const [output, setOutput] = useState('')
  const [exampleSubmitSignal, setExampleSubmitSignal] = useState(0)
  const [autoSubmitMessage, setAutoSubmitMessage] = useState(
    hasLinkedTopic ? 'Auto-loading topic from link...' : '',
  )

  const selectSubject = (subject: string) => {
    setTopic(`${subject}: `)
  }

  const runExample = () => {
    setTopic('Operating System process scheduling algorithms')
    setExampleSubmitSignal(Date.now())
  }

  useEffect(() => {
    if (!hasLinkedTopic) {
      return
    }

    const timer = window.setTimeout(() => setAutoSubmitMessage(''), 1400)
    return () => window.clearTimeout(timer)
  }, [hasLinkedTopic])

  return (
    <AiModulePage
      moduleName="notes"
      title="Scholr Notes"
      description="Generate structured revision notes built for university prep, quick revision, and last-minute exam confidence."
      endpoint="/api/notes"
      payloadKey="topic"
      primaryValue={topic}
      onPrimaryChange={setTopic}
      primaryPlaceholder="e.g. Operating System deadlock"
      output={output}
      setOutput={setOutput}
      loadingLabel="Writing notes..."
      idleLabel="Generate Notes"
      autoSubmitSignal={exampleSubmitSignal || (hasLinkedTopic ? 1 : 0)}
      autoSubmitMessage={autoSubmitMessage}
      autoSubmitDelayMs={exampleSubmitSignal ? 0 : 500}
      promptExtras={
        <div className="space-y-2">
          {!topic && !output ? (
            <button
              type="button"
              onClick={runExample}
              className="min-h-11 w-full rounded-2xl bg-indigo-600 px-4 text-sm font-semibold text-white transition hover:bg-indigo-700"
            >
              ▶ Try a live example
            </button>
          ) : null}
          <p className="text-sm text-slate-500">Choose a subject:</p>
          <div className="flex flex-wrap gap-2">
            {subjectChips.map((subject) => (
              <button
                key={subject}
                type="button"
                onClick={() => selectSubject(subject)}
                className="rounded-full border border-slate-200 px-3 py-1.5 text-sm text-slate-600 transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
              >
                {subject}
              </button>
            ))}
          </div>
        </div>
      }
    />
  )
}

export default function NotesPage() {
  return (
    <Suspense fallback={null}>
      <NotesPageContent />
    </Suspense>
  )
}
