'use client'

import { useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  AlertCircle,
  ArrowUpRight,
  BookText,
  CheckCircle2,
  Copy,
  FileQuestion,
  LoaderCircle,
  NotebookPen,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  TimerReset,
  Upload,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { trackEvent } from '@/lib/analytics'
import {
  answerDocumentQuestion,
  getDocumentHealth,
  type DocumentAnswerResult,
  type DocumentHealthResult,
  type DocumentUploadResult,
  StreamModuleError,
  uploadDocument,
} from '@/lib/api'

type WorkflowPreset = {
  label: string
  description: string
  buildPrompt: (documentTitle: string) => string
}

const studyWorkflows: WorkflowPreset[] = [
  {
    label: 'Generate Revision Notes',
    description: 'Turn the uploaded PDF into exam-ready revision structure.',
    buildPrompt: (title) =>
      `Create concise revision notes from "${title}". Use only the uploaded document. Include key definitions, core points, one example where helpful, and short viva-style checks.`,
  },
  {
    label: 'Important Questions',
    description: 'Extract likely study questions without fake certainty.',
    buildPrompt: (title) =>
      `From "${title}", list the most important study questions a student should revise. Stay conservative and only use what is clearly supported by the uploaded material.`,
  },
  {
    label: 'Explain Like Exam Answer',
    description: 'Structure a direct, textbook-style answer.',
    buildPrompt: (title) =>
      `Using "${title}", write a structured exam-style answer for the most central topic in the uploaded material. Keep it readable, direct, and grounded in the document.`,
  },
  {
    label: 'Quick Revision',
    description: 'Summarize the fastest useful recap.',
    buildPrompt: (title) =>
      `Give me a quick revision summary from "${title}" with the top concepts, must-remember points, and one or two likely viva triggers.`,
  },
  {
    label: 'Viva Questions',
    description: 'Generate oral-exam style questions grounded in the PDF.',
    buildPrompt: (title) =>
      `Using "${title}", generate viva-style questions and short answer cues. Use only what is grounded in the uploaded document.`,
  },
]

const pyqWorkflows: WorkflowPreset[] = [
  {
    label: 'Repeated Topics',
    description: 'Find visibly repeated themes in the uploaded question paper set.',
    buildPrompt: (title) =>
      `Analyze "${title}" as a previous year question document. Identify repeated topics only when the PDF clearly supports them. Do not invent probability claims.`,
  },
  {
    label: 'High-Frequency Units',
    description: 'Group questions into units or themes conservatively.',
    buildPrompt: (title) =>
      `Analyze "${title}" and group the question areas into likely units or themes based only on repeated or clustered evidence in the document. Avoid fake frequency claims.`,
  },
  {
    label: 'Exam-Priority Revision Areas',
    description: 'Highlight what looks worth revising first.',
    buildPrompt: (title) =>
      `From "${title}", suggest exam-priority revision areas using only the uploaded material. Be conservative, explain your reasoning, and avoid fake probability language.`,
  },
  {
    label: 'Important Concepts',
    description: 'Extract the concepts students should know before the exam.',
    buildPrompt: (title) =>
      `From "${title}", list the important concepts students should revise before the exam. Keep the answer grounded in the uploaded PDF and say when evidence is weak.`,
  },
]

const retrievalModeLabel: Record<string, string> = {
  lexical: 'Lexical Retrieval',
  lexical_fallback: 'Lexical Retrieval',
  semantic: 'Semantic Retrieval',
  semantic_vector: 'Semantic Retrieval',
  hybrid: 'Hybrid Retrieval',
}

function DocumentWorkspaceContent() {
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [documentHealth, setDocumentHealth] = useState<DocumentHealthResult | null>(null)
  const [healthChecking, setHealthChecking] = useState(true)
  const [healthError, setHealthError] = useState('')
  const [selectedFileName, setSelectedFileName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadError, setUploadError] = useState('')
  const [uploadedDocument, setUploadedDocument] = useState<DocumentUploadResult | null>(null)
  const [question, setQuestion] = useState('')
  const [answerResult, setAnswerResult] = useState<DocumentAnswerResult | null>(null)
  const [answering, setAnswering] = useState(false)
  const [answerError, setAnswerError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    trackEvent('module_opened', {
      module: 'documents',
      entrypoint: 'module_page',
    })

    const timeout = new Promise<never>((_, reject) => {
      window.setTimeout(() => reject(new Error('Document health timed out')), 5000)
    })

    Promise.race([getDocumentHealth(), timeout])
      .then(setDocumentHealth)
      .catch(() => setHealthError('Document health could not be loaded right now. Upload still may work.'))
      .finally(() => setHealthChecking(false))
  }, [])

  const uploadModeLabel = useMemo(() => {
    if (!uploadedDocument) {
      return documentHealth?.retrieval_default_mode === 'semantic'
        ? 'Semantic-ready path'
        : 'Retrieval-first path'
    }

    if (uploadedDocument.status === 'ready') {
      return 'Document Ready'
    }

    return 'Retrieval-only mode'
  }, [documentHealth?.retrieval_default_mode, uploadedDocument])

  const answerModeBadge = useMemo(() => {
    if (!answerResult) {
      return null
    }

    if (answerResult.generation_used) {
      return {
        label: 'AI Mode',
        className: 'bg-emerald-50 text-emerald-800 border border-emerald-200',
      }
    }

    return {
      label: 'Retrieval-only mode',
      className: 'bg-amber-50 text-amber-800 border border-amber-200',
    }
  }, [answerResult])

  const retrievalBadge = useMemo(() => {
    if (!answerResult) {
      return documentHealth
        ? {
            label:
              documentHealth.retrieval_default_mode === 'semantic'
                ? 'Semantic retrieval available'
                : 'Lexical retrieval active',
            className:
              documentHealth.retrieval_default_mode === 'semantic'
                ? 'bg-sky-50 text-sky-800 border border-sky-200'
                : 'bg-slate-100 text-slate-700 border border-slate-200',
          }
        : null
    }

      return {
        label: retrievalModeLabel[answerResult.retrieval_mode] || answerResult.retrieval_mode,
        className:
        answerResult.retrieval_mode === 'semantic' || answerResult.retrieval_mode === 'semantic_vector'
          ? 'bg-sky-50 text-sky-800 border border-sky-200'
          : answerResult.retrieval_mode === 'hybrid'
            ? 'bg-violet-50 text-violet-800 border border-violet-200'
            : 'bg-slate-100 text-slate-700 border border-slate-200',
    }
  }, [answerResult, documentHealth])

  const renderHealthValue = (value: string) =>
    healthChecking ? (
      <div className="mt-3 space-y-2" aria-label="Checking system status">
        <div className="h-3 w-28 animate-pulse rounded-full bg-slate-200" />
        <div className="h-3 w-20 animate-pulse rounded-full bg-slate-200" />
      </div>
    ) : (
      <p className="mt-2 text-sm font-medium text-slate-900">{value}</p>
    )

  const uploadDocumentFile = async (file: File) => {
    setUploading(true)
    setUploadProgress(0)
    setUploadError('')
    setAnswerError('')
    setAnswerResult(null)
    setUploadedDocument(null)
    setSelectedFileName(file.name)
    trackEvent('document_upload_started', {
      module: 'documents_upload',
    })

    try {
      const result = await uploadDocument(file, setUploadProgress)
      setUploadedDocument(result)
      setUploadProgress(100)
      trackEvent('document_upload_completed', {
        module: 'documents_upload',
        success: true,
        upload_pages: result.page_count,
        chunk_count: result.chunk_count,
      })
    } catch (error) {
      const message =
        error instanceof StreamModuleError
          ? error.message
          : 'Scholr could not prepare this PDF right now. Please try another text-based PDF.'
      setUploadError(message)
      trackEvent('document_upload_failed', {
        module: 'documents_upload',
        success: false,
        error_category: error instanceof StreamModuleError ? error.category : 'upload_failed',
      })
    } finally {
      setUploading(false)
    }
  }

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }
    await uploadDocumentFile(file)
  }

  const handleWorkflowClick = (workflow: WorkflowPreset) => {
    const title = uploadedDocument?.title || 'the uploaded document'
    setQuestion(workflow.buildPrompt(title))
  }

  const handleAsk = async () => {
    if (!uploadedDocument || !question.trim()) {
      return
    }

    setAnswering(true)
    setAnswerError('')
    setAnswerResult(null)
    trackEvent('document_answer_started', {
      module: 'documents_answer',
    })

    const startedAt = performance.now()

    try {
      const result = await answerDocumentQuestion({
        document_id: uploadedDocument.document_id,
        question: question.trim(),
        top_k: 4,
      })
      setAnswerResult(result)
      trackEvent('document_answer_completed', {
        module: 'documents_answer',
        success: true,
        response_length: result.answer.length,
        duration_ms: Math.round(performance.now() - startedAt),
        retrieval_mode: result.retrieval_mode,
        citations_count: result.citations.length,
      })
    } catch (error) {
      const message =
        error instanceof StreamModuleError
          ? error.message
          : 'Scholr could not answer from this document right now. Please retry.'
      setAnswerError(message)
      trackEvent('document_answer_failed', {
        module: 'documents_answer',
        success: false,
        duration_ms: Math.round(performance.now() - startedAt),
        error_category: error instanceof StreamModuleError ? error.category : 'document_answer_failed',
      })
    } finally {
      setAnswering(false)
    }
  }

  const handleCopy = async () => {
    if (!answerResult?.answer) {
      return
    }
    await navigator.clipboard.writeText(answerResult.answer)
    setCopied(true)
    trackEvent('copy_clicked', {
      module: 'documents_answer',
      response_length: answerResult.answer.length,
    })
    window.setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="space-y-5 lg:space-y-8">
      <section className="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-[linear-gradient(135deg,rgba(254,243,199,0.95),rgba(255,255,255,0.98),rgba(240,249,255,0.98))] p-5 shadow-sm sm:rounded-[2rem] sm:p-8">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex w-fit items-center gap-2 rounded-full bg-white/85 px-3 py-1 text-sm font-medium text-amber-800 shadow-sm">
              <BookText className="h-4 w-4" />
              Scholr Document Intelligence
            </div>
            <h1 className="mt-4 text-[1.9rem] font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Upload a PDF, ask grounded questions, and study from cited evidence.
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              This is the first live document workflow for Scholr. It supports retrieval-grounded
              answers, citation snippets, PYQ analysis prompts, and graceful retrieval-only mode
              when embeddings or provider-backed synthesis are unavailable.
            </p>
          </div>
          <div className="grid gap-3 rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-sm sm:grid-cols-2 xl:min-w-[21rem]">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Upload mode</p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {uploadModeLabel}
                </span>
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Current retrieval</p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                {retrievalBadge ? (
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${retrievalBadge.className}`}>
                    {retrievalBadge.label}
                  </span>
                ) : (
                  <span className="text-sm font-medium text-slate-500">Loading</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)] xl:gap-6">
        <div className="space-y-5">
          <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-sm sm:rounded-[2rem] sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Step 1</p>
                <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                  Upload your PDF
                </h2>
              </div>
              {uploadedDocument ? (
                <Badge className="rounded-full bg-emerald-50 px-3 py-1 text-emerald-800 shadow-none">
                  <CheckCircle2 className="mr-1 h-3.5 w-3.5" />
                  Document Ready
                </Badge>
              ) : null}
            </div>

            <div className="mt-5 rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50/80 p-4 sm:p-5">
              <div className="flex flex-col gap-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <Button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="min-h-12 rounded-2xl bg-slate-950 text-white hover:bg-slate-800"
                  >
                    {uploading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
                    {uploading ? 'Uploading PDF...' : 'Choose PDF'}
                  </Button>
                  <p className="text-sm text-slate-500">
                    {selectedFileName || 'Upload class notes, a chapter, lab manual, PYQ set, or a paper.'}
                  </p>
                </div>

                {uploading ? (
                  <div className="space-y-2">
                    <div className="h-2 rounded-full bg-slate-200">
                      <div
                        className="h-2 rounded-full bg-slate-950 transition-all"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                    <p className="text-xs text-slate-500">{uploadProgress}% uploaded</p>
                  </div>
                ) : null}

                {uploadError ? (
                  <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {uploadError}
                  </div>
                ) : null}

                {uploadedDocument ? (
                  <div className="rounded-[1.5rem] border border-slate-200 bg-white px-4 py-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-950">{uploadedDocument.title}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          {uploadedDocument.page_count} page{uploadedDocument.page_count === 1 ? '' : 's'} •{' '}
                          {uploadedDocument.chunk_count} chunk{uploadedDocument.chunk_count === 1 ? '' : 's'}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Badge variant="outline" className="rounded-full">
                          {uploadedDocument.status === 'ready' ? 'Semantic-ready' : 'Retrieval-first'}
                        </Badge>
                        {uploadedDocument.status !== 'ready' ? (
                          <Badge className="rounded-full bg-amber-50 text-amber-800 shadow-none">
                            Retrieval-only mode
                          </Badge>
                        ) : null}
                      </div>
                    </div>
                    {uploadedDocument.warning ? (
                      <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                        {uploadedDocument.warning}
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-sm sm:rounded-[2rem] sm:p-6">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Step 2</p>
              <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                Choose a real student workflow
              </h2>
            </div>

            <div className="mt-5 grid gap-4">
              <div>
                <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-900">
                  <NotebookPen className="h-4 w-4 text-amber-700" />
                  Study workflows
                </div>
                <div className="flex flex-wrap gap-2">
                  {studyWorkflows.map((workflow) => (
                    <button
                      key={workflow.label}
                      type="button"
                      onClick={() => handleWorkflowClick(workflow)}
                      disabled={!uploadedDocument}
                      className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition hover:border-slate-300 hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {workflow.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-900">
                  <ScanSearch className="h-4 w-4 text-slate-700" />
                  PYQ intelligence
                </div>
                <div className="flex flex-wrap gap-2">
                  {pyqWorkflows.map((workflow) => (
                    <button
                      key={workflow.label}
                      type="button"
                      onClick={() => handleWorkflowClick(workflow)}
                      disabled={!uploadedDocument}
                      className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition hover:border-slate-300 hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {workflow.label}
                    </button>
                  ))}
                </div>
                <p className="mt-3 text-xs leading-5 text-slate-500">
                  PYQ prompts are conservative by design. Scholr should surface repeated themes and
                  exam-priority areas only when the uploaded PDF actually supports them.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-sm sm:rounded-[2rem] sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Step 3</p>
                <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                  Ask questions about the uploaded PDF
                </h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {answerModeBadge ? (
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${answerModeBadge.className}`}>
                    {answerModeBadge.label}
                  </span>
                ) : null}
                {retrievalBadge ? (
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${retrievalBadge.className}`}>
                    {retrievalBadge.label}
                  </span>
                ) : null}
              </div>
            </div>

            <div className="mt-5 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Document question or workflow prompt</label>
                <Textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={8}
                  disabled={!uploadedDocument || answering}
                  placeholder="Ask about the PDF, request revision notes, extract important concepts, or analyze a PYQ document."
                  className="min-h-[190px] resize-none rounded-[1.5rem] border-slate-200 bg-slate-50/70 px-4 py-3 text-base leading-7 md:text-base"
                />
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                <Button
                  type="button"
                  onClick={handleAsk}
                  disabled={!uploadedDocument || !question.trim() || answering}
                  className="min-h-12 rounded-2xl bg-slate-950 text-white hover:bg-slate-800"
                >
                  {answering ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <FileQuestion className="mr-2 h-4 w-4" />}
                  {answering ? 'Reading document...' : 'Ask the document'}
                  {!answering ? <ArrowUpRight className="ml-2 h-4 w-4" /> : null}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCopy}
                  disabled={!answerResult?.answer}
                  className="min-h-12 rounded-2xl border-slate-200"
                >
                  <Copy className="mr-2 h-4 w-4" />
                  {copied ? 'Copied' : 'Copy answer'}
                </Button>
              </div>

              {healthError ? (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                  {healthError}
                </div>
              ) : null}

              {answerError ? (
                <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {answerError}
                </div>
              ) : null}

              {answering && !answerResult ? (
                <div className="space-y-4">
                  <div className="animate-pulse rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5">
                    <div className="h-4 w-36 rounded-full bg-slate-200" />
                    <div className="mt-5 space-y-3">
                      <div className="h-4 w-full rounded-full bg-slate-200" />
                      <div className="h-4 w-[90%] rounded-full bg-slate-200" />
                      <div className="h-4 w-[78%] rounded-full bg-slate-200" />
                    </div>
                  </div>
                  <p className="text-sm text-slate-500">
                    Scholr is reading the uploaded document and preparing a grounded answer.
                  </p>
                </div>
              ) : null}

              {answerResult ? (
                <div className="space-y-4">
                  <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50/60 p-4">
                    <div className="flex flex-wrap gap-2">
                      <Badge className="rounded-full bg-emerald-50 text-emerald-800 shadow-none">
                        Document grounded answer
                      </Badge>
                      <Badge variant="outline" className="rounded-full">
                        Confidence: {answerResult.confidence}
                      </Badge>
                      <Badge variant="outline" className="rounded-full">
                        Citations: {answerResult.citations.length}
                      </Badge>
                    </div>

                    <div className="scholr-markdown mt-4">
                      <ReactMarkdown>{answerResult.answer}</ReactMarkdown>
                    </div>

                    {answerResult.warning ? (
                      <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                        {answerResult.warning}
                      </div>
                    ) : null}
                  </div>

                  <div className="rounded-[1.5rem] border border-slate-200 bg-white p-4">
                    <div className="mb-4 flex items-center gap-2 text-sm font-medium text-slate-900">
                      <ShieldCheck className="h-4 w-4 text-emerald-700" />
                      Citations and source chunks
                    </div>
                    <div className="space-y-3">
                      {answerResult.citations.map((citation, index) => (
                        <div
                          key={`${citation.document_name}-${citation.page_number}-${citation.chunk_index}-${index}`}
                          className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4"
                        >
                          <div className="flex flex-wrap items-center gap-2">
                            <Badge variant="outline" className="rounded-full capitalize">
                              {citation.document_name}
                            </Badge>
                            <Badge variant="outline" className="rounded-full">
                              {citation.citation_label}
                            </Badge>
                            <Badge variant="outline" className="rounded-full">
                              Chunk {citation.chunk_index}
                            </Badge>
                          </div>
                          <p className="mt-3 text-sm leading-6 text-slate-600">{citation.snippet}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {answerResult.limitations.length ? (
                    <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50/60 p-4">
                      <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-900">
                        <AlertCircle className="h-4 w-4 text-amber-700" />
                        Confidence and limitations
                      </div>
                      <ul className="ml-5 list-disc space-y-2 text-sm leading-6 text-slate-600">
                        {answerResult.limitations.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              ) : null}

              {!answerResult && !answering ? (
                <div className="rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center">
                  <div className="mx-auto w-fit rounded-full bg-white p-3 shadow-sm">
                    <Sparkles className="h-5 w-5 text-amber-700" />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-slate-950">No document answer yet</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    Upload a PDF, choose a workflow, or ask a grounded question. Scholr will show
                    the retrieval mode, answer quality limits, and cited snippets instead of hiding
                    how the result was produced.
                  </p>
                </div>
              ) : null}
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-sm sm:rounded-[2rem] sm:p-6">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-900">
              <TimerReset className="h-4 w-4 text-slate-700" />
              {healthChecking ? 'Checking system status...' : 'Retrieval and embedding health'}
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">PDF parsing</p>
                {renderHealthValue(documentHealth?.pdf_parsing_available ? 'Available' : 'Unavailable')}
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Embeddings</p>
                {renderHealthValue(documentHealth?.embedding_health || 'Unavailable')}
                {!healthChecking && documentHealth?.embedding_provider ? (
                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    Provider: {documentHealth.embedding_provider}
                  </p>
                ) : null}
                {!healthChecking && documentHealth?.embedding_model ? (
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Model: {documentHealth.embedding_model}
                  </p>
                ) : null}
                {!healthChecking && documentHealth?.provider_error_category ? (
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    State: {documentHealth.provider_error_category}
                  </p>
                ) : null}
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Vector retrieval</p>
                {renderHealthValue(
                  documentHealth?.semantic_retrieval_ready
                    ? 'Active'
                    : documentHealth?.vector_store_available
                      ? 'Standing by'
                      : 'Lexical fallback active',
                )}
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Default mode</p>
                {renderHealthValue(documentHealth?.retrieval_default_mode || 'Unavailable')}
                {!healthChecking && documentHealth?.retrieval_health ? (
                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    Retrieval health: {documentHealth.retrieval_health}
                  </p>
                ) : null}
                {!healthChecking && documentHealth?.lexical_fallback_ready ? (
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Lexical fallback remains available if semantic retrieval is degraded.
                  </p>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default function DocumentWorkspace() {
  return <DocumentWorkspaceContent />
}
