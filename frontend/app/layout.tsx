import type { Metadata } from 'next'

import './globals.css'

export const metadata: Metadata = {
  title: 'Scholr',
  description: 'AI-powered research, notes, and doubt solving for BTech students',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
