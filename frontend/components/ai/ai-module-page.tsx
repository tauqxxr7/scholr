'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  Copy,
  RefreshCcw,
  Sparkles,
  WandSparkles,
  ArrowUpRight,
  ClipboardCheck,
  RotateCcw,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { StreamModuleError, streamModuleResponse } from '@/lib/api'

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
  const [hasGeneratedOnce, setHasGeneratedOnce] = useState(false)
  const [emptyStateMessage, setEmptyStateMessage] = useState('')
  const [lastAttemptFailed, setLastAttemptFailed] = useState(false)

  const runRequest = async () => {
    const payload: Record<string, string> = {
      [payloadKey]: primaryValue,
    }

    if (secondaryField) {
      payload.subject = secondaryField.value
    }

    setLoading(true)
    setOutput('')
    setError('')
    setEmptyStateMessage('')
    setLastAttemptFailed(false)

    try {
      const result = await streamModuleResponse(endpoint, payload, (chunk) => {
        setOutput((current) => current + chunk)
      })

      if (!result.hadChunks) {
        setEmptyStateMessage(
          result.emptyMessage || 'Scholr did not return any output for this prompt. Try refining it and run again.',
        )
      }

      setHasGeneratedOnce(true)
    } catch (submissionError) {
      const friendlyError =
        submissionError instanceof StreamModuleError
          ? submissionError.message
          : submissionError instanceof Error
            ? submissionError.message
            : 'Scholr could not complete this request right now. Please try again.'

      setError(friendlyError)
      setHasGeneratedOnce(true)
      setLastAttemptFailed(true)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!primaryValue.trim()) {
      return
    }
    await runRequest()
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
  const outputStatus = loading
    ? 'Streaming answer'
    : error
      ? 'Needs retry'
      : output
      ? 'Ready to review'
      : emptyStateMessage
        ? 'No output returned'
      : 'Waiting for input'

  return (
    <div className="space-y-6 lg:space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-[linear-gradient(135deg,rgba(255,251,235,0.95),rgba(255,255,255,0.98),rgba(240,249,255,0.98))] p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex w-fit items-center gap-2 rounded-full bg-white/85 px-3 py-1 text-sm font-medium text-amber-800 shadow-sm">
            <Sparkles className="h-4 w-4" />
            Scholr Core
            </div>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              {title}
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              {description}
            </p>
          </div>
          <div className="grid gap-3 rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-sm sm:grid-cols-2 lg:min-w-[20rem]">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Experience</p>
              <p className="mt-2 text-sm font-medium text-slate-900">
                Fast, readable, and pitch-ready
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Response mode</p>
              <p className="mt-2 text-sm font-medium text-slate-900">{outputStatus}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
        <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Prompt</p>
                <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                  Describe what you need
                </h2>
              </div>
              <div className="hidden rounded-2xl bg-slate-100 px-3 py-2 text-xs text-slate-500 sm:block">
                Streamed answer
              </div>
            </div>

            {secondaryField ? (
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Subject</label>
                <Input
                  placeholder={secondaryField.placeholder}
                  value={secondaryField.value}
                  onChange={(event) => secondaryField.onChange(event.target.value)}
                  className="h-12 rounded-2xl border-slate-200 bg-slate-50/70"
                />
              </div>
            ) : null}

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                {secondaryField ? 'Question' : 'Topic'}
              </label>
              <Textarea
                placeholder={primaryPlaceholder}
                value={primaryValue}
                onChange={(event) => onPrimaryChange(event.target.value)}
                rows={secondaryField ? 8 : 10}
                className="min-h-[220px] resize-none rounded-[1.5rem] border-slate-200 bg-slate-50/70 px-4 py-3 text-sm leading-7 shadow-none"
              />
            </div>

            <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50/80 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-2xl bg-white p-2 text-slate-700 shadow-sm">
                  <WandSparkles className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">Best results tip</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    Mention the exact concept, use case, or exam topic you care about. Specific
                    prompts usually produce stronger structured answers.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Button
                onClick={handleSubmit}
                disabled={loading || !primaryValue.trim()}
                className="min-h-12 rounded-2xl bg-slate-950 px-5 text-white hover:bg-slate-800 sm:min-w-44"
              >
                {loading ? loadingLabel : idleLabel}
                {!loading ? <ArrowUpRight className="ml-2 h-4 w-4" /> : null}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setOutput('')
                  setError('')
                  setEmptyStateMessage('')
                  setLastAttemptFailed(false)
                }}
                disabled={loading || !hasContent}
                className="min-h-12 rounded-2xl border-slate-200"
              >
                <RefreshCcw className="mr-2 h-4 w-4" />
                Clear
              </Button>
              <Button
                variant="outline"
                onClick={handleCopy}
                disabled={!output}
                className="min-h-12 rounded-2xl border-slate-200"
              >
                <Copy className="mr-2 h-4 w-4" />
                {copied ? 'Copied' : 'Copy'}
              </Button>
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="mb-5 flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Output</p>
              <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                Structured result
              </h2>
            </div>
            <div className="inline-flex w-fit items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs font-medium text-slate-600">
              <ClipboardCheck className="h-3.5 w-3.5" />
              {outputStatus}
            </div>
          </div>

          {!hasContent && !loading ? (
            <div className="flex min-h-[24rem] flex-col items-center justify-center rounded-[1.5rem] border border-dashed border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.9),rgba(255,255,255,0.95))] px-6 text-center">
              <div className="rounded-full bg-white p-4 shadow-sm">
                <Sparkles className="h-5 w-5 text-amber-700" />
              </div>
              <h3 className="mt-5 text-lg font-semibold text-slate-950">Nothing generated yet</h3>
              <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
                Start with a precise prompt and Scholr will stream a structured answer here with
                headings, examples, and revision-ready formatting.
              </p>
            </div>
          ) : null}

          {loading && !output ? (
            <div className="space-y-4">
              <div className="animate-pulse rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5">
                <div className="h-4 w-32 rounded-full bg-slate-200" />
                <div className="mt-5 space-y-3">
                  <div className="h-4 w-full rounded-full bg-slate-200" />
                  <div className="h-4 w-[92%] rounded-full bg-slate-200" />
                  <div className="h-4 w-[80%] rounded-full bg-slate-200" />
                </div>
              </div>
              <div className="animate-pulse rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5">
                <div className="h-4 w-28 rounded-full bg-slate-200" />
                <div className="mt-5 space-y-3">
                  <div className="h-4 w-full rounded-full bg-slate-200" />
                  <div className="h-4 w-[88%] rounded-full bg-slate-200" />
                  <div className="h-4 w-[74%] rounded-full bg-slate-200" />
                </div>
              </div>
              <p className="text-sm text-slate-500">Generating a polished answer for you...</p>
            </div>
          ) : null}

          {error ? (
            <div className="rounded-[1.5rem] border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">
              <p>{error}</p>
              {lastAttemptFailed ? (
                <Button
                  variant="outline"
                  onClick={runRequest}
                  disabled={loading || !primaryValue.trim()}
                  className="mt-4 min-h-11 rounded-2xl border-red-200 bg-white text-red-700 hover:bg-red-100 hover:text-red-800"
                >
                  <RotateCcw className="mr-2 h-4 w-4" />
                  Retry request
                </Button>
              ) : null}
            </div>
          ) : null}

          {output ? (
            <div className="scholr-markdown">
              <ReactMarkdown>{output}</ReactMarkdown>
              {loading ? <span className="scholr-streaming-cursor" aria-hidden="true" /> : null}
            </div>
          ) : null}

          {!output && !error && emptyStateMessage ? (
            <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
              {emptyStateMessage}
            </div>
          ) : null}

          {!output && !error && !emptyStateMessage && hasGeneratedOnce && !loading ? (
            <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
              Your next answer will appear here. Try refining the prompt for a more targeted
              result.
            </div>
          ) : null}
        </div>
      </section>
    </div>
  )
}
