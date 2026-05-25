import Link from 'next/link'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BTech Topics — Scholr AI Academic Platform',
  description:
    'AI-powered research, notes, and doubt solving for common BTech engineering topics. Free for all students.',
}

const TOPICS = [
  {
    category: 'Computer Science',
    topics: [
      'Data Structures and Algorithms',
      'Operating Systems',
      'Computer Networks',
      'Database Management Systems',
      'Compiler Design',
      'Software Engineering',
      'Machine Learning',
      'Deep Learning',
      'Natural Language Processing',
      'Computer Vision',
    ],
  },
  {
    category: 'Electronics',
    topics: [
      'Digital Electronics',
      'Signals and Systems',
      'VLSI Design',
      'Microprocessors',
      'Communication Systems',
      'Control Systems',
      'Power Electronics',
      'Embedded Systems',
    ],
  },
  {
    category: 'Mathematics',
    topics: [
      'Engineering Mathematics',
      'Linear Algebra',
      'Probability and Statistics',
      'Discrete Mathematics',
      'Numerical Methods',
    ],
  },
  {
    category: 'Core Engineering',
    topics: [
      'Engineering Mechanics',
      'Thermodynamics',
      'Fluid Mechanics',
      'Strength of Materials',
      'Manufacturing Processes',
    ],
  },
]

export default function TopicsPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="mb-3 text-3xl font-bold text-gray-900">BTech Topics on Scholr</h1>
      <p className="mb-10 text-gray-500">
        Get AI-powered research papers, study notes, and doubt solving for any engineering topic.
        Free for all BTech students.
      </p>

      <div className="space-y-10">
        {TOPICS.map((category) => (
          <div key={category.category}>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">{category.category}</h2>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {category.topics.map((topic) => (
                <Link
                  key={topic}
                  href={`/research?topic=${encodeURIComponent(topic)}`}
                  className="group flex items-center justify-between rounded-lg border bg-white px-4 py-3 text-sm text-gray-700 transition hover:border-indigo-400 hover:shadow-sm"
                >
                  <span>{topic}</span>
                  <span className="text-xs text-indigo-400 group-hover:text-indigo-600">Try →</span>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 rounded-xl bg-indigo-50 p-6">
        <p className="mb-1 text-sm font-medium text-indigo-700">Not finding your topic?</p>
        <p className="text-sm text-indigo-600">
          Type any BTech topic directly on the{' '}
          <Link href="/research" className="underline">
            Research page
          </Link>{' '}
          — Scholr works for any engineering subject.
        </p>
      </div>
    </main>
  )
}
