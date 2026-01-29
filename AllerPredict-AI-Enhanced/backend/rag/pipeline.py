"""RAG Pipeline for Product Analysis"""
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
import ollama

class RAGPipeline:
    def __init__(self, metadata_path: str = None):
        """Initialize RAG pipeline with embeddings model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.products = self._load_products(metadata_path)
        self.embeddings = self._create_embeddings()
        
    def _load_products(self, path: str) -> List[Dict]:
        """Load product metadata from JSON"""
        import os
        
        # If path is None or doesn't exist, try to find it
        if path is None or not os.path.exists(path):
            # Try multiple possible locations
            possible_paths = [
                "../data/metadata.json",
                "data/metadata.json",
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata.json"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "metadata.json"),
            ]
            
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    path = possible_path
                    print(f"✅ Found metadata.json at: {path}")
                    break
            else:
                raise FileNotFoundError(
                    f"Could not find metadata.json. Tried:\n" + 
                    "\n".join(f"  - {p}" for p in possible_paths) +
                    f"\n\nCurrent directory: {os.getcwd()}\n" +
                    "Make sure data/metadata.json exists in the project root!"
                )
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_embeddings(self) -> np.ndarray:
        """Create embeddings for all products"""
        texts = [
            f"{p['name']} {p['brand']} {' '.join(p['ingredients'])} {p['description']}"
            for p in self.products
        ]
        return self.model.encode(texts)
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for most similar products"""
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            product = self.products[idx].copy()
            product['similarity_score'] = float(similarities[idx])
            results.append(product)
        return results
    
    def analyze_with_llm(self, product: Dict, user_query: str) -> str:
        """Analyze product using Ollama LLM"""
        context = self._build_context(product)
        prompt = f"""You are a product safety analyst. Analyze this product:

{context}

User Question: {user_query}

Provide a detailed analysis covering:
1. Allergen identification
2. Risk level assessment (Low/Medium/High)
3. Health implications
4. Recommendations

Be concise and factual."""

        response = ollama.generate(
            model='llama3.2',
            prompt=prompt,
            options={'temperature': 0.3}
        )
        return response['response']
    
    def _build_context(self, product: Dict) -> str:
        """Build context string from product data"""
        return f"""Product: {product['name']} by {product['brand']}
Category: {product['category']}
Ingredients: {', '.join(product['ingredients'])}
Known Allergens: {', '.join(product['allergens']) if product['allergens'] else 'None'}
Description: {product['description']}
Ethical Score: {product['ethical_score']}/10
Company Info: {product['company_info']}
Certifications: {', '.join(product['certifications']) if product['certifications'] else 'None'}"""
    
    def find_alternatives(self, allergens: List[str], exclude_id: int) -> List[Dict]:
        """Find safe alternative products"""
        alternatives = []
        for product in self.products:
            if product['id'] != exclude_id:
                # Check if product is safe (no matching allergens)
                if not any(allergen in product['allergens'] for allergen in allergens):
                    alternatives.append(product)
        
        # Sort by ethical score
        alternatives.sort(key=lambda x: x['ethical_score'], reverse=True)
        return alternatives[:3]