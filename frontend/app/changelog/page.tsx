import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Changelog - Scholr',
  description: 'What is new in Scholr - the AI academic platform for BTech students.',
}

const CHANGELOG = [
  {
    version: '1.5.0',
    date: 'May 2026',
    changes: [
      'Added semantic search across your history',
      'PDF export for all AI responses',
      'Keyboard shortcuts (Ctrl+Enter, Escape, Ctrl+K)',
      'Backend status indicator with cold-start warning',
      'One-click example demos on all module pages',
      'Share button for AI responses',
      'Email waitlist for product updates',
    ],
  },
  {
    version: '1.0.0',
    date: 'April 2026',
    changes: [
      'Research module: papers, reading order, research gaps',
      'Notes module: structured exam-ready notes',
      'Doubt solver: step-by-step explanations',
      'Document intelligence: upload and query PDFs',
      'Real-time streaming AI responses',
      'Dashboard with search history',
      'Fast and Deep response modes',
    ],
  },
]

export default function ChangelogPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">Changelog</h1>
      <p className="mb-10 text-sm text-gray-500">What is new in Scholr. Updated regularly.</p>
      <div className="space-y-10">
        {CHANGELOG.map((release) => (
          <div key={release.version}>
            <div className="mb-4 flex items-center gap-3">
              <span className="rounded bg-indigo-50 px-2 py-0.5 font-mono text-sm text-indigo-700">
                v{release.version}
              </span>
              <span className="text-sm text-gray-400">{release.date}</span>
            </div>
            <ul className="space-y-2">
              {release.changes.map((change) => (
                <li key={change} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="mt-0.5 text-indigo-400">+</span>
                  {change}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="mt-12 text-sm text-gray-400">
        Built by{' '}
        <a
          href="https://www.linkedin.com/in/tauqeer-sameer-85b868235"
          className="text-indigo-500 hover:underline"
        >
          Tauqeer Bharde
        </a>
      </div>
    </main>
  )
}
