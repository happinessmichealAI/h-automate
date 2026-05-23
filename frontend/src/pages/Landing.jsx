import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Store, Pill, CreditCard, UtensilsCrossed, Shirt } from 'lucide-react'

export default function Landing() {
  const navigate = useNavigate()
  const [showModal, setShowModal] = useState(false)

  const businessTypes = [
    {
      id: 'mini-mart',
      name: 'Mini-Mart',
      description: 'Understand stock and sales performance',
      icon: Store,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      id: 'pharmacy',
      name: 'Pharmacy',
      description: 'Reduce expiry and dead stock',
      icon: Pill,
      color: 'bg-green-50 text-green-600',
    },
    {
      id: 'pos-agent',
      name: 'POS Agent',
      description: 'Track transactions and manage float',
      icon: CreditCard,
      color: 'bg-purple-50 text-purple-600',
    },
    {
      id: 'restaurant',
      name: 'Restaurant',
      description: 'Analyze revenue and costs',
      icon: UtensilsCrossed,
      color: 'bg-orange-50 text-orange-600',
    },
    {
      id: 'fashion-store',
      name: 'Fashion Store',
      description: 'Track customer buying patterns',
      icon: Shirt,
      color: 'bg-pink-50 text-pink-600',
    },
  ]

  const handleSampleData = (businessType) => {
    navigate('/insights', { state: { sampleType: businessType } })
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Understand your business better with AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-12">
            Upload your sales file or describe a business problem and receive
            practical recommendations in minutes.
          </p>

          {/* Primary CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => setShowModal(true)}
              className="w-full sm:w-auto px-8 py-4 bg-primary text-white rounded-xl text-lg font-semibold hover:bg-blue-700 transition shadow-lg"
            >
              Try Sample Business Data
            </button>
            <button
              onClick={() => navigate('/insights')}
              className="w-full sm:w-auto px-8 py-4 border-2 border-primary text-primary rounded-xl text-lg font-semibold hover:bg-blue-50 transition"
            >
              Upload Your File
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Built for Nigerian SMEs
          </h2>
          <p className="text-xl text-gray-600 text-center mb-16 max-w-2xl mx-auto">
            Get AI-powered insights tailored to your business type
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-primary transition">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Business Health Snapshot</h3>
              <p className="text-gray-600">
                Get scored metrics on revenue stability, inventory health, and customer retention
              </p>
            </div>

            <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-primary transition">
              <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Actionable Insights</h3>
              <p className="text-gray-600">
                Receive specific recommendations you can implement immediately
              </p>
            </div>

            <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-primary transition">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Downloadable Reports</h3>
              <p className="text-gray-600">
                Get professional PDF reports you can share with partners
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Business Type Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl md:text-3xl font-bold">Choose Your Business Type</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {businessTypes.map((business) => {
                const Icon = business.icon
                return (
                  <button
                    key={business.id}
                    onClick={() => {
                      setShowModal(false)
                      handleSampleData(business.id)
                    }}
                    className="p-6 border-2 border-gray-200 rounded-xl hover:border-primary hover:shadow-lg transition text-left"
                  >
                    <div className={`w-12 h-12 ${business.color} rounded-lg flex items-center justify-center mb-4`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{business.name}</h3>
                    <p className="text-sm text-gray-600">{business.description}</p>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Made with Bob
