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

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Get all products
export const getProducts = async () => {
  const response = await api.get('/products');
  return response.data;
};

// Analyze product
export const analyzeProduct = async ({ query, user_allergies = null, detailed_analysis = false }) => {
  const response = await api.post('/analyze', {
    query,
    user_allergies,
    detailed_analysis,
  });
  return response.data;
};

// Find alternatives
export const findAlternatives = async (allergens, category = null) => {
  const response = await api.post('/alternatives', {
    allergens,
    category,
  });
  return response.data;
};

// Search products
export const searchProducts = async (query, limit = 5) => {
  const response = await api.get(`/search/${encodeURIComponent(query)}`, {
    params: { limit },
  });
  return response.data;
};

// Get specific product
export const getProduct = async (productId) => {
  const response = await api.get(`/product/${productId}`);
  return response.data;
};

// Default export
const allerPredictAPI = {
  healthCheck,
  getProducts,
  analyzeProduct,
  findAlternatives,
  searchProducts,
  getProduct,
};

export default allerPredictAPI;