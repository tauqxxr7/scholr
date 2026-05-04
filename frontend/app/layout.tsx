import type { Metadata } from 'next'

import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://scholr-demo.vercel.app'),
  title: {
    default: 'Scholr | AI Academic Platform for BTech Students',
    template: '%s | Scholr',
  },
  description:
    'Scholr is an AI academic workspace for BTech students with research guidance, structured notes, doubt solving, and saved history.',
  openGraph: {
    title: 'Scholr | AI Academic Platform for BTech Students',
    description:
      'Research faster, generate revision notes, and solve doubts in one focused academic workspace.',
    url: 'https://scholr-demo.vercel.app',
    siteName: 'Scholr',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Scholr | AI Academic Platform for BTech Students',
    description:
      'A recruiter-grade MVP for research, notes, doubt solving, and academic history.',
  },
  robots: {
    index: true,
    follow: true,
  },
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
