'use client'

import { useState } from 'react'

import AiModulePage from '@/components/ai/ai-module-page'

export default function DoubtPage() {
  const [subject, setSubject] = useState('')
  const [question, setQuestion] = useState('')
  const [output, setOutput] = useState('')

  return (
    <AiModulePage
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
    />
  )
}
