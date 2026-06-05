import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Research Papers - Scholr',
  description:
    'Find key research papers, reading order, and research gaps for any BTech topic. Free AI research assistant.',
}

export default function ResearchLayout({ children }: { children: React.ReactNode }) {
  return children
}
