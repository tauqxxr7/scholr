import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const base = 'https://scholr-coral.vercel.app'
  return [
    { url: base, lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    { url: `${base}/research`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/notes`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/doubt`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/changelog`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
    { url: `${base}/demo`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/feedback`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${base}/topics`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${base}/status`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.6 },
    { url: `${base}/documents`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
    { url: `${base}/dashboard`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.6 },
    { url: `${base}/privacy`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
    { url: `${base}/terms`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
  ]
}
