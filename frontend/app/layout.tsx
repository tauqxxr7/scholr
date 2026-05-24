import type { Metadata, Viewport } from 'next'
import { ClerkProvider } from '@clerk/nextjs'

import PostHogProvider from '@/components/PostHogProvider'

import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://scholr-coral.vercel.app'),
  applicationName: 'Scholr',
  manifest: '/manifest.webmanifest',
  title: {
    default: 'Scholr — AI Academic Platform for BTech Students',
    template: '%s | Scholr',
  },
  description:
    'Free AI tool for BTech students. Get research papers, study notes, and doubt solving in 60 seconds.',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/favicon.ico',
  },
  openGraph: {
    title: 'Scholr — AI Academic Platform for BTech Students',
    description:
      'Free AI tool for BTech students. Get research papers, study notes, and doubt solving in 60 seconds.',
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
    title: 'Scholr — AI Academic Platform for BTech Students',
    description:
      'Free AI tool for BTech students. Get research papers, study notes, and doubt solving in 60 seconds.',
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

const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const shell = (
    <html lang="en">
      <body className="antialiased">
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  )

  if (clerkKey) {
    return <ClerkProvider>{shell}</ClerkProvider>
  }

  return shell
}
