import Link from 'next/link'

export const metadata = {
  title: 'Terms',
  description: 'Terms of use for the Scholr MVP.',
}

const sections = [
  {
    title: 'Service scope',
    body: 'Scholr is an academic AI assistant for BTech students. It helps with research direction, structured notes, and doubt solving, but it is not a substitute for textbooks, faculty guidance, or official academic resources.',
  },
  {
    title: 'No guarantee of correctness',
    body: 'AI-generated output can be incomplete or wrong. You are responsible for reviewing and verifying any result before using it in exams, assignments, reports, or projects.',
  },
  {
    title: 'Acceptable use',
    body: 'Do not use Scholr to upload unlawful material, abuse the service, or attempt to extract or misuse secrets. Keep prompts focused on legitimate academic workflows.',
  },
  {
    title: 'MVP disclaimer',
    body: 'This product is an early-stage MVP and may change quickly. Features, uptime, and stored history are provided on a best-effort basis until the production platform is fully hardened.',
  },
]

export default function TermsPage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)] px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
      <div className="mx-auto max-w-3xl rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm sm:rounded-[2rem] sm:p-8">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-6">
          <Link href="/" className="text-sm font-medium text-slate-500 transition hover:text-slate-950">
            Back to Scholr
          </Link>
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Terms</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Terms of use for the Scholr MVP
            </h1>
            <p className="mt-3 text-sm leading-7 text-slate-600 sm:text-base">
              These terms are intentionally lightweight for an early product. Before a public
              rollout, they should be reviewed and upgraded with proper legal counsel.
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
