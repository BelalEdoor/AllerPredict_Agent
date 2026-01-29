/**
 * Analysis Report Component
 */
import React from 'react';
import { AlertCircle, CheckCircle, TrendingUp, Heart, Download } from 'lucide-react';

const AnalysisReport = ({ report, onClose }) => {
  const downloadReport = () => {
    const content = JSON.stringify(report, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `allerpredict-${report.product.name.replace(/\s+/g, '-')}.json`;
    a.click();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-xl">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-1">{report.product.name}</h2>
              <p className="text-blue-100">{report.product.brand} • {report.product.category}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
            >
              ✕
            </button>
          </div>

          <div className="flex gap-4 mt-4">
            <div className="bg-white bg-opacity-20 rounded-lg px-4 py-2">
              <span className="text-sm">Allergens: </span>
              <span className="font-bold">{report.product.allergens?.length || 0}</span>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg px-4 py-2">
              <span className="text-sm">Ethical Score: </span>
              <span className="font-bold">{report.product.ethical_score}/10</span>
            </div>
            <button
              onClick={downloadReport}
              className="ml-auto bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download Report
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Allergen Alert */}
          {report.product.allergens && report.product.allergens.length > 0 && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-bold text-red-800 mb-1">Allergen Warning</h3>
                  <p className="text-red-700 text-sm">
                    This product contains: <strong>{report.product.allergens.join(', ')}</strong>
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Analysis Sections */}
          <div className="space-y-4">
            {report.analysis.symptom_analysis && (
              <AnalysisSection
                title="Symptom Analysis"
                icon={<Heart className="w-5 h-5" />}
                content={report.analysis.symptom_analysis}
                color="purple"
              />
            )}

            {report.analysis.allergen_prediction && (
              <AnalysisSection
                title="Allergen Prediction"
                icon={<AlertCircle className="w-5 h-5" />}
                content={report.analysis.allergen_prediction}
                color="orange"
              />
            )}

            {report.analysis.risk_assessment && (
              <AnalysisSection
                title="Risk Assessment"
                icon={<TrendingUp className="w-5 h-5" />}
                content={report.analysis.risk_assessment}
                color="red"
              />
            )}

            {report.analysis.medical_advice && (
              <AnalysisSection
                title="Medical Advice"
                icon={<CheckCircle className="w-5 h-5" />}
                content={report.analysis.medical_advice}
                color="green"
              />
            )}

            {typeof report.analysis === 'string' && (
              <AnalysisSection
                title="Product Analysis"
                icon={<CheckCircle className="w-5 h-5" />}
                content={report.analysis}
                color="blue"
              />
            )}
          </div>

          {/* Alternatives */}
          {report.alternatives && report.alternatives.length > 0 && (
            <div className="bg-green-50 rounded-lg p-6">
              <h3 className="text-lg font-bold text-green-800 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Safe Alternatives
              </h3>
              <div className="grid gap-3">
                {report.alternatives.map((alt, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-4 border border-green-200">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-gray-800">{alt.name}</h4>
                        <p className="text-sm text-gray-600">{alt.brand}</p>
                      </div>
                      <span className="bg-green-100 text-green-700 px-3 py-1 rounded text-sm font-bold">
                        {alt.ethical_score}/10
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">{alt.description}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {alt.allergens && alt.allergens.length > 0 ? (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                          Allergens: {alt.allergens.join(', ')}
                        </span>
                      ) : (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          ✓ No allergens
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const AnalysisSection = ({ title, icon, content, color }) => {
  const colorClasses = {
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
  };

  return (
    <div className={`border rounded-lg p-4 ${colorClasses[color]}`}>
      <h3 className="font-bold mb-2 flex items-center gap-2">
        {icon}
        {title}
      </h3>
      <div className="text-sm whitespace-pre-wrap">{content}</div>
    </div>
  );
};

export default AnalysisReport;
