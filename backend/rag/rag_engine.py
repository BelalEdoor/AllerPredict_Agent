"""
Updated RAG Engine - Refactored to work as a CrewAI tool
"""
import os
import json
from typing import List, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from crewai_tools import BaseTool


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for product analysis
    """
    
    def __init__(self, metadata_path: str = None):
        """
        Initialize RAG engine with embeddings model and product data
        
        Args:
            metadata_path: Path to product metadata JSON file
        """
        # Load embedding model
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load product metadata
        if metadata_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            metadata_path = os.path.join(base_dir, "data", "metadata.json")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.products = json.load(f)
        
        # Create embeddings for all products
        self.embeddings = []
        self.product_texts = []
        
        for product in self.products:
            text = self._create_product_text(product)
            self.product_texts.append(text)
            embedding = self.model.encode(text)
            self.embeddings.append(embedding)
        
        self.embeddings = np.array(self.embeddings)
        print(f"✅ Loaded {len(self.products)} products with embeddings")
    
    def _create_product_text(self, product: Dict[str, Any]) -> str:
        """
        Create searchable text representation of a product
        
        Args:
            product: Product dictionary
            
        Returns:
            str: Combined text representation
        """
        return f"""
        Product: {product.get('name', '')}
        Category: {product.get('category', '')}
        Brand: {product.get('brand', '')}
        Description: {product.get('description', '')}
        Ingredients: {product.get('ingredients', '')}
        Allergens: {product.get('allergen_warnings', '')}
        Ethical Notes: {product.get('ethical_notes', '')}
        Recommendations: {product.get('recommendations', '')}
        """.strip()
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search for relevant products using semantic similarity
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (similarity_score, product) tuples
        """
        # Encode query
        query_embedding = self.model.encode(query)
        
        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return results
        results = []
        for idx in top_indices:
            results.append((float(similarities[idx]), self.products[idx]))
        
        return results
    
    def analyze_product(self, product_name: str) -> Dict[str, Any]:
        """
        Analyze a product and return structured results
        
        Args:
            product_name: Name of the product to analyze
            
        Returns:
            Dict with analysis results
        """
        # Search for the product
        results = self.search(product_name, top_k=3)
        
        if not results or results[0][0] < 0.3:  # Low similarity threshold
            return {
                "found": False,
                "message": f"Product '{product_name}' not found in database",
                "detected_allergens": [],
                "risk_level": "unknown",
                "ethical_score": 0,
                "recommendations": []
            }
        
        # Get best match
        score, product = results[0]
        
        # Parse allergens
        allergens_str = product.get('allergen_warnings', '')
        allergens = [a.strip() for a in allergens_str.split(',') if a.strip()]
        
        # Calculate risk level based on allergen count
        if len(allergens) == 0:
            risk_level = "low"
        elif len(allergens) <= 2:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Calculate ethical score (inverse of how many concerns mentioned)
        ethical_notes = product.get('ethical_notes', '').lower()
        concern_keywords = ['criticism', 'controversy', 'concern', 'accused', 'poor', 'child labor']
        concerns_count = sum(1 for keyword in concern_keywords if keyword in ethical_notes)
        ethical_score = max(0, 100 - (concerns_count * 20))
        
        # Parse recommendations
        rec_str = product.get('recommendations', '')
        recommendations_list = [r.strip() for r in rec_str.split(',') if r.strip()]
        
        return {
            "found": True,
            "product_name": product.get('name'),
            "brand": product.get('brand'),
            "category": product.get('category'),
            "description": product.get('description'),
            "ingredients": product.get('ingredients'),
            "detected_allergens": allergens,
            "risk_level": risk_level,
            "ethical_score": ethical_score,
            "ethical_notes": product.get('ethical_notes'),
            "recommendations": recommendations_list,
            "similarity_score": score
        }


class RAGTool(BaseTool):
    """
    CrewAI tool wrapper for RAG engine
    """
    name: str = "Product Analysis Tool"
    description: str = "Analyzes food products for allergens, ingredients, and ethical concerns. Input should be a product name."
    
    # Define engine as a class attribute
    engine: Any = None
    products: List[Dict[str, Any]] = []
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        """Initialize the RAG engine"""
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'engine', RAGEngine())
        object.__setattr__(self, 'products', self.engine.products)
    
    def _run(self, product_name: str) -> str:
        """
        Run the tool
        
        Args:
            product_name: Product to analyze
            
        Returns:
            str: Formatted analysis results
        """
        result = self.engine.analyze_product(product_name)
        
        if not result['found']:
            return result['message']
        
        # Format as readable text for the agent
        return f"""
**Product Analysis: {result['product_name']}**

**Brand:** {result['brand']}
**Category:** {result['category']}

**Description:** {result['description']}

**Ingredients:** {result['ingredients']}

**Detected Allergens:** {', '.join(result['detected_allergens']) if result['detected_allergens'] else 'None detected'}

**Risk Level:** {result['risk_level'].upper()}

**Ethical Score:** {result['ethical_score']}/100

**Ethical Concerns:** {result['ethical_notes']}

**Recommended Alternatives:** {', '.join(result['recommendations']) if result['recommendations'] else 'No alternatives listed'}
        """.strip()


# Legacy functions for backward compatibility
def load_resources():
    """Legacy function - returns RAG engine instance"""
    engine = RAGEngine()
    return engine.model, {"engine": engine}


def encode_query(model, query: str):
    """Legacy function - encode query"""
    return model.encode(query)


def query_chroma(meta: Dict, query_emb, top_k: int = 3):
    """Legacy function - perform search"""
    engine = meta["engine"]
    return engine.search("", top_k=top_k)


def ask_ollama(context: str, query: str) -> str:
    """Legacy function - simplified response"""
    return json.dumps({
        "detected_allergens": [],
        "risk_level": "medium",
        "ethical_score": 50,
        "recommendations": ["Please use the new MCP server for full analysis"]
    })