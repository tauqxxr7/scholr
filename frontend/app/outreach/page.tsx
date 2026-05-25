'use client'

import { useState } from 'react'

import { Button } from '@/components/ui/button'

type MessageVariant = {
  label: string
  content: string
}

export default function OutreachPage() {
  const [name, setName] = useState('')
  const [college, setCollege] = useState('')
  const [subject, setSubject] = useState('')
  const [copied, setCopied] = useState('')

  const safeName = name.trim() || 'there'
  const safeCollege = college.trim() || 'your college'
  const safeSubject = subject.trim() || 'BTech'

  const messages: MessageVariant[] = [
    {
      label: 'WhatsApp',
      content: `Hey ${safeName}! I built Scholr — a free AI tool for ${safeSubject} students at ${safeCollege}. You type a topic and get research papers, study notes, or doubt solving in under a minute. Takes 30 seconds to try: scholr-coral.vercel.app — would love your feedback!`,
    },
    {
      label: 'LinkedIn DM',
      content: `Hi ${safeName}, I noticed you're studying ${safeSubject} at ${safeCollege}. I built Scholr, a free AI academic tool for BTech students — research papers, notes, and doubt solving in one place. Would you be open to trying it and sharing feedback? scholr-coral.vercel.app`,
    },
    {
      label: 'Email',
      content: `Subject: Quick favour — try my AI study tool?\n\nHi ${safeName}, I'm Tauqeer, a BTech AI & DS student. I built Scholr — a free tool that helps ${safeSubject} students at ${safeCollege} find research papers, generate notes, and solve doubts instantly. Would you try it for 5 minutes? scholr-coral.vercel.app — I'd genuinely value your feedback.`,
    },
  ]

  const copyMessage = async (label: string, content: string) => {
    await navigator.clipboard.writeText(content)
    setCopied(label)
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6">
      <section className="mx-auto max-w-4xl rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Scholr validation</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
            Student Outreach Generator
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Use this to generate personalised messages for 10-student validation
          </p>
        </div>

        <div className="mt-8 grid gap-3 md:grid-cols-3">
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Student Name"
            className="min-h-11 rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:bg-white"
          />
          <input
            value={college}
            onChange={(event) => setCollege(event.target.value)}
            placeholder="College"
            className="min-h-11 rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:bg-white"
          />
          <input
            value={subject}
            onChange={(event) => setSubject(event.target.value)}
            placeholder="Subject they study"
            className="min-h-11 rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:bg-white"
          />
        </div>

        <Button className="mt-4 rounded-xl bg-slate-950 text-white hover:bg-slate-800">
          Generate Message
        </Button>

        <div className="mt-8 grid gap-4">
          {messages.map((message) => (
            <article
              key={message.label}
              className="rounded-[1.5rem] border border-slate-200 bg-slate-50/70 p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="font-semibold text-slate-950">{message.label}</h2>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="rounded-xl"
                  onClick={() => copyMessage(message.label, message.content)}
                >
                  {copied === message.label ? 'Copied' : 'Copy'}
                </Button>
              </div>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">
                {message.content}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}
