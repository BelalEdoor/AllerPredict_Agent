/**
 * AllerPredict AI - Enhanced Frontend
 */
import React, { useState, useEffect } from 'react';
import { Search, Loader, AlertCircle, Sparkles, Brain } from 'lucide-react';
import { allerPredictAPI } from './services/api';
import ProductCard from './components/ProductCard';
import AnalysisReport from './components/AnalysisReport';

function App() {
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [currentReport, setCurrentReport] = useState(null);
  const [detailedMode, setDetailedMode] = useState(false);
  const [userAllergies, setUserAllergies] = useState([]);
  const [allergyInput, setAllergyInput] = useState('');

  // Load products on mount
  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await allerPredictAPI.getProducts();
      setProducts(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load products. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (product) => {
    setAnalyzing(true);
    setError(null);
    try {
      const result = await allerPredictAPI.analyzeProduct(
        product.name,
        userAllergies.length > 0 ? userAllergies : [],
        detailedMode
      );
      setCurrentReport(result);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setError('Product analysis failed: Product not found.');
      } else if (err.response?.status === 500) {
        setError('Analysis failed due to internal server error.');
      } else {
        setError('Unexpected error occurred during analysis.');
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const addAllergy = () => {
    const allergy = allergyInput.trim().toLowerCase();
    if (allergy && !userAllergies.includes(allergy)) {
      setUserAllergies([...userAllergies, allergy]);
      setAllergyInput('');
    }
  };

  const removeAllergy = (allergy) => {
    setUserAllergies(userAllergies.filter(a => a !== allergy));
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8" />
            <div>
              <h1 className="text-3xl font-bold">AllerPredict AI</h1>
              <p className="text-blue-100 text-sm">Intelligent Product Analysis System</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm bg-white bg-opacity-20 px-3 py-1 rounded">v2.0</span>
            <Brain className="w-6 h-6" />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Control Panel */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          {/* Search */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Products</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name, brand, or category..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* User Allergies */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Your Allergies (Optional)</label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={allergyInput}
                onChange={(e) => setAllergyInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addAllergy()}
                placeholder="e.g., peanuts, dairy, gluten..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={addAllergy}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add
              </button>
            </div>
            {userAllergies.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {userAllergies.map((allergy, idx) => (
                  <span key={idx} className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                    {allergy}
                    <button onClick={() => removeAllergy(allergy)} className="hover:text-red-900">✕</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Analysis Mode */}
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={detailedMode}
                onChange={(e) => setDetailedMode(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Detailed Analysis (Multi-Agent AI)</span>
            </label>
            <span className="text-xs text-gray-500">
              {detailedMode ? '🔬 Deep analysis with 4 specialized agents' : '⚡ Quick analysis'}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-800 font-medium">Error</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Loading Products */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <Loader className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600">Loading products...</span>
          </div>
        )}

        {/* Products Grid */}
        {!loading && filteredProducts.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} onAnalyze={handleAnalyze} />
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && filteredProducts.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No products found matching your search.
          </div>
        )}
      </main>

      {/* Analysis Modal */}
      {analyzing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md text-center">
            <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-700 font-medium">
              {detailedMode ? 'Running multi-agent analysis...' : 'Analyzing product...'}
            </p>
            {detailedMode && <p className="text-gray-500 text-sm mt-2">This may take 15-30 seconds</p>}
          </div>
        </div>
      )}

      {/* Report Modal */}
      {currentReport && (
        <AnalysisReport report={currentReport} onClose={() => setCurrentReport(null)} />
      )}

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12 text-center">
        <p className="text-sm">AllerPredict AI v2.0 • Powered by CrewAI, RAG & MCP</p>
        <p className="text-xs text-gray-400 mt-1">Multi-Agent System with Local AI Processing</p>
      </footer>
    </div>
  );
}

export default App;
