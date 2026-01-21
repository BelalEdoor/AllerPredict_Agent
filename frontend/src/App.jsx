import React, { useState, useRef, useEffect } from 'react'

export default function App() {
  const [messages, setMessages] = useState([])
  const [products, setProducts] = useState([])
  const [filteredProducts, setFilteredProducts] = useState([])
  const [input, setInput] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [useAgenticMode, setUseAgenticMode] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const chatEndRef = useRef(null)

  useEffect(() => { scrollToBottom() }, [messages])

  useEffect(() => {
    const endpoint = useAgenticMode ? "/api/v2/products" : "/products"
    
    fetch(`http://localhost:8000${endpoint}`)
      .then(res => res.json())
      .then(data => {
        const productList = data.products || data
        setProducts(productList)
        setFilteredProducts(productList)
      })
      .catch(err => {
        console.error("Error loading products:", err)
        const fallback = [
          { name: 'Nutella Hazelnut Spread', brand: 'Ferrero', category: 'Spreads' },
          { name: 'Coca-Cola Classic', brand: 'Coca-Cola', category: 'Beverages' },
          { name: 'Lay\'s Potato Chips', brand: 'PepsiCo', category: 'Snacks' },
          { name: 'Oreo Cookies', brand: 'Mondelez', category: 'Cookies' },
          { name: 'Kind Dark Chocolate', brand: 'Kind LLC', category: 'Bars' }
        ]
        setProducts(fallback)
        setFilteredProducts(fallback)
      })
  }, [useAgenticMode])

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    const filtered = products.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase())
    )
    setFilteredProducts(filtered)
  }, [search, products])

  const analyzeProduct = async (productName) => {
    const userMessage = { type: 'user', text: productName }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const endpoint = useAgenticMode 
        ? 'http://localhost:8000/api/v2/analyze'
        : 'http://localhost:8000/analyze_product'

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(
          useAgenticMode 
            ? { product_name: productName, user_context: "" }
            : { product_name: productName }
        )
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Backend response:', data)

      if (useAgenticMode) {
        // ✅ عرض البيانات حتى لو success: false
        if (data.analysis || data.recommendations || data.error) {
          const botMessage = {
            type: 'bot-agentic',
            data: {
              analysis: data.analysis || data.error || 'No analysis available',
              recommendations: data.recommendations || '',
              full_report: data.full_report || '',
              agents_used: data.agents_used || ['AI Agent']
            }
          }
          setMessages(prev => [...prev, botMessage])
        } else {
          setMessages(prev => [...prev, {
            type: 'bot-error',
            text: 'No response from AI. Please try again.'
          }])
        }
      } else {
        const botMessage = {
          type: 'bot-legacy',
          data: {
            detected_allergens: data.detected_allergens || [],
            risk_level: data.risk_level || 'UNKNOWN',
            ethical_score: data.ethical_score || 0,
            recommendations: data.recommendations || []
          }
        }
        setMessages(prev => [...prev, botMessage])
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        type: 'bot-error',
        text: `Error: ${error.message}`
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleSend = () => {
    if (!input.trim()) return
    analyzeProduct(input)
    setInput('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-gray-200 z-50 shadow-sm">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  AllerPredict AI
                </h1>
                <p className="text-xs text-gray-500">Professional Food Analysis</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setUseAgenticMode(!useAgenticMode)}
              className={`px-4 py-2 rounded-xl font-medium text-sm transition-all ${
                useAgenticMode 
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {useAgenticMode ? '🤖 AI Agents' : '📊 Basic Mode'}
            </button>
            
            <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-xl">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-gray-700">System Active</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex pt-16">
        <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed lg:relative lg:translate-x-0 left-0 top-16 w-80 h-[calc(100vh-4rem)] bg-white border-r border-gray-200 transition-transform duration-300 z-40 flex flex-col shadow-xl lg:shadow-none`}>
          <div className="p-6 border-b border-gray-200 bg-gradient-to-br from-gray-50 to-white">
            <h2 className="text-lg font-bold text-gray-800 mb-3">Product Database</h2>
            <div className="relative">
              <input
                type="text"
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm transition"
              />
              <svg className="w-5 h-5 text-gray-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {filteredProducts.length === 0 ? (
              <div className="text-center py-8">
                <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-500 text-sm">No products found</p>
              </div>
            ) : (
              filteredProducts.map((p, i) => (
                <div
                  key={i}
                  onClick={() => analyzeProduct(p.name)}
                  className="group cursor-pointer p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl hover:from-blue-50 hover:to-purple-50 border border-gray-200 hover:border-blue-300 transition-all hover:shadow-md"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800 group-hover:text-blue-600 transition mb-1">{p.name}</p>
                      <p className="text-xs text-gray-500">{p.brand}</p>
                    </div>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-lg font-medium">
                      {p.category}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        <div className="flex-1 flex flex-col h-[calc(100vh-4rem)]">
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center max-w-md">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-3">Welcome to AllerPredict AI</h3>
                  <p className="text-gray-600 mb-6">Select a product to get instant AI-powered allergen and safety analysis.</p>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="p-3 bg-blue-50 rounded-xl">
                      <div className="text-2xl mb-2">🔍</div>
                      <div className="font-medium text-gray-800">Allergen Detection</div>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-xl">
                      <div className="text-2xl mb-2">⚡</div>
                      <div className="font-medium text-gray-800">Risk Assessment</div>
                    </div>
                    <div className="p-3 bg-green-50 rounded-xl">
                      <div className="text-2xl mb-2">🌱</div>
                      <div className="font-medium text-gray-800">Ethical Scoring</div>
                    </div>
                    <div className="p-3 bg-orange-50 rounded-xl">
                      <div className="text-2xl mb-2">💡</div>
                      <div className="font-medium text-gray-800">Recommendations</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg, i) => {
                if (msg.type === 'user') {
                  return (
                    <div key={i} className="flex justify-end">
                      <div className="max-w-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-lg">
                        <p className="font-medium">{msg.text}</p>
                      </div>
                    </div>
                  )
                } else if (msg.type === 'bot-agentic') {
                  return (
                    <div key={i} className="flex justify-start">
                      <div className="max-w-3xl">
                        <div className="bg-white rounded-2xl rounded-tl-sm shadow-lg border border-gray-200 overflow-hidden">
                          <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-5 py-3 border-b border-gray-200">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                </svg>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-800">AI Analysis Complete</p>
                                {msg.data.agents_used && (
                                  <p className="text-xs text-gray-500">{msg.data.agents_used.join(' • ')}</p>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <div className="p-5 space-y-4">
                            {msg.data.analysis && (
                              <div>
                                <div className="flex items-center gap-2 mb-2">
                                  <div className="w-6 h-6 bg-blue-100 rounded-lg flex items-center justify-center">
                                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                    </svg>
                                  </div>
                                  <h4 className="font-semibold text-gray-800">Analysis Report</h4>
                                </div>
                                <div className="bg-gray-50 rounded-xl p-4 whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
                                  {msg.data.analysis}
                                </div>
                              </div>
                            )}
                            
                            {msg.data.recommendations && (
                              <div>
                                <div className="flex items-center gap-2 mb-2">
                                  <div className="w-6 h-6 bg-green-100 rounded-lg flex items-center justify-center">
                                    <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                  </div>
                                  <h4 className="font-semibold text-gray-800">Recommendations</h4>
                                </div>
                                <div className="bg-green-50 rounded-xl p-4 whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
                                  {msg.data.recommendations}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                } else if (msg.type === 'bot-legacy') {
                  return (
                    <div key={i} className="flex justify-start">
                      <div className="max-w-2xl bg-white rounded-2xl rounded-tl-sm shadow-lg border border-gray-200 p-5">
                        <h4 className="font-semibold text-gray-800 mb-3">Analysis Result</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Allergens:</span>
                            <span className="font-medium text-red-600">{msg.data.detected_allergens?.join(', ') || 'None'}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Risk Level:</span>
                            <span className={`px-2 py-1 rounded-lg font-medium ${
                              msg.data.risk_level === 'HIGH' ? 'bg-red-100 text-red-700' :
                              msg.data.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>{msg.data.risk_level}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Ethical Score:</span>
                            <span className="font-medium">{msg.data.ethical_score}/100</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                } else if (msg.type === 'bot-error') {
                  return (
                    <div key={i} className="flex justify-start">
                      <div className="max-w-2xl bg-red-50 border border-red-200 rounded-2xl rounded-tl-sm shadow-lg p-5">
                        <div className="flex items-center gap-2 mb-2">
                          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <h4 className="font-semibold text-red-800">Error</h4>
                        </div>
                        <p className="text-sm text-red-700">{msg.text}</p>
                      </div>
                    </div>
                  )
                }
                return null
              })
            )}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl rounded-tl-sm shadow-lg border border-gray-200 px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                    <span className="text-sm text-gray-600">
                      {useAgenticMode ? 'AI analyzing product...' : 'Processing...'}
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={chatEndRef}></div>
          </div>

          <div className="border-t border-gray-200 bg-white p-4">
            <div className="max-w-4xl mx-auto flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type a product name..."
                className="flex-1 px-5 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition"
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}