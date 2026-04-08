'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Copy, RefreshCcw, Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { streamModuleResponse } from '@/lib/api'

type SecondaryField = {
  value: string
  onChange: (value: string) => void
  placeholder: string
}

type AiModulePageProps = {
  title: string
  description: string
  endpoint: string
  payloadKey: string
  primaryValue: string
  onPrimaryChange: (value: string) => void
  primaryPlaceholder: string
  secondaryField?: SecondaryField
  output: string
  setOutput: (value: string | ((current: string) => string)) => void
  loadingLabel: string
  idleLabel: string
}

export default function AiModulePage({
  title,
  description,
  endpoint,
  payloadKey,
  primaryValue,
  onPrimaryChange,
  primaryPlaceholder,
  secondaryField,
  output,
  setOutput,
  loadingLabel,
  idleLabel,
}: AiModulePageProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  const handleSubmit = async () => {
    if (!primaryValue.trim()) {
      return
    }

    setLoading(true)
    setOutput('')
    setError('')

    try {
      const payload: Record<string, string> = {
        [payloadKey]: primaryValue,
      }

      if (secondaryField) {
        payload.subject = secondaryField.value
      }

      await streamModuleResponse(endpoint, payload, (chunk) => {
        setOutput((current) => current + chunk)
      })
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : 'Something went wrong. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (!output) {
      return
    }

    await navigator.clipboard.writeText(output)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1500)
  }

  const hasContent = output || error

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-sm">
        <div className="flex flex-col gap-3">
          <div className="inline-flex w-fit items-center gap-2 rounded-full bg-amber-50 px-3 py-1 text-sm font-medium text-amber-800">
            <Sparkles className="h-4 w-4" />
            Scholr Core
          </div>
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-950">{title}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">{description}</p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="space-y-4">
            {secondaryField ? (
              <Input
                placeholder={secondaryField.placeholder}
                value={secondaryField.value}
                onChange={(event) => secondaryField.onChange(event.target.value)}
              />
            ) : null}

            <Textarea
              placeholder={primaryPlaceholder}
              value={primaryValue}
              onChange={(event) => onPrimaryChange(event.target.value)}
              rows={secondaryField ? 8 : 10}
              className="resize-none"
            />

            <div className="flex flex-wrap gap-3">
              <Button
                onClick={handleSubmit}
                disabled={loading || !primaryValue.trim()}
                className="min-w-44 bg-slate-950 text-white hover:bg-slate-800"
              >
                {loading ? loadingLabel : idleLabel}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setOutput('')
                  setError('')
                }}
                disabled={loading || !hasContent}
              >
                <RefreshCcw className="mr-2 h-4 w-4" />
                Clear
              </Button>
              <Button variant="outline" onClick={handleCopy} disabled={!output}>
                <Copy className="mr-2 h-4 w-4" />
                {copied ? 'Copied' : 'Copy'}
              </Button>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          {!hasContent && !loading ? (
            <div className="flex h-full min-h-80 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 text-center text-sm leading-6 text-slate-500">
              Ask Scholr something meaningful and your answer will stream here in real time.
            </div>
          ) : null}

          {loading && !output ? (
            <div className="flex min-h-80 items-center justify-center">
              <div className="space-y-4 text-center">
                <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />
                <p className="text-sm text-slate-500">Generating a polished answer for you...</p>
              </div>
            </div>
          ) : null}

          {error ? (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          {output ? (
            <div className="scholr-markdown">
              <ReactMarkdown>{output}</ReactMarkdown>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  )
}
