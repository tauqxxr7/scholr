'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'

import AiModulePage from '@/components/ai/ai-module-page'

const topicSuggestions = [
  'Binary Search Trees',
  'Machine Learning for beginners',
  'Operating System scheduling',
  'VLSI Design basics',
  'Neural Networks',
  'Computer Networks TCP/IP',
]

function ResearchPageContent() {
  const searchParams = useSearchParams()
  const linkedTopic = searchParams.get('topic')?.trim() || ''
  const hasLinkedTopic = linkedTopic.length > 3
  const [topic, setTopic] = useState(hasLinkedTopic ? linkedTopic : '')
  const [output, setOutput] = useState('')
  const [autoSubmitMessage, setAutoSubmitMessage] = useState(
    hasLinkedTopic ? 'Auto-loading topic from link...' : '',
  )

  useEffect(() => {
    if (!hasLinkedTopic) {
      return
    }

    const timer = window.setTimeout(() => setAutoSubmitMessage(''), 1400)
    return () => window.clearTimeout(timer)
  }, [hasLinkedTopic])

  return (
    <AiModulePage
      moduleName="research"
      title="Scholr Research"
      description="Turn any engineering topic into a research starting point with papers, reading order, and a realistic project gap."
      endpoint="/api/research"
      payloadKey="topic"
      primaryValue={topic}
      onPrimaryChange={setTopic}
      primaryPlaceholder="e.g. Object detection using YOLO for real-time traffic monitoring"
      output={output}
      setOutput={setOutput}
      loadingLabel="Searching papers..."
      idleLabel="Find Research Papers"
      autoSubmitSignal={hasLinkedTopic ? 1 : 0}
      autoSubmitMessage={autoSubmitMessage}
      promptExtras={
        <div className="space-y-2">
          <p className="text-sm text-slate-500">Try one of these:</p>
          <div className="flex flex-wrap gap-2">
            {topicSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setTopic(suggestion)}
                className="rounded-full border border-slate-200 px-3 py-1.5 text-sm text-slate-600 transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      }
    />
  )
}

export default function ResearchPage() {
  return (
    <Suspense fallback={null}>
      <ResearchPageContent />
    </Suspense>
  )
}
