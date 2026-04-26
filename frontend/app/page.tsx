'use client'

import { useState } from 'react'

interface Recommendation {
  restaurant_name: string
  cuisine: string
  rating: number
  estimated_cost: number
  explanation: string
}

interface ApiResponse {
  recommendations: Recommendation[]
  llm_provider_used: string
  fallback_applied: boolean
  filter_strategy: string
}

export default function Home() {
  const [formData, setFormData] = useState({
    location: '',
    budget: 'medium',
    cuisine: '',
    minRating: 4.0,
    additionalPreferences: '',
    topN: 5
  })
  const [loading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<ApiResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setRecommendations(null)

    try {
      const response = await fetch('http://localhost:8000/api/v1/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location: formData.location,
          budget: formData.budget,
          cuisine: formData.cuisine,
          min_rating: parseFloat(formData.minRating),
          additional_preferences: formData.additionalPreferences || null,
          top_n: parseInt(formData.topN)
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: ApiResponse = await response.json()
      setRecommendations(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Restaurant Recommender</h1>
          <p className="text-white/80">Find the perfect restaurant based on your preferences</p>
        </div>

        <div className="bg-white rounded-xl shadow-2xl p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="location" className="block text-sm font-semibold text-gray-700 mb-2">
                Location *
              </label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Bellandur, Indiranagar"
                required
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            <div>
              <label htmlFor="budget" className="block text-sm font-semibold text-gray-700 mb-2">
                Budget *
              </label>
              <select
                id="budget"
                name="budget"
                value={formData.budget}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="low">Low (Up to Rs.800)</option>
                <option value="medium">Medium (Rs.801 - Rs.2000)</option>
                <option value="high">High (Above Rs.2000)</option>
              </select>
            </div>

            <div>
              <label htmlFor="cuisine" className="block text-sm font-semibold text-gray-700 mb-2">
                Cuisine *
              </label>
              <input
                type="text"
                id="cuisine"
                name="cuisine"
                value={formData.cuisine}
                onChange={handleChange}
                placeholder="e.g., Italian, North Indian, Chinese"
                required
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            <div>
              <label htmlFor="minRating" className="block text-sm font-semibold text-gray-700 mb-2">
                Minimum Rating *
              </label>
              <input
                type="number"
                id="minRating"
                name="minRating"
                value={formData.minRating}
                onChange={handleChange}
                min="0"
                max="5"
                step="0.1"
                required
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            <div>
              <label htmlFor="additionalPreferences" className="block text-sm font-semibold text-gray-700 mb-2">
                Additional Preferences (Optional)
              </label>
              <input
                type="text"
                id="additionalPreferences"
                name="additionalPreferences"
                value={formData.additionalPreferences}
                onChange={handleChange}
                placeholder="e.g., family-friendly, outdoor seating"
                maxLength={500}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            <div>
              <label htmlFor="topN" className="block text-sm font-semibold text-gray-700 mb-2">
                Number of Recommendations *
              </label>
              <select
                id="topN"
                name="topN"
                value={formData.topN}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Finding Restaurants...' : 'Get Recommendations'}
            </button>
          </form>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-lg">
            <p className="text-red-700">Error: {error}</p>
          </div>
        )}

        {recommendations && (
          <div className="bg-white rounded-xl shadow-2xl p-8">
            <div className="mb-6 pb-6 border-b-2 border-gray-100">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Recommendations</h2>
              <div className="flex gap-2 text-sm text-gray-600">
                <span className="bg-gray-100 px-3 py-1 rounded-full">
                  Provider: {recommendations.llm_provider_used}
                </span>
                <span className="bg-gray-100 px-3 py-1 rounded-full">
                  Fallback: {recommendations.fallback_applied ? 'Yes' : 'No'}
                </span>
              </div>
            </div>

            <div className="space-y-4">
              {recommendations.recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="border-2 border-gray-100 rounded-lg p-6 hover:border-purple-300 transition-colors"
                >
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-bold text-gray-800">{rec.restaurant_name}</h3>
                    <div className="bg-gradient-to-r from-pink-500 to-rose-500 text-white px-4 py-2 rounded-full font-semibold">
                      ⭐ {rec.rating}
                    </div>
                  </div>
                  <div className="space-y-2 text-gray-600">
                    <p><strong>Cuisine:</strong> {rec.cuisine}</p>
                    <p><strong>Cost for Two:</strong> Rs.{rec.estimated_cost.toFixed(0)}</p>
                    <p className="mt-4 p-4 bg-gray-50 rounded-lg border-l-4 border-purple-500 italic">
                      <strong>Why this?</strong> {rec.explanation}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
