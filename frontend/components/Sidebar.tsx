'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BookOpen, BrainCircuit, FileText, Home, Menu, NotebookPen, Sparkles, X } from 'lucide-react'

import AccountPanel from '@/components/auth/account-panel'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/research', label: 'Research', icon: BookOpen },
  { href: '/notes', label: 'Notes', icon: NotebookPen },
  { href: '/doubt', label: 'Doubt', icon: BrainCircuit },
  { href: '/documents', label: 'Documents', icon: FileText },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY)

  const sidebarContent = (
    <div className="flex h-full flex-col gap-5 px-4 py-5 sm:px-6 lg:px-6 lg:py-6">
      <div className="flex items-start justify-between gap-4 lg:block">
        <Link href="/" className="block">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Scholr</p>
          <h1 className="mt-2 text-xl font-semibold tracking-tight text-slate-950 sm:text-2xl">
            Core workspace
          </h1>
        </Link>
        <div className="inline-flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800 shadow-sm">
          <Sparkles className="h-3.5 w-3.5" />
          Live MVP
        </div>
        <p className="hidden text-sm leading-6 text-slate-500 lg:mt-3 lg:block">
          Streamed academic workflows with identity-safe history, user-scoped documents, and multi-provider resilience.
        </p>
      </div>

      {clerkEnabled ? <AccountPanel /> : null}

      <nav className="flex gap-2 overflow-x-auto pb-1 lg:flex-1 lg:flex-col lg:overflow-visible lg:pb-0">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                'flex min-h-12 shrink-0 items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition lg:shrink',
                active
                  ? 'bg-slate-950 text-white shadow-sm'
                  : 'border border-slate-200 text-slate-600 hover:bg-slate-100 hover:text-slate-950 lg:border-transparent',
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="rounded-[1.5rem] border border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.9),rgba(255,255,255,0.98))] p-4 lg:hidden">
        <p className="text-sm font-medium text-slate-900">Current milestone</p>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Responsive MVP with streaming AI, saved history, and cross-device polish.
        </p>
      </div>

      <div className="hidden rounded-[1.75rem] border border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.9),rgba(255,255,255,0.98))] p-5 lg:block">
        <p className="text-sm font-medium text-slate-900">Current milestone</p>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Responsive MVP with streaming AI, saved history, and cross-device polish.
        </p>
      </div>
    </div>
  )

  return (
    <>
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/92 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <Link href="/" className="min-w-0">
            <p className="text-[11px] uppercase tracking-[0.35em] text-slate-400">Scholr</p>
            <p className="mt-1 truncate text-base font-semibold text-slate-950">Core workspace</p>
          </Link>
          <button
            type="button"
            aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={mobileMenuOpen}
            onClick={() => setMobileMenuOpen((current) => !current)}
            className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:border-slate-300 hover:text-slate-950"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </header>

      {mobileMenuOpen ? (
        <div className="fixed inset-0 z-40 flex bg-slate-950/30 backdrop-blur-[2px] lg:hidden">
          <div className="h-full w-full max-w-[20rem] bg-white shadow-2xl">{sidebarContent}</div>
          <button
            type="button"
            aria-label="Close navigation overlay"
            onClick={() => setMobileMenuOpen(false)}
            className="flex-1"
          />
        </div>
      ) : null}

      <aside className="hidden border-r border-slate-200 bg-white/90 backdrop-blur lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-80 lg:flex-col">
        {sidebarContent}
      </aside>
    </>
  )
}
