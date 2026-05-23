import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import BusinessInsights from './pages/BusinessInsights'
import SmartOperations from './pages/SmartOperations'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        {/* Navigation */}
        <nav className="bg-white border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-8">
                <a href="/" className="text-2xl font-bold text-primary">
                  H-Automate
                </a>
                <div className="hidden md:flex space-x-6">
                  <a 
                    href="/insights" 
                    className="text-gray-600 hover:text-primary transition"
                  >
                    Business Insights
                  </a>
                  <a 
                    href="/operations" 
                    className="text-gray-600 hover:text-primary transition"
                  >
                    Smart Operations
                  </a>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/insights" element={<BusinessInsights />} />
          <Route path="/operations" element={<SmartOperations />} />
        </Routes>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-20">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center text-gray-600 text-sm">
              <p>© 2026 H-Automate. Built for Nigerian SMEs with ❤️</p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App

// Made with Bob
