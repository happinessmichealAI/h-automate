import { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function SmartOperations() {
  const [problem, setProblem] = useState('')
  const [businessType, setBusinessType] = useState('mini-mart')
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (problem.trim().length < 10) {
      setError('Please provide a detailed description of your business challenge (at least 10 characters).')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/api/operations`, {
        problem_description: problem,
        business_type: businessType,
      })

      setAnalysis(response.data)
    } catch (err) {
      setError(err.response?.data?.message || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center mb-4">Smart Operations</h1>
        <p className="text-xl text-gray-600 text-center mb-12">
          Describe a business challenge and get practical solutions
        </p>

        {/* Input Section */}
        <div className="bg-white rounded-2xl p-8 shadow-lg mb-8">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Type
            </label>
            <select
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="mini-mart">Mini-Mart</option>
              <option value="pharmacy">Pharmacy</option>
              <option value="pos-agent">POS Agent</option>
              <option value="restaurant">Restaurant</option>
              <option value="fashion-store">Fashion Store</option>
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Describe Your Challenge
            </label>
            <textarea
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="e.g. Customers buy once but rarely return"
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
            />
            <p className="text-sm text-gray-500 mt-2">
              {problem.length} characters (minimum 10)
            </p>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || problem.trim().length < 10}
            className="w-full px-6 py-4 bg-primary text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze Problem'}
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-2xl p-8 shadow-lg">
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">Understanding your business challenge...</h3>
              <p className="text-gray-600 text-center">
                We're identifying possible causes and practical next steps.
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-red-800 mb-2">Analysis Error</h3>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Results */}
        {analysis && !loading && (
          <div className="space-y-6">
            {/* Situation Summary */}
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-primary">Situation Summary</h2>
              <p className="text-gray-700 leading-relaxed">{analysis.situation_summary}</p>
            </div>

            {/* Likely Causes */}
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-primary">Likely Causes</h2>
              <div className="space-y-4">
                {analysis.likely_causes && analysis.likely_causes.map((cause, idx) => (
                  <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-gray-700">{cause}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Actions */}
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-primary">Recommended Actions</h2>
              <div className="space-y-4">
                {analysis.recommended_actions && analysis.recommended_actions.map((action, idx) => (
                  <div key={idx} className="p-6 border-2 border-gray-200 rounded-lg hover:border-primary transition">
                    <h3 className="font-semibold text-lg mb-2">{action.title || `Action ${idx + 1}`}</h3>
                    {action.difficulty && (
                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-3 ${
                        action.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                        action.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {action.difficulty}
                      </span>
                    )}
                    {action.why && <p className="text-gray-700 mb-2"><strong>Why it matters:</strong> {action.why}</p>}
                    {action.how && <p className="text-gray-700"><strong>How to do it:</strong> {action.how}</p>}
                  </div>
                ))}
              </div>
            </div>

            {/* Workflow */}
            {analysis.workflow && analysis.workflow.length > 0 && (
              <div className="bg-white rounded-2xl p-8 shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-primary">Suggested Workflow</h2>
                <div className="space-y-4">
                  {analysis.workflow.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold">
                        {idx + 1}
                      </div>
                      <p className="text-gray-700 pt-1">{step}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Expected Outcome */}
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-8">
              <h2 className="text-2xl font-bold mb-4 text-primary">Expected Business Outcome</h2>
              <p className="text-gray-700 leading-relaxed">{analysis.expected_outcome}</p>
            </div>

            {/* Download Button */}
            <div className="text-center">
              <button className="px-8 py-4 bg-primary text-white rounded-lg font-semibold hover:bg-blue-700 transition shadow-lg">
                Download Action Report
              </button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !analysis && !error && (
          <div className="bg-white rounded-2xl p-12 shadow-lg text-center">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              Describe your challenge to get started
            </h3>
            <p className="text-gray-500">
              Your operational recommendations will appear here
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

// Made with Bob
