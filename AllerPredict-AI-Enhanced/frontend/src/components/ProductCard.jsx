/**
 * Product Card Component
 */
import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

const ProductCard = ({ product, onAnalyze }) => {
  const getRiskColor = (allergens) => {
    if (!allergens || allergens.length === 0) return 'green';
    if (allergens.length <= 2) return 'yellow';
    return 'red';
  };

  const riskColor = getRiskColor(product.allergens);
  const colorClasses = {
    green: 'bg-green-50 border-green-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    red: 'bg-red-50 border-red-200',
  };

  return (
    <div className={`border-2 rounded-lg p-4 ${colorClasses[riskColor]} transition-all hover:shadow-lg`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-bold text-gray-800">{product.name}</h3>
          <p className="text-sm text-gray-600">{product.brand}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-gray-200 px-2 py-1 rounded">{product.category}</span>
        </div>
      </div>

      <div className="mb-3">
        <p className="text-sm text-gray-700 line-clamp-2">{product.description}</p>
      </div>

      <div className="space-y-2 mb-3">
        <div className="flex items-center gap-2">
          {product.allergens && product.allergens.length > 0 ? (
            <>
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-medium">Allergens:</span>
              <span className="text-sm text-gray-700">{product.allergens.join(', ')}</span>
            </>
          ) : (
            <>
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-green-600">No known allergens</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-medium">Ethical Score:</span>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: `${product.ethical_score * 10}%` }}
            />
          </div>
          <span className="text-sm font-bold">{product.ethical_score}/10</span>
        </div>
      </div>

      {product.certifications && product.certifications.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {product.certifications.map((cert, idx) => (
            <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              ✓ {cert}
            </span>
          ))}
        </div>
      )}

      <button
        onClick={() => onAnalyze(product)}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        Analyze with AI
      </button>
    </div>
  );
};

export default ProductCard;
