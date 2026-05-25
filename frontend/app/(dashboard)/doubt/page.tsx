'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'

import AiModulePage from '@/components/ai/ai-module-page'

function DoubtPageContent() {
  const searchParams = useSearchParams()
  const linkedQuestion = searchParams.get('question')?.trim() || ''
  const hasLinkedQuestion = linkedQuestion.length > 3
  const [subject, setSubject] = useState('')
  const [question, setQuestion] = useState(hasLinkedQuestion ? linkedQuestion : '')
  const [output, setOutput] = useState('')
  const [exampleSubmitSignal, setExampleSubmitSignal] = useState(0)
  const [autoSubmitMessage, setAutoSubmitMessage] = useState(
    hasLinkedQuestion ? 'Auto-loading topic from link...' : '',
  )

  const runExample = () => {
    setQuestion('What is the difference between stack and queue data structure?')
    setExampleSubmitSignal(Date.now())
  }

  useEffect(() => {
    if (!hasLinkedQuestion) {
      return
    }

    const timer = window.setTimeout(() => setAutoSubmitMessage(''), 1400)
    return () => window.clearTimeout(timer)
  }, [hasLinkedQuestion])

  return (
    <AiModulePage
      moduleName="doubt"
      title="Scholr Doubt"
      description="Get a calm, step-by-step explanation for difficult topics without losing the depth needed for engineering subjects."
      endpoint="/api/doubt"
      payloadKey="question"
      primaryValue={question}
      onPrimaryChange={setQuestion}
      primaryPlaceholder="Ask your doubt here..."
      secondaryField={{
        value: subject,
        onChange: setSubject,
        placeholder: 'Subject (optional) e.g. DBMS',
      }}
      output={output}
      setOutput={setOutput}
      loadingLabel="Solving doubt..."
      idleLabel="Solve My Doubt"
      autoSubmitSignal={exampleSubmitSignal || (hasLinkedQuestion ? 1 : 0)}
      autoSubmitMessage={autoSubmitMessage}
      autoSubmitDelayMs={exampleSubmitSignal ? 0 : 500}
      promptExtras={
        !question && !output ? (
          <button
            type="button"
            onClick={runExample}
            className="min-h-11 w-full rounded-2xl bg-indigo-600 px-4 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            ▶ Try a live example
          </button>
        ) : null
      }
    />
  )
}

export default function DoubtPage() {
  return (
    <Suspense fallback={null}>
      <DoubtPageContent />
    </Suspense>
  )
}
