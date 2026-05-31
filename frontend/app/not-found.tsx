import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="px-6 text-center">
        <p className="mb-4 text-6xl font-bold text-indigo-600">404</p>
        <h1 className="mb-2 text-xl font-semibold text-gray-900">Page not found</h1>
        <p className="mb-8 text-gray-500">This page does not exist. Try one of these:</p>
        <div className="flex flex-col justify-center gap-3 sm:flex-row">
          <Link
            href="/research"
            className="rounded-lg bg-indigo-600 px-5 py-2 text-sm text-white hover:bg-indigo-700"
          >
            Research papers
          </Link>
          <Link
            href="/notes"
            className="rounded-lg border px-5 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Study notes
          </Link>
          <Link
            href="/"
            className="rounded-lg border px-5 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Home
          </Link>
        </div>
      </div>
    </main>
  )
}
