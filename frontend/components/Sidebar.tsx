'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BookOpen, BrainCircuit, Home, NotebookPen } from 'lucide-react'

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
    <aside className="flex h-screen w-72 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-6 py-6">
        <Link href="/" className="block">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Scholr</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
            Core workspace
          </h1>
        </Link>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Ship the wedge first, then layer on auth, monetization, and deploy polish.
        </p>
      </div>

      <nav className="flex-1 space-y-2 px-4 py-5">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition',
                active
                  ? 'bg-slate-950 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950',
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-slate-200 px-6 py-5">
        <p className="text-sm font-medium text-slate-900">Current milestone</p>
        <p className="mt-1 text-sm leading-6 text-slate-500">
          Stable local MVP with streaming AI and saved history.
        </p>
      </div>
    </aside>
  )
}
