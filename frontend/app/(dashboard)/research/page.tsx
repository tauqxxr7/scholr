'use client'

import { useState } from 'react'

import AiModulePage from '@/components/ai/ai-module-page'

export default function ResearchPage() {
  const [topic, setTopic] = useState('')
  const [output, setOutput] = useState('')

  return (
    <AiModulePage
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
    />
  )
}
