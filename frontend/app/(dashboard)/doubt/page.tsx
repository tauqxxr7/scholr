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
  const [autoSubmitMessage, setAutoSubmitMessage] = useState(
    hasLinkedQuestion ? 'Auto-loading topic from link...' : '',
  )

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
      autoSubmitSignal={hasLinkedQuestion ? 1 : 0}
      autoSubmitMessage={autoSubmitMessage}
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
