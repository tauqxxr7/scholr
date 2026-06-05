import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Doubt Solver - Scholr',
  description:
    'Get step-by-step explanations for any BTech engineering concept. Free AI doubt solver.',
}

export default function DoubtLayout({ children }: { children: React.ReactNode }) {
  return children
}
