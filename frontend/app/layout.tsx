import type { Metadata, Viewport } from 'next'

import PostHogProvider from '@/components/PostHogProvider'

import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://scholr-coral.vercel.app'),
  applicationName: 'Scholr',
  manifest: '/manifest.webmanifest',
  title: {
    default: 'Scholr | AI Academic Platform for BTech Students',
    template: '%s | Scholr',
  },
  description:
    'Scholr is an AI academic workspace for BTech students with research guidance, structured notes, doubt solving, and saved history.',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/favicon.ico',
  },
  openGraph: {
    title: 'Scholr | AI Academic Platform for BTech Students',
    description:
      'Research faster, generate revision notes, and solve doubts in one focused academic workspace.',
    url: 'https://scholr-coral.vercel.app',
    siteName: 'Scholr',
    type: 'website',
    images: [
      {
        url: '/screenshots/landing.png',
        width: 1918,
        height: 1010,
        alt: 'Scholr landing page',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Scholr | AI Academic Platform for BTech Students',
    description:
      'A recruiter-grade MVP for research, notes, doubt solving, and academic history.',
    images: ['/screenshots/landing.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
  appleWebApp: {
    capable: true,
    title: 'Scholr',
    statusBarStyle: 'default',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#020617',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  )
}
