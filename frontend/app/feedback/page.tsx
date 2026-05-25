'use client'

import { FormEvent, useState } from 'react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'

type SubmitState = 'idle' | 'loading' | 'success' | 'error'

export default function FeedbackPage() {
  const [submitState, setSubmitState] = useState<SubmitState>('idle')
  const [form, setForm] = useState({
    name: '',
    college_year: '',
    module_used: 'Research',
    was_useful: 'Yes',
    what_was_missing: '',
    would_use_again: 'Definitely',
    other_feedback: '',
  })

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitState('loading')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '')
      if (!apiUrl) {
        throw new Error('Missing API URL')
      }

      const response = await fetch(`${apiUrl}/api/feedback-form`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })

      if (!response.ok) {
        throw new Error('Feedback request failed')
      }

      setSubmitState('success')
    } catch {
      setSubmitState('error')
    }
  }

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#fffdf7_0%,#ffffff_55%,#f8fafc_100%)] px-5 py-12 text-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <Link href="/" className="text-sm font-medium text-slate-500 transition hover:text-slate-950">
          Back to Scholr
        </Link>

        <section className="mt-6 rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Help improve Scholr</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600 sm:text-base">
            Takes 2 minutes. Your feedback directly shapes what we build next.
          </p>

          {submitState === 'success' ? (
            <div className="mt-8 rounded-2xl border border-emerald-100 bg-emerald-50 p-5 text-sm font-medium leading-6 text-emerald-800">
              Thank you! Your feedback helps us build better tools for BTech students.
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="space-y-2 text-sm font-medium text-slate-700">
                  Name <span className="font-normal text-slate-400">(optional)</span>
                  <input
                    value={form.name}
                    onChange={(event) => updateField('name', event.target.value)}
                    className="min-h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-slate-400 focus:bg-white"
                  />
                </label>
                <label className="space-y-2 text-sm font-medium text-slate-700">
                  College and Year <span className="font-normal text-slate-400">(optional)</span>
                  <input
                    value={form.college_year}
                    onChange={(event) => updateField('college_year', event.target.value)}
                    className="min-h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-slate-400 focus:bg-white"
                  />
                </label>
              </div>

              <label className="space-y-2 text-sm font-medium text-slate-700">
                Which module did you use?
                <select
                  value={form.module_used}
                  onChange={(event) => updateField('module_used', event.target.value)}
                  className="min-h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-slate-400 focus:bg-white"
                >
                  {['Research', 'Notes', 'Doubt', 'Documents', 'All'].map((item) => (
                    <option key={item}>{item}</option>
                  ))}
                </select>
              </label>

              <div className="grid gap-4 sm:grid-cols-2">
                <fieldset className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <legend className="px-1 text-sm font-medium text-slate-700">Was it useful?</legend>
                  {['Yes', 'Somewhat', 'No'].map((item) => (
                    <label key={item} className="flex items-center gap-2 text-sm text-slate-600">
                      <input
                        type="radio"
                        name="was_useful"
                        checked={form.was_useful === item}
                        onChange={() => updateField('was_useful', item)}
                      />
                      {item}
                    </label>
                  ))}
                </fieldset>
                <fieldset className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <legend className="px-1 text-sm font-medium text-slate-700">Would you use this again?</legend>
                  {['Definitely', 'Maybe', 'No'].map((item) => (
                    <label key={item} className="flex items-center gap-2 text-sm text-slate-600">
                      <input
                        type="radio"
                        name="would_use_again"
                        checked={form.would_use_again === item}
                        onChange={() => updateField('would_use_again', item)}
                      />
                      {item}
                    </label>
                  ))}
                </fieldset>
              </div>

              <label className="space-y-2 text-sm font-medium text-slate-700">
                What was missing or confusing? <span className="font-normal text-slate-400">(optional)</span>
                <textarea
                  value={form.what_was_missing}
                  onChange={(event) => updateField('what_was_missing', event.target.value)}
                  rows={4}
                  className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-slate-400 focus:bg-white"
                />
              </label>

              <label className="space-y-2 text-sm font-medium text-slate-700">
                Any other feedback? <span className="font-normal text-slate-400">(optional)</span>
                <textarea
                  value={form.other_feedback}
                  onChange={(event) => updateField('other_feedback', event.target.value)}
                  rows={4}
                  className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-slate-400 focus:bg-white"
                />
              </label>

              {submitState === 'error' ? (
                <p className="text-sm text-red-600">Something went wrong. Please try again.</p>
              ) : null}

              <Button
                type="submit"
                disabled={submitState === 'loading'}
                className="min-h-11 rounded-xl bg-slate-950 px-5 text-sm text-white hover:bg-slate-800"
              >
                {submitState === 'loading' ? 'Submitting...' : 'Submit feedback'}
              </Button>
            </form>
          )}
        </section>
      </div>
    </main>
  )
}
