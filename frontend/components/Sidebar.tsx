'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BookOpen, BrainCircuit, Home, NotebookPen, Sparkles } from 'lucide-react'

import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/research', label: 'Research', icon: BookOpen },
  { href: '/notes', label: 'Notes', icon: NotebookPen },
  { href: '/doubt', label: 'Doubt', icon: BrainCircuit },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="border-b border-slate-200 bg-white/90 backdrop-blur lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-80 lg:flex-col lg:border-b-0 lg:border-r">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 px-4 py-5 sm:px-6 lg:max-w-none lg:px-6 lg:py-6">
        <div className="flex items-start justify-between gap-4 lg:block">
          <Link href="/" className="block">
            <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Scholr</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
              Core workspace
            </h1>
          </Link>
          <div className="inline-flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800 shadow-sm">
            <Sparkles className="h-3.5 w-3.5" />
            Live MVP
          </div>
          <p className="hidden text-sm leading-6 text-slate-500 lg:mt-3 lg:block">
            Ship the wedge first, then layer on auth, monetization, and deploy polish.
          </p>
        </div>

        <nav className="flex gap-2 overflow-x-auto pb-1 lg:flex-1 lg:flex-col lg:overflow-visible lg:pb-0">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = pathname === item.href

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex shrink-0 items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition lg:shrink',
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

        <div className="hidden rounded-[1.75rem] border border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.9),rgba(255,255,255,0.98))] p-5 lg:block">
          <p className="text-sm font-medium text-slate-900">Current milestone</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Stable local MVP with streaming AI, better UI polish, and saved history.
          </p>
        </div>
      </div>
    </aside>
  )
}
