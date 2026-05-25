'use client'

import { useState } from 'react'

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

export default function NotesPage() {
  const [topic, setTopic] = useState('')
  const [output, setOutput] = useState('')

  const selectSubject = (subject: string) => {
    setTopic(`${subject}: `)
  }

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
      promptExtras={
        <div className="space-y-2">
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
