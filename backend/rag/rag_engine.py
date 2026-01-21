"""
FIXED: Accurate Product Analysis Engine
Solves the wrong product matching problem
"""
import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from crewai_tools import BaseTool
from difflib import SequenceMatcher

class AccurateProductAnalyzer:
    """
    Improved analyzer with accurate product matching
    """
    
    def __init__(self, data_file_path=None):
        """Load the AI model and product data"""
        print("Loading AI model...")
        
        # Load the search model
        self.search_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load product database
        if data_file_path is None:
            base_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_file_path = os.path.join(base_folder, "data", "metadata.json")
        
        with open(data_file_path, 'r', encoding='utf-8') as file:
            self.all_products = json.load(file)
        
        # Prepare products for searching
        self.product_search_data = []
        self.product_embeddings = []
        
        for product in self.all_products:
            # Create searchable text (NAME IS MOST IMPORTANT)
            search_text = self._make_searchable_text(product)
            self.product_search_data.append(search_text)
            
            # Convert text to numbers (embedding)
            embedding = self.search_model.encode(search_text)
            self.product_embeddings.append(embedding)
        
        self.product_embeddings = np.array(self.product_embeddings)
        
        print(f"✅ Loaded {len(self.all_products)} products successfully")
    
    def _make_searchable_text(self, product):
        """
        Create searchable text with NAME having highest priority
        """
        name = product.get('name', '')
        brand = product.get('brand', '')
        category = product.get('category', '')
        
        # NAME APPEARS 3 TIMES for higher weight
        combined_text = f"{name} {name} {name} {brand} {brand} {category}"
        return combined_text.strip()
    
    def _calculate_name_similarity(self, search_query, product_name):
        """
        Calculate exact name similarity using string matching
        This prevents wrong product matches
        """
        search_lower = search_query.lower().strip()
        product_lower = product_name.lower().strip()
        
        # Exact match
        if search_lower == product_lower:
            return 1.0
        
        # Contains match
        if search_lower in product_lower or product_lower in search_lower:
            return 0.9
        
        # Word-by-word match
        search_words = set(search_lower.split())
        product_words = set(product_lower.split())
        
        if search_words & product_words:  # If any word matches
            common_words = len(search_words & product_words)
            total_words = len(search_words | product_words)
            return 0.5 + (0.4 * common_words / total_words)
        
        # Character similarity (for typos)
        char_similarity = SequenceMatcher(None, search_lower, product_lower).ratio()
        return char_similarity * 0.6
    
    def find_product(self, search_query):
        """
        IMPROVED: Find product with accurate name matching
        """
        # Step 1: Calculate semantic similarity (AI-based)
        query_embedding = self.search_model.encode(search_query)
        
        semantic_scores = []
        for product_embedding in self.product_embeddings:
            dot_product = np.dot(product_embedding, query_embedding)
            product_length = np.linalg.norm(product_embedding)
            query_length = np.linalg.norm(query_embedding)
            similarity = dot_product / (product_length * query_length)
            semantic_scores.append(similarity)
        
        # Step 2: Calculate name similarity (exact matching)
        name_scores = []
        for product in self.all_products:
            product_name = product.get('name', '')
            brand_name = product.get('brand', '')
            
            # Check both product name and brand
            name_sim = self._calculate_name_similarity(search_query, product_name)
            brand_sim = self._calculate_name_similarity(search_query, brand_name)
            
            # Take the higher score
            final_score = max(name_sim, brand_sim * 0.8)
            name_scores.append(final_score)
        
        # Step 3: Combine both scores (name is MORE important)
        combined_scores = []
        for i in range(len(self.all_products)):
            # 70% name matching, 30% semantic similarity
            combined = (name_scores[i] * 0.7) + (semantic_scores[i] * 0.3)
            combined_scores.append(combined)
        
        # Step 4: Get top 3 matches
        combined_scores = np.array(combined_scores)
        top_3_indices = np.argsort(combined_scores)[-3:][::-1]
        
        results = []
        for index in top_3_indices:
            results.append({
                'product': self.all_products[index],
                'match_score': float(combined_scores[index]),
                'name_match': float(name_scores[index]),
                'semantic_match': float(semantic_scores[index])
            })
        
        return results
    
    def extract_allergens(self, allergen_text):
        """
        Extract and clean allergen list
        """
        if not allergen_text or allergen_text.strip() == "":
            return []
        
        # Clean and split
        allergen_list = [item.strip() for item in allergen_text.split(',')]
        
        # Remove empty and "none" values
        allergen_list = [
            item for item in allergen_list 
            if item and item.lower() not in ['none', 'n/a', 'no allergens', 'nil']
        ]
        
        return allergen_list
    
    def calculate_risk_level(self, allergens, ingredients):
        """
        Multi-factor risk assessment
        """
        risk_score = 0
        
        # Factor 1: Number of allergens
        num_allergens = len(allergens)
        if num_allergens == 0:
            risk_score += 0
        elif num_allergens <= 2:
            risk_score += 30
        elif num_allergens <= 4:
            risk_score += 60
        else:
            risk_score += 90
        
        # Factor 2: High-risk allergens
        allergen_text_lower = ' '.join(allergens).lower()
        high_risk = ['peanut', 'tree nut', 'shellfish', 'fish', 'sesame']
        
        for risk_item in high_risk:
            if risk_item in allergen_text_lower:
                risk_score += 20
                break
        
        # Factor 3: Cross-contamination warnings
        if ingredients:
            ingredients_lower = ingredients.lower()
            if 'may contain' in ingredients_lower or 'traces of' in ingredients_lower:
                risk_score += 15
        
        # Convert to level
        if risk_score <= 20:
            return "low"
        elif risk_score <= 50:
            return "medium"
        else:
            return "high"
    
    def calculate_ethical_score(self, ethical_notes):
        """
        Keyword-based ethical scoring
        """
        if not ethical_notes:
            return 75
        
        ethical_text = ethical_notes.lower()
        score = 100
        
        # Serious violations
        serious = ['child labor', 'forced labor', 'slavery', 'exploitation']
        for issue in serious:
            if issue in ethical_text:
                score -= 30
        
        # Major concerns
        major = ['lawsuit', 'accused', 'investigation', 'violation']
        for concern in major:
            if concern in ethical_text:
                score -= 20
        
        # Moderate issues
        moderate = ['criticism', 'controversy', 'concern', 'disputed']
        for issue in moderate:
            if issue in ethical_text:
                score -= 15
        
        # Positive factors
        positive = ['fair trade', 'organic', 'sustainable', 'certified', 'ethical']
        for factor in positive:
            if factor in ethical_text:
                score += 10
        
        return max(0, min(100, score))
    
    def extract_recommendations(self, recommendation_text):
        """
        Extract product recommendations
        """
        if not recommendation_text or recommendation_text.strip() == "":
            return []
        
        rec_list = [item.strip() for item in recommendation_text.split(',')]
        rec_list = [item for item in rec_list if item and len(item) > 2]
        
        return rec_list
    
    def analyze_product(self, product_query):
        """
        FIXED: Main analysis with accurate matching
        """
        # Find the product
        search_results = self.find_product(product_query)
        best_match = search_results[0]
        
        # STRICTER THRESHOLD: Require high name match OR high combined score
        name_match = best_match['name_match']
        combined_match = best_match['match_score']
        
        # If name match is low AND combined match is low, product not found
        if name_match < 0.4 and combined_match < 0.5:
            return {
                "found": False,
                "message": f"Product '{product_query}' not found in database.",
                "detected_allergens": [],
                "risk_level": "unknown",
                "ethical_score": 0,
                "recommendations": [],
                "similar_products": [
                    {
                        "name": result['product'].get('name'),
                        "brand": result['product'].get('brand'),
                        "name_match": round(result['name_match'] * 100, 1),
                        "overall_match": round(result['match_score'] * 100, 1)
                    }
                    for result in search_results[:3]
                ]
            }
        
        # Extract product data
        product = best_match['product']
        
        product_name = product.get('name', 'Unknown')
        brand = product.get('brand', 'Unknown')
        category = product.get('category', 'Unknown')
        description = product.get('description', '')
        ingredients = product.get('ingredients', '')
        allergen_warnings = product.get('allergen_warnings', '')
        ethical_notes = product.get('ethical_notes', '')
        recommendation_text = product.get('recommendations', '')
        
        # Analyze
        allergens = self.extract_allergens(allergen_warnings)
        risk_level = self.calculate_risk_level(allergens, ingredients)
        ethical_score = self.calculate_ethical_score(ethical_notes)
        recommendations = self.extract_recommendations(recommendation_text)
        
        # VALIDATION: Check if this is really the right product
        confidence = "high" if name_match > 0.8 else "medium" if name_match > 0.5 else "low"
        
        return {
            "found": True,
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "description": description,
            "ingredients": ingredients,
            "detected_allergens": allergens,
            "allergen_count": len(allergens),
            "risk_level": risk_level,
            "ethical_score": ethical_score,
            "ethical_notes": ethical_notes,
            "recommendations": recommendations,
            "match_score": round(combined_match * 100, 1),
            "name_match_score": round(name_match * 100, 1),
            "confidence": confidence,
            "warning": "Low confidence match - please verify product name" if confidence == "low" else None
        }


class ProductAnalysisTool(BaseTool):
    """
    Fixed tool with accurate matching
    """
    name: str = "Accurate Product Safety Analysis Tool"
    description: str = (
        "Analyzes food products with ACCURATE name matching. "
        "Input: exact product name (e.g., 'Coca-Cola Classic', 'Oreo Cookies'). "
        "Returns: Detailed analysis with allergens, risk, and ethical info."
    )
    
    analyzer: any = None
    products: list = []
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'analyzer', AccurateProductAnalyzer())
        object.__setattr__(self, 'products', self.analyzer.all_products)
    
    def _run(self, product_name: str) -> str:
        """
        Run analysis with validation
        """
        result = self.analyzer.analyze_product(product_name)
        
        if not result['found']:
            similar_text = '\n'.join([
                f"- {p['name']} ({p['brand']}) - Name match: {p['name_match']}%"
                for p in result['similar_products']
            ])
            
            return f"""
❌ PRODUCT NOT FOUND

Search query: {product_name}
Message: {result['message']}

Did you mean one of these?
{similar_text}

Please search with the exact product name.
"""
        
        # Format successful analysis
        allergen_text = ', '.join(result['detected_allergens']) if result['detected_allergens'] else '✅ None detected'
        rec_text = '\n'.join([f"- {rec}" for rec in result['recommendations']]) if result['recommendations'] else 'No specific alternatives listed'
        
        # Add warning if low confidence
        warning_text = f"\n\n⚠️ WARNING: {result['warning']}" if result.get('warning') else ""
        
        return f"""
📊 PRODUCT ANALYSIS REPORT

🏷️ Product: {result['product_name']}
🏢 Brand: {result['brand']}
📁 Category: {result['category']}
🎯 Name Match: {result['name_match_score']}%
🎯 Overall Match: {result['match_score']}%
✅ Confidence: {result['confidence'].upper()}{warning_text}

📝 DESCRIPTION:
{result['description']}

🧪 INGREDIENTS:
{result['ingredients']}

⚠️ ALLERGEN ANALYSIS:
Detected Allergens: {allergen_text}
Total Count: {result['allergen_count']}
Risk Level: {result['risk_level'].upper()}

🌍 ETHICAL ASSESSMENT:
Ethical Score: {result['ethical_score']}/100
Details: {result['ethical_notes']}

💡 RECOMMENDED ALTERNATIVES:
{rec_text}

---
Analysis completed with {result['confidence']} confidence.
Match scores: Name={result['name_match_score']}%, Overall={result['match_score']}%
"""