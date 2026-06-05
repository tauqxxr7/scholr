import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Study Notes - Scholr',
  description:
    'Generate structured exam-ready study notes for any BTech subject in seconds. Free for all students.',
}

export default function NotesLayout({ children }: { children: React.ReactNode }) {
  return children
}
