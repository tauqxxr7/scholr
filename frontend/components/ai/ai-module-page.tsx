'use client'

import { useEffect, useState } from 'react'
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
import ResponseFeedback from '@/components/ai/ResponseFeedback'
import { trackEvent } from '@/lib/analytics'
import { StreamModuleError, streamModuleResponse } from '@/lib/api'

const LOCAL_RESPONSE_CACHE_KEY = 'scholr-local-response-cache-v1'

type SecondaryField = {
  value: string
  onChange: (value: string) => void
  placeholder: string
}

type AiModulePageProps = {
  moduleName: 'research' | 'notes' | 'doubt'
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

function AiModulePageContent({
  moduleName,
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
  const [responseMode, setResponseMode] = useState<'ai' | 'cache' | 'warm_cache' | 'fallback' | 'recovering'>('ai')
  const [responseModeLabel, setResponseModeLabel] = useState('AI Mode')
  const [answerDepth, setAnswerDepth] = useState<'fast' | 'deep'>('fast')
  const [progressStage, setProgressStage] = useState<'connecting' | 'thinking' | 'writing' | 'finalizing'>('connecting')
  const [slowStreamHint, setSlowStreamHint] = useState(false)

  const getCacheKey = () =>
    [
      moduleName,
      secondaryField?.value.trim().toLowerCase() || '',
      primaryValue.trim().toLowerCase(),
    ].join('::')

  const buildOptimisticTemplate = () => {
    const topic = primaryValue.trim() || 'this topic'
    const subject = secondaryField?.value.trim() || 'General'
    const normalizedTopic = topic.toLowerCase()
    const looksLikeDefinition = normalizedTopic.startsWith('what is') || normalizedTopic.startsWith('define')
    const looksLikeSummary = normalizedTopic.includes('summary') || normalizedTopic.includes('summar')
    const looksLikeExam = normalizedTopic.includes('exam') || normalizedTopic.includes('long answer')

    if (moduleName === 'research') {
      return `## Generating short answer...\n\n### Connecting\n- Preparing fast research direction for **${topic}**.\n- Scholr will keep this compact first; use Deep only if you need more detail.`
    }

    if (moduleName === 'notes') {
      const notesFocus = looksLikeExam
        ? '### Exam Answer Frame\n- definition or introduction\n- core explanation in 3 to 5 points\n- diagram, formula, or example\n- short conclusion for scoring answers'
        : looksLikeSummary
          ? '### Summary Frame\n- one-line meaning\n- top 3 to 5 ideas\n- one quick example\n- one mnemonic or memory hook'
          : '### Revision Frame\n- definition\n- key concepts\n- formulas or conditions\n- common viva questions'

      return `## Generating short answer...\n\n${notesFocus}\n\n### Connecting\n- Preparing compact revision notes for **${topic}**.`
    }

    const doubtFocus = looksLikeDefinition
      ? '### Definition Scaffold\n- textbook definition\n- plain-English meaning\n- one example\n- one related concept'
      : looksLikeSummary
        ? '### Summary Scaffold\n- one-paragraph explanation\n- key bullets\n- one important formula or condition\n- common mistake'
        : looksLikeExam
          ? '### Exam Answer Scaffold\n- intro definition\n- stepwise explanation\n- one worked example\n- conclusion point'
          : '### Explanation Flow\n- textbook definition\n- step-by-step reasoning\n- one simple example\n- one common mistake to avoid'

    return `## Generating short answer...\n\n${doubtFocus}\n\n### Connecting\n- Preparing a direct answer for **${topic}** in **${subject}**.`
  }

  const readLocalCache = () => {
    if (typeof window === 'undefined') {
      return null
    }

    try {
      const raw = window.localStorage.getItem(LOCAL_RESPONSE_CACHE_KEY)
      if (!raw) {
        return null
      }

      const parsed = JSON.parse(raw) as Record<string, { response: string; savedAt: string }>
      return parsed[getCacheKey()] || null
    } catch {
      return null
    }
  }

  const writeLocalCache = (response: string) => {
    if (typeof window === 'undefined' || !response.trim()) {
      return
    }

    try {
      const raw = window.localStorage.getItem(LOCAL_RESPONSE_CACHE_KEY)
      const parsed = raw
        ? (JSON.parse(raw) as Record<string, { response: string; savedAt: string }>)
        : {}
      parsed[getCacheKey()] = {
        response,
        savedAt: new Date().toISOString(),
      }
      window.localStorage.setItem(LOCAL_RESPONSE_CACHE_KEY, JSON.stringify(parsed))
    } catch {
      return
    }
  }

  useEffect(() => {
    trackEvent('module_opened', {
      module: moduleName,
      entrypoint: 'module_page',
    })
  }, [moduleName])

  const runRequest = async () => {
    const startedAt = performance.now()
    let responseLength = 0
    let firstTokenTracked = false
    let firstTokenLatencyMs = 0
    let finalResponse = ''
    let streamHydrated = false
    let frontendStreamParseLatencyMs = 0
    const requestSequence = hasGeneratedOnce ? 'second_or_later' : 'first'
    const payload: Record<string, string> = {
      [payloadKey]: primaryValue,
      mode: answerDepth,
      response_mode: answerDepth,
    }

    if (secondaryField) {
      payload.subject = secondaryField.value
    }

    setLoading(true)
    setOutput('')
    setError('')
    setEmptyStateMessage('')
    setLastAttemptFailed(false)
    setProgressStage('connecting')
    setSlowStreamHint(false)
    const slowHintTimer = window.setTimeout(() => {
      setSlowStreamHint(true)
      setProgressStage((current) => (current === 'connecting' || current === 'thinking' ? 'writing' : current))
    }, 8000)
    const cachedHydration = readLocalCache()
    if (cachedHydration) {
      setOutput(cachedHydration.response)
      setResponseMode('cache')
      setResponseModeLabel('Cached Response')
      trackEvent('cache_hydrated', {
        module: moduleName,
        cache_source: 'local_storage',
        response_length: cachedHydration.response.length,
      })
    } else {
      setOutput(buildOptimisticTemplate())
      setResponseMode('recovering')
      setResponseModeLabel('Provider Recovering')
    }
    trackEvent('generation_started', {
      module: moduleName,
      request_sequence: requestSequence,
      response_mode: answerDepth,
    })
    trackEvent('search_started', {
      module: moduleName,
      query: primaryValue,
      response_mode: answerDepth,
    })

    try {
      const result = await streamModuleResponse(
        endpoint,
        payload,
        (chunk) => {
          if (!streamHydrated) {
            streamHydrated = true
            setOutput('')
          }
          if (!firstTokenTracked) {
            firstTokenTracked = true
            firstTokenLatencyMs = Math.round(performance.now() - startedAt)
            trackEvent('first_token_received', {
              module: moduleName,
              first_token_latency_ms: firstTokenLatencyMs,
              request_sequence: requestSequence,
              response_mode: answerDepth,
            })
          }
          responseLength += chunk.length
          finalResponse += chunk
          const parseStartedAt = performance.now()
          setOutput((current) => current + chunk)
          frontendStreamParseLatencyMs = Math.max(
            frontendStreamParseLatencyMs,
            Math.round(performance.now() - parseStartedAt),
          )
        },
        (meta) => {
          if (meta.mode) {
            setResponseMode(meta.mode)
          }
          if (meta.label) {
            setResponseModeLabel(meta.label)
          }
        },
        (progress) => {
          setProgressStage(progress.stage)
        },
      )

      if (!result.hadChunks) {
        setEmptyStateMessage(
          result.emptyMessage || 'Scholr did not return any output for this prompt. Try refining it and run again.',
        )
      }
      if (result.mode) {
        setResponseMode(result.mode)
      }
      if (result.modeLabel) {
        setResponseModeLabel(result.modeLabel)
      }
      if (result.mode === 'fallback' || result.mode === 'recovering') {
        trackEvent('fallback_activated', {
          module: moduleName,
          mode: result.mode,
          response_length: responseLength,
        })
      }
      if (result.mode === 'ai') {
        trackEvent('provider_recovery_success', {
          module: moduleName,
          mode: result.mode,
          response_length: responseLength,
        })
      }
      if (result.partialMessage) {
        setError(result.partialMessage)
        setLastAttemptFailed(true)
        trackEvent('partial_output_recovered', {
          module: moduleName,
          response_length: responseLength,
          duration_ms: Math.round(performance.now() - startedAt),
          error_category: result.partialCategory,
          request_sequence: requestSequence,
          response_mode: answerDepth,
        })
      }

      trackEvent('generation_completed', {
        module: moduleName,
        success: result.hadChunks,
        response_length: responseLength,
        duration_ms: Math.round(performance.now() - startedAt),
        output_token_estimate: Math.ceil(responseLength / 4),
        frontend_stream_parse_latency_ms: frontendStreamParseLatencyMs,
        request_sequence: requestSequence,
        response_mode: answerDepth,
      })
      trackEvent('search_completed', {
        module: moduleName,
        mode: answerDepth,
        first_token_ms: firstTokenLatencyMs,
        completion_ms: Math.round(performance.now() - startedAt),
        output_length: responseLength,
      })
      if (finalResponse.trim()) {
        writeLocalCache(finalResponse)
      }
      setHasGeneratedOnce(true)
    } catch (submissionError) {
      const friendlyError =
        submissionError instanceof StreamModuleError
          ? submissionError.message
          : submissionError instanceof Error
            ? submissionError.message
            : 'Scholr could not complete this request right now. Please try again.'

      const errorCategory =
        submissionError instanceof StreamModuleError
          ? submissionError.category
          : 'unexpected'

      trackEvent('generation_failed', {
        module: moduleName,
        success: false,
        response_length: responseLength,
        duration_ms: Math.round(performance.now() - startedAt),
        error_category: errorCategory,
        request_sequence: requestSequence,
        response_mode: answerDepth,
      })
      trackEvent('search_failed', {
        module: moduleName,
        error: friendlyError,
      })
      if (finalResponse.trim()) {
        setError('Answer completed partially. Tap retry for deeper version.')
      } else {
        setError(friendlyError)
      }
      setHasGeneratedOnce(true)
      setLastAttemptFailed(true)
    } finally {
      window.clearTimeout(slowHintTimer)
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
    trackEvent('copy_clicked', {
      module: moduleName,
      response_length: output.length,
    })
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1500)
  }

  const handleClear = () => {
    setOutput('')
    setError('')
    setEmptyStateMessage('')
    setLastAttemptFailed(false)
    setResponseMode('ai')
    setResponseModeLabel('AI Mode')
    trackEvent('clear_clicked', {
      module: moduleName,
      response_length: output.length,
    })
  }

  const handleRetry = async () => {
    trackEvent('retry_clicked', {
      module: moduleName,
      response_length: output.length,
    })
    await runRequest()
  }

  const hasContent = output || error
  const isOptimisticOutput =
    output.startsWith('## Generating short answer')
  const inferredFallbackMode = output.startsWith('## Provider Temporarily Unavailable')
  const activeMode = inferredFallbackMode ? 'fallback' : isOptimisticOutput ? 'recovering' : responseMode
  const activeModeLabel = inferredFallbackMode
    ? 'Fallback Academic Mode'
    : isOptimisticOutput
      ? 'Provider Recovering'
      : responseModeLabel
  const outputStatus = loading
    ? progressStage === 'connecting'
      ? 'Connecting'
      : progressStage === 'thinking'
        ? 'Thinking'
        : progressStage === 'finalizing'
          ? 'Finalizing'
          : 'Writing'
    : error
      ? 'Needs retry'
      : output
      ? 'Ready to review'
      : emptyStateMessage
        ? 'No output returned'
      : 'Waiting for input'
  const modeBadgeClass =
    activeMode === 'fallback'
      ? 'bg-amber-50 text-amber-800 border border-amber-200'
      : activeMode === 'recovering'
        ? 'bg-slate-100 text-slate-700 border border-slate-200'
      : activeMode === 'cache' || activeMode === 'warm_cache'
        ? 'bg-sky-50 text-sky-800 border border-sky-200'
        : 'bg-emerald-50 text-emerald-800 border border-emerald-200'

  return (
    <div className="space-y-5 lg:space-y-8">
      <section className="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-[linear-gradient(135deg,rgba(255,251,235,0.95),rgba(255,255,255,0.98),rgba(240,249,255,0.98))] p-5 shadow-sm sm:rounded-[2rem] sm:p-8">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex w-fit items-center gap-2 rounded-full bg-white/85 px-3 py-1 text-sm font-medium text-amber-800 shadow-sm">
              <Sparkles className="h-4 w-4" />
              Scholr Core
            </div>
            <h1 className="mt-4 text-[1.9rem] font-semibold tracking-tight text-slate-950 sm:text-4xl">
              {title}
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              {description}
            </p>
          </div>
          <div className="grid gap-3 rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-sm sm:grid-cols-2 xl:min-w-[20rem]">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Experience</p>
              <p className="mt-2 text-sm font-medium text-slate-900">
                Fast, readable, and pitch-ready
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Response mode</p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${modeBadgeClass}`}>
                  {activeModeLabel}
                </span>
                <span className="text-sm font-medium text-slate-900">{outputStatus}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)] xl:gap-6">
        <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-sm sm:rounded-[2rem] sm:p-6">
          <div className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Prompt</p>
                <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                  Describe what you need
                </h2>
              </div>
              <div className="flex rounded-2xl bg-slate-100 p-1 text-xs font-medium text-slate-600">
                <button
                  type="button"
                  onClick={() => setAnswerDepth('fast')}
                  disabled={loading}
                  className={`rounded-xl px-3 py-2 transition ${
                    answerDepth === 'fast' ? 'bg-white text-slate-950 shadow-sm' : 'hover:text-slate-900'
                  }`}
                >
                  Fast
                </button>
                <button
                  type="button"
                  onClick={() => setAnswerDepth('deep')}
                  disabled={loading}
                  className={`rounded-xl px-3 py-2 transition ${
                    answerDepth === 'deep' ? 'bg-white text-slate-950 shadow-sm' : 'hover:text-slate-900'
                  }`}
                >
                  Deep
                </button>
              </div>
            </div>

            {secondaryField ? (
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Subject</label>
                <Input
                  placeholder={secondaryField.placeholder}
                  value={secondaryField.value}
                  onChange={(event) => secondaryField.onChange(event.target.value)}
                  className="min-h-12 rounded-2xl border-slate-200 bg-slate-50/70 text-base md:text-base"
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
                rows={secondaryField ? 7 : 9}
                className="min-h-[180px] resize-none rounded-[1.5rem] border-slate-200 bg-slate-50/70 px-4 py-3 text-base leading-7 shadow-none sm:min-h-[220px] md:text-base"
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
                className="min-h-12 w-full rounded-2xl bg-slate-950 px-5 text-white hover:bg-slate-800 sm:w-auto sm:min-w-44"
              >
                {loading ? loadingLabel : idleLabel}
                {!loading ? <ArrowUpRight className="ml-2 h-4 w-4" /> : null}
              </Button>
              <Button
                variant="outline"
                onClick={handleClear}
                disabled={loading || !hasContent}
                className="min-h-12 w-full rounded-2xl border-slate-200 sm:w-auto"
              >
                <RefreshCcw className="mr-2 h-4 w-4" />
                Clear
              </Button>
              <Button
                variant="outline"
                onClick={handleCopy}
                disabled={!output}
                className="min-h-12 w-full rounded-2xl border-slate-200 sm:w-auto"
              >
                <Copy className="mr-2 h-4 w-4" />
                {copied ? 'Copied' : 'Copy'}
              </Button>
            </div>
          </div>
        </div>

        <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-sm sm:rounded-[2rem] sm:p-6">
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
            <div className="flex min-h-[18rem] flex-col items-center justify-center rounded-[1.5rem] border border-dashed border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.9),rgba(255,255,255,0.95))] px-5 py-8 text-center sm:min-h-[24rem] sm:px-6">
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
              <p className="text-sm text-slate-500">
                {slowStreamHint
                  ? 'Still working - shortening answer so mobile does not stall...'
                  : responseMode === 'recovering'
                  ? 'Preparing a useful academic scaffold while the provider recovers...'
                  : 'Generating a polished answer for you...'}
              </p>
            </div>
          ) : null}

          {error ? (
            <div className="rounded-[1.5rem] border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">
              <p>{error}</p>
              {lastAttemptFailed ? (
                <Button
                  variant="outline"
                  onClick={handleRetry}
                  disabled={loading || !primaryValue.trim()}
                  className="mt-4 min-h-11 w-full rounded-2xl border-red-200 bg-white text-red-700 hover:bg-red-100 hover:text-red-800 sm:w-auto"
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
              {!loading && !isOptimisticOutput ? (
                <ResponseFeedback
                  key={`${moduleName}-${primaryValue}-${output.length}`}
                  module={moduleName}
                  query={primaryValue}
                  responseLength={output.length}
                />
              ) : null}
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

export default function AiModulePage(props: AiModulePageProps) {
  return <AiModulePageContent {...props} />
}
