import { useState, useEffect } from 'react';
import { Search, ShoppingCart, Loader } from 'lucide-react';
import { analyzeProduct, getProducts } from './services/api';

function App() {
  const [step, setStep] = useState(1); // 1: إدخال حساسية، 2: التسوق
  const [userAllergies, setUserAllergies] = useState([]);
  const [allergyInput, setAllergyInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // تحميل المنتجات
  useEffect(() => {
    loadProducts();
  }, []);

  // فلترة المنتجات عند البحث
  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = products.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.brand.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredProducts(filtered);
    } else {
      setFilteredProducts(products);
    }
  }, [searchQuery, products]);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data.products || []);
      setFilteredProducts(data.products || []);
    } catch (error) {
      console.error('Error loading products:', error);
    }
  };

  // إضافة حساسية
  const addAllergy = () => {
    if (allergyInput.trim() && !userAllergies.includes(allergyInput.trim())) {
      setUserAllergies([...userAllergies, allergyInput.trim()]);
      setAllergyInput('');
    }
  };

  // حذف حساسية
  const removeAllergy = (allergy) => {
    setUserAllergies(userAllergies.filter(a => a !== allergy));
  };

  // بدء التسوق
  const startShopping = () => {
    if (userAllergies.length > 0) {
      setStep(2);
    }
  };

  // تحليل منتج
  const checkProduct = async (product) => {
    setLoading(true);
    setResult(null);

    try {
      const response = await analyzeProduct({
        query: product.name,
        user_allergies: userAllergies,
        detailed_analysis: false
      });

      // تحديد إذا كان المنتج آمن
      const productAllergens = product.allergens || [];
      const hasAllergen = productAllergens.some(allergen =>
        userAllergies.some(userAllergy =>
          allergen.toLowerCase().includes(userAllergy.toLowerCase()) ||
          userAllergy.toLowerCase().includes(allergen.toLowerCase())
        )
      );

      // استخراج رد مختصر من التحليل
      const analysis = response.analysis || '';
      const firstSentence = analysis.split('.')[0] + '.';

      setResult({
        isSafe: !hasAllergen,
        productName: product.name,
        reason: firstSentence,
        alternatives: response.alternatives?.slice(0, 3) || []
      });
    } catch (error) {
      console.error('Error analyzing product:', error);
      setResult({
        isSafe: false,
        productName: product.name,
        reason: 'حدث خطأ في التحليل. يرجى المحاولة مرة أخرى.',
        alternatives: []
      });
    } finally {
      setLoading(false);
    }
  };

  // الخطوة 1: إدخال الحساسية
  if (step === 1) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 p-4 flex items-center justify-center">
        <div className="max-w-md w-full">
          {/* Header */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 mb-6 text-center">
            <div className="text-6xl mb-4">🛒</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">AllerPredict</h1>
            <p className="text-gray-600">مساعدك الذكي للتسوق الآمن</p>
          </div>

          {/* Allergy Input Card */}
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
              <span>⚠️</span>
              <span>ما هي حساسيتك؟</span>
            </h2>
            <p className="text-gray-600 mb-6 text-sm">
              أدخل المواد التي تسبب لك حساسية لنساعدك في اختيار المنتجات المناسبة
            </p>

            {/* Input */}
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={allergyInput}
                onChange={(e) => setAllergyInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addAllergy()}
                placeholder="مثال: الفول السوداني، الحليب..."
                className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none text-right"
              />
              <button
                onClick={addAllergy}
                className="px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition"
              >
                إضافة
              </button>
            </div>

            {/* Allergies List */}
            {userAllergies.length > 0 && (
              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-2">حساسيتك:</p>
                <div className="flex flex-wrap gap-2">
                  {userAllergies.map((allergy, index) => (
                    <div
                      key={index}
                      className="bg-red-100 text-red-700 px-4 py-2 rounded-full flex items-center gap-2 font-semibold"
                    >
                      <span>{allergy}</span>
                      <button
                        onClick={() => removeAllergy(allergy)}
                        className="hover:text-red-900"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Start Button */}
            <button
              onClick={startShopping}
              disabled={userAllergies.length === 0}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-bold text-lg hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ابدأ التسوق الآن 🛍️
            </button>
          </div>
        </div>
      </div>
    );
  }

  // الخطوة 2: التسوق
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <ShoppingCart size={32} />
              <div>
                <h1 className="text-2xl font-bold">AllerPredict</h1>
                <p className="text-sm opacity-90">اختر منتجك بأمان</p>
              </div>
            </div>
            <button
              onClick={() => setStep(1)}
              className="text-sm bg-white/20 px-4 py-2 rounded-lg hover:bg-white/30 transition"
            >
              تعديل الحساسية
            </button>
          </div>

          {/* Allergies Display */}
          <div className="flex flex-wrap gap-2">
            {userAllergies.map((allergy, index) => (
              <div key={index} className="bg-white/20 px-3 py-1 rounded-full text-sm">
                ⚠️ {allergy}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="ابحث عن منتج أو امسح الباركود..."
              className="w-full pr-12 pl-4 py-4 bg-white border-2 border-gray-300 rounded-2xl focus:border-purple-500 focus:outline-none text-right text-lg"
            />
          </div>
        </div>

        {/* Products Grid */}
        {!result && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {filteredProducts.map((product) => (
              <button
                key={product.id}
                onClick={() => checkProduct(product)}
                disabled={loading}
                className="bg-white p-6 rounded-2xl shadow hover:shadow-lg transition text-right disabled:opacity-50"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-2">{product.name}</h3>
                <p className="text-gray-600 text-sm mb-3">{product.brand}</p>
                <div className="flex flex-wrap gap-2">
                  {product.allergens?.map((allergen, idx) => (
                    <span key={idx} className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">
                      {allergen}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <Loader className="animate-spin mx-auto mb-4 text-purple-600" size={48} />
            <p className="text-xl font-semibold text-gray-700">جاري التحليل...</p>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className={`rounded-3xl shadow-2xl p-8 text-center ${result.isSafe ? 'bg-gradient-to-br from-green-400 to-green-600' : 'bg-gradient-to-br from-red-400 to-red-600'} text-white`}>
            {/* Icon */}
            <div className="text-7xl mb-4">
              {result.isSafe ? '✅' : '❌'}
            </div>

            {/* Title */}
            <h2 className="text-3xl font-bold mb-2">
              {result.isSafe ? 'منتج آمن!' : 'تحذير!'}
            </h2>

            {/* Product Name */}
            <p className="text-xl mb-4 opacity-90">{result.productName}</p>

            {/* Reason */}
            <div className="bg-white/20 rounded-2xl p-6 mb-6">
              <p className="text-lg leading-relaxed">{result.reason}</p>
            </div>

            {/* Alternatives */}
            {!result.isSafe && result.alternatives.length > 0 && (
              <div className="bg-white/20 rounded-2xl p-6 mb-6">
                <h3 className="text-xl font-bold mb-4">بدائل صحية لك:</h3>
                <div className="space-y-3">
                  {result.alternatives.map((alt, idx) => (
                    <div key={idx} className="bg-white/30 rounded-xl p-4">
                      <p className="font-semibold text-lg">✨ {alt.name}</p>
                      <p className="text-sm opacity-90">{alt.brand}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => setResult(null)}
                className="flex-1 py-4 bg-white text-purple-600 rounded-xl font-bold hover:bg-gray-100 transition"
              >
                فحص منتج آخر
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;