import Link from 'next/link'

export const metadata = {
  title: 'Privacy',
  description: 'Privacy information for the Scholr MVP.',
}

const sections = [
  {
    title: 'What Scholr stores',
    body: 'Scholr stores the search queries you send, completed AI responses, and response feedback so dashboard history and quality improvements can work. For the MVP, that history lives in the configured project database.',
  },
  {
    title: 'Analytics and feedback',
    body: 'Scholr may collect anonymous usage analytics and helpful/not-helpful feedback to understand which academic workflows are useful. We do not sell your personal data.',
  },
  {
    title: 'How the AI works',
    body: 'Scholr sends your prompt to a third-party AI provider to generate research guidance, notes, and doubt explanations. Do not submit secrets, passwords, or sensitive personal information.',
  },
  {
    title: 'Accuracy and verification',
    body: 'Scholr is an academic assistant, not an authoritative source. You should verify facts, formulas, citations, and recommendations before relying on them for coursework, exams, or projects.',
  },
  {
    title: 'Contact',
    body: 'Questions or privacy requests? Email tauqeerplayer@gmail.com.',
  },
]

export default function PrivacyPage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
      <div className="mx-auto max-w-3xl rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm sm:rounded-[2rem] sm:p-8">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-6">
          <Link href="/" className="text-sm font-medium text-slate-500 transition hover:text-slate-950">
            Back to Scholr
          </Link>
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Privacy</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Privacy notice for the Scholr MVP
            </h1>
            <p className="mt-3 text-sm leading-7 text-slate-600 sm:text-base">
              This is a simple, product-stage privacy page for the current MVP. Scholr does not
              sell personal data, and this notice should be reviewed before large-scale launch.
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-4 sm:mt-8 sm:space-y-6">
          {sections.map((section) => (
            <section
              key={section.title}
              className="rounded-[1.5rem] border border-slate-200 bg-slate-50/60 p-4 sm:p-5"
            >
              <h2 className="text-lg font-semibold text-slate-950">{section.title}</h2>
              <p className="mt-2 text-sm leading-7 text-slate-600 sm:text-base">{section.body}</p>
            </section>
          ))}
        </div>
      </div>
    </main>
  )
}
