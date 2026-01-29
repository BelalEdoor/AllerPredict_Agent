/**
 * API Service for AllerPredict AI
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const allerPredictAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get all products
  getProducts: async () => {
    const response = await api.get('/products');
    return response.data.products;
  },

  // Analyze product
  analyzeProduct: async (query, userAllergies = null, detailedAnalysis = false) => {
    const response = await api.post('/analyze', {
      query,
      user_allergies: userAllergies,
      detailed_analysis: detailedAnalysis,
    });
    return response.data;
  },

  // Find alternatives
  findAlternatives: async (allergens, category = null) => {
    const response = await api.post('/alternatives', {
      allergens,
      category,
    });
    return response.data;
  },

  // Search products
  searchProducts: async (query, limit = 5) => {
    const response = await api.get(`/search/${encodeURIComponent(query)}`, {
      params: { limit },
    });
    return response.data;
  },

  // Get specific product
  getProduct: async (productId) => {
    const response = await api.get(`/product/${productId}`);
    return response.data;
  },
};

export default allerPredictAPI;
