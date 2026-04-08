'use client'

import { useState } from 'react'

import AiModulePage from '@/components/ai/ai-module-page'

export default function NotesPage() {
  const [topic, setTopic] = useState('')
  const [output, setOutput] = useState('')

  return (
    <AiModulePage
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
    />
  )
}
