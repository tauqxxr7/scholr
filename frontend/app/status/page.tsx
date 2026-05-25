'use client'

import { useEffect, useState } from 'react'

type StatusResponse = {
  status: string
  services: Record<string, string>
  queries_last_hour: number
  uptime_note: string
  checked_at: string
}

export default function StatusPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null)

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, '')
    if (!apiUrl) {
      return
    }

    const loadStatus = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/status`, { cache: 'no-store' })
        if (response.ok) {
          setStatus(await response.json())
        }
      } catch {
        setStatus(null)
      }
    }

    void loadStatus()
    const timer = window.setInterval(loadStatus, 30000)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6">
      <section className="mx-auto max-w-3xl rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
        {!status ? (
          <div className="flex items-center gap-3 text-slate-600">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
            Checking status...
          </div>
        ) : (
          <div>
            <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full bg-emerald-500" />
              <h1 className="text-3xl font-semibold tracking-tight text-slate-950">
                All systems operational
              </h1>
            </div>
            <p className="mt-3 text-sm text-slate-500">
              Last checked {new Date(status.checked_at).toLocaleString()}
            </p>

            <div className="mt-8 grid gap-3">
              {Object.entries(status.services).map(([service, state]) => (
                <div
                  key={service}
                  className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                    <span className="capitalize text-slate-900">{service.replace('_', ' ')}</span>
                  </div>
                  <span className="text-sm text-emerald-700">{state}</span>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-sm text-slate-500">Queries in last hour</p>
              <p className="mt-1 text-2xl font-semibold text-slate-950">{status.queries_last_hour}</p>
            </div>

            <p className="mt-6 rounded-2xl bg-amber-50 p-4 text-sm leading-6 text-amber-800">
              {status.uptime_note}
            </p>
          </div>
        )}
      </section>
    </main>
  )
}
