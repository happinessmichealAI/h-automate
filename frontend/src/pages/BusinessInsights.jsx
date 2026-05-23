import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import axios from 'axios'
import HealthSnapshot from '../components/HealthSnapshot'
import Charts from '../components/Charts'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function BusinessInsights() {
  const location = useLocation()
  const [loading, setLoading] = useState(false)
  const [diagnosis, setDiagnosis] = useState(null)
  const [error, setError] = useState(null)
  const [businessType, setBusinessType] = useState('mini-mart')

  // Check if we came from sample data selection
  useEffect(() => {
    if (location.state?.sampleType) {
      handleSampleAnalysis(location.state.sampleType)
    }
  }, [location.state])

  const handleSampleAnalysis = async (sampleType) => {
    setLoading(true)
    setError(null)
    
    try {
      const formData = new FormData()
      formData.append('business_type', sampleType)
      formData.append('sample_type', sampleType)

      const response = await axios.post(`${API_URL}/api/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setDiagnosis(response.data)
      setBusinessType(sampleType)
    } catch (err) {
      setError(err.response?.data?.message || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('business_type', businessType)

      const response = await axios.post(`${API_URL}/api/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setDiagnosis(response.data)
    } catch (err) {
      setError(err.response?.data?.message || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!diagnosis) return

    try {
      const formData = new FormData()
      formData.append('diagnosis', diagnosis.diagnosis)
      formData.append('metrics', JSON.stringify(diagnosis.metrics))
      formData.append('business_type', diagnosis.business_type)
      formData.append('missing_fields', JSON.stringify(diagnosis.missing_fields || []))
      formData.append('warnings', JSON.stringify(diagnosis.warnings || []))

      const response = await axios.post(`${API_URL}/api/download-report`, formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/plain' }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `h-automate-report-${diagnosis.business_type}-${new Date().toISOString().split('T')[0]}.txt`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('PDF download failed:', err)
      alert('Failed to download report. Please try again.')
    }
  }

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-12">Business Insights</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel: File Upload */}
          <div className="bg-white rounded-2xl p-8 shadow-lg">
            <h2 className="text-2xl font-semibold mb-6">Upload Your Sales Data</h2>
            
            {/* Business Type Selector */}
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

            {/* File Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-primary transition">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0])}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <svg className="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-lg mb-2">Drag and drop your sales file here</p>
                <p className="text-sm text-gray-500 mb-4">or</p>
                <span className="px-6 py-2 bg-primary text-white rounded-lg inline-block">
                  Choose File
                </span>
                <p className="text-xs text-gray-400 mt-4">
                  Accepted formats: CSV, Excel (.xlsx)
                </p>
              </label>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => handleSampleAnalysis(businessType)}
                className="text-primary hover:underline"
              >
                or try sample data
              </button>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-1">
            {loading && <LoadingState type="analysis" duration={15} />}

            {error && (
              <ErrorState
                type={error.includes('format') ? 'unreadable_file' :
                      error.includes('missing') ? 'messy_data' :
                      error.includes('unavailable') ? 'ai_unavailable' : 'wrong_type'}
                message={error}
                onRetry={() => setError(null)}
              />
            )}

            {!loading && !diagnosis && !error && (
              <ErrorState
                type="empty_state"
                onViewSample={() => handleSampleAnalysis(businessType)}
              />
            )}
          </div>
        </div>

        {/* Full-width Results Section */}
        {diagnosis && !loading && (
          <div className="mt-12 space-y-8">
            {/* Health Snapshot */}
            <HealthSnapshot metrics={diagnosis.diagnosis} />

            {/* Key Insights Section */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">AI Diagnosis</h2>
              <div className="prose max-w-none">
                <pre className="text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {diagnosis.diagnosis}
                </pre>
              </div>
            </div>

            {/* Charts */}
            {diagnosis.metrics && <Charts metrics={diagnosis.metrics} />}

            {/* Data Quality Warnings */}
            {diagnosis.warnings && diagnosis.warnings.length > 0 && (
              <div className="bg-amber-50 border-2 border-amber-200 rounded-2xl p-6">
                <h3 className="font-semibold text-amber-900 mb-3 flex items-center gap-2">
                  <span>⚠️</span>
                  Data Quality Notes
                </h3>
                <ul className="text-sm text-amber-800 space-y-2">
                  {diagnosis.warnings.map((warning, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-600">•</span>
                      <span>{warning}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Download Button */}
            <div className="flex justify-center">
              <button
                onClick={() => handleDownloadReport()}
                className="px-8 py-4 bg-primary text-white rounded-xl font-semibold text-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                📄 Download Business Report
              </button>
            </div>

            {/* Gentle Prompt for Own Data */}
            {diagnosis.business_type && location.state?.sampleType && (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-6 text-center">
                <p className="text-blue-900 font-medium mb-3">
                  Want insights for your own business?
                </p>
                <button
                  onClick={() => {
                    setDiagnosis(null)
                    window.scrollTo({ top: 0, behavior: 'smooth' })
                  }}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Upload Your File
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Made with Bob
