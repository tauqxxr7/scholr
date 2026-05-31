export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse space-y-3 rounded-xl border bg-white p-5">
      <div className="h-4 w-3/4 rounded bg-gray-200" />
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`h-3 rounded bg-gray-100 ${index === lines - 1 ? 'w-2/3' : 'w-full'}`}
        />
      ))}
    </div>
  )
}
