import Link from 'next/link'
import { Metadata } from 'next'

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

const MOST_SEARCHED = [
  'Machine Learning',
  'Data Structures',
  'Operating Systems',
  'Computer Networks',
  'VLSI Design',
]

const topicCount = TOPICS.reduce((total, category) => total + category.topics.length, 0)

export function generateMetadata(): Metadata {
  const categories = TOPICS.map((category) => category.category).join(', ')
  return {
    title: 'BTech Topics - Scholr AI Academic Platform',
    description: `${topicCount} BTech topics across ${TOPICS.length} engineering disciplines: ${categories}. Get AI-powered research, notes, and doubt solving for free.`,
  }
}

export default function TopicsPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="mb-3 text-3xl font-bold text-gray-900">BTech Topics on Scholr</h1>
      <p className="mb-2 text-sm font-medium text-indigo-600">
        {topicCount} topics across {TOPICS.length} engineering disciplines
      </p>
      <p className="mb-10 text-gray-500">
        Get AI-powered research papers, study notes, and doubt solving for any engineering topic.
        Free for all BTech students.
      </p>

      <section className="mb-12">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Most searched</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {MOST_SEARCHED.map((topic) => (
            <Link
              key={topic}
              href={`/research?topic=${encodeURIComponent(topic)}`}
              className="group rounded-xl border bg-white p-5 text-gray-800 transition hover:border-indigo-400 hover:shadow-sm"
            >
              <span className="mb-3 inline-flex rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
                Popular
              </span>
              <div className="flex items-center justify-between gap-4">
                <span className="font-semibold">{topic}</span>
                <span className="text-sm text-indigo-400 group-hover:text-indigo-600">Try -&gt;</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

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
                  <span className="text-xs text-indigo-400 group-hover:text-indigo-600">Try -&gt;</span>
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
          - Scholr works for any engineering subject.
        </p>
      </div>

      <div className="mt-8 text-center">
        <Link href="/research" className="text-sm font-medium text-indigo-600 hover:underline">
          Can&apos;t find your topic? Ask Scholr anything -&gt;
        </Link>
      </div>
    </main>
  )
}
