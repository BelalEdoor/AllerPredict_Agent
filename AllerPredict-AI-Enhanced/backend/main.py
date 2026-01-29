"""FastAPI Main Application - Dual Mode Support"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from rag.pipeline import RAGPipeline

# Initialize FastAPI
app = FastAPI(
    title="AllerPredict AI",
    description="Intelligent Product Analysis System with Multi-Agent AI",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system
print("🚀 Initializing AllerPredict AI...")

# Try to load CrewAI (optional)
CREW_AVAILABLE = False
crew = None

try:
    print("📦 Loading CrewAI Multi-Agent System...")
    from agents.crew_orchestrator import AllerPredictCrew
    crew = AllerPredictCrew()
    CREW_AVAILABLE = True
    print("✅ CrewAI Multi-Agent System loaded successfully!")
except Exception as e:
    print(f"⚠️  CrewAI not available: {e}")
    print("📋 Running in Quick Analysis mode only")
    # Initialize RAG directly as fallback
    try:
        rag = RAGPipeline()
        print(f"✅ RAG System loaded with {len(rag.products)} products")
    except Exception as e:
        print(f"❌ Error loading RAG: {e}")
        raise

# Pydantic Models
class ProductQuery(BaseModel):
    query: str
    user_allergies: Optional[List[str]] = None
    detailed_analysis: bool = False

class AlternativeRequest(BaseModel):
    allergens: List[str]
    category: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "active",
        "service": "AllerPredict AI",
        "version": "2.0.0",
        "features": ["RAG", "Ollama"] + (["CrewAI", "Multi-Agent"] if CREW_AVAILABLE else []),
        "mode": "Full" if CREW_AVAILABLE else "Quick Analysis Only"
    }

@app.get("/products")
async def get_products():
    """Get all products in database"""
    products = crew.rag.products if CREW_AVAILABLE else rag.products
    return {"products": products}

@app.post("/analyze")
async def analyze_product(request: ProductQuery):
    """
    Analyze a product using AI system
    
    - **query**: Product name or description
    - **user_allergies**: Optional list of user allergies
    - **detailed_analysis**: Use full crew analysis (only if CrewAI available)
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing: {request.query}")
        print(f"   Detailed Mode: {request.detailed_analysis}")
        print(f"   CrewAI Available: {CREW_AVAILABLE}")
        print(f"{'='*60}\n")
        
        # Build user profile
        user_profile = None
        if request.user_allergies:
            user_profile = {"allergies": request.user_allergies}
            print(f"👤 User Allergies: {request.user_allergies}")
        
        # Choose analysis mode
        if CREW_AVAILABLE and request.detailed_analysis:
            print("🤖 Using Multi-Agent Analysis (CrewAI)...")
            result = crew.analyze_product(request.query, user_profile)
        else:
            if request.detailed_analysis and not CREW_AVAILABLE:
                print("⚠️  Detailed analysis requested but CrewAI not available")
                print("📋 Falling back to Quick Analysis...")
            
            print("⚡ Using Quick Analysis (RAG + Ollama)...")
            
            # Use RAG from crew or standalone
            rag_instance = crew.rag if CREW_AVAILABLE else rag
            
            # Search for product
            search_results = rag_instance.search(request.query, top_k=1)
            
            if not search_results:
                raise HTTPException(status_code=404, detail="Product not found")
            
            product = search_results[0]
            print(f"✅ Found: {product['name']}")
            
            # Build query with user context
            user_context = ""
            if request.user_allergies:
                user_context = f"\nUser has allergies to: {', '.join(request.user_allergies)}"
            
            query_text = f"Analyze {product['name']} for safety and allergens.{user_context}"
            
            # Get AI analysis
            print("🤖 Generating AI analysis...")
            analysis = rag_instance.analyze_with_llm(product, query_text)
            
            # Find alternatives
            print("🔄 Finding safe alternatives...")
            allergens_to_avoid = product.get('allergens', [])
            if request.user_allergies:
                allergens_to_avoid = list(set(allergens_to_avoid + request.user_allergies))
            
            alternatives = rag_instance.find_alternatives(allergens_to_avoid, product['id'])
            
            result = {
                "product": {
                    "name": product['name'],
                    "brand": product['brand'],
                    "category": product['category'],
                    "allergens": product['allergens'],
                    "ethical_score": product['ethical_score'],
                    "similarity_score": product.get('similarity_score', 0)
                },
                "analysis": analysis,
                "alternatives": alternatives
            }
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        print("\n✅ Analysis complete!\n")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/alternatives")
async def find_alternatives(request: AlternativeRequest):
    """Find safe alternative products"""
    try:
        rag_instance = crew.rag if CREW_AVAILABLE else rag
        alternatives = rag_instance.find_alternatives(
            allergens=request.allergens,
            exclude_id=-1
        )
        
        # Filter by category if provided
        if request.category:
            alternatives = [
                alt for alt in alternatives 
                if alt.get('category', '').lower() == request.category.lower()
            ]
        
        return {
            "allergens_avoided": request.allergens,
            "alternatives": alternatives[:5]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/{query}")
async def search_products(query: str, limit: int = 5):
    """Search for products by name or description"""
    try:
        rag_instance = crew.rag if CREW_AVAILABLE else rag
        results = rag_instance.search(query, top_k=limit)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    """Get specific product by ID"""
    products = crew.rag.products if CREW_AVAILABLE else rag.products
    for product in products:
        if product['id'] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# Health check for monitoring
@app.get("/health")
async def health_check():
    """Detailed health check"""
    products = crew.rag.products if CREW_AVAILABLE else rag.products
    return {
        "status": "healthy",
        "rag_loaded": len(products) > 0,
        "crew_available": CREW_AVAILABLE,
        "agents_initialized": CREW_AVAILABLE,
        "mode": "Full (Multi-Agent + Quick)" if CREW_AVAILABLE else "Quick Analysis Only",
        "models": {
            "embeddings": "all-MiniLM-L6-v2",
            "llm": "llama3.2 (Ollama)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting AllerPredict AI")
    print("="*60)
    if CREW_AVAILABLE:
        print("✅ Mode: Full System (Multi-Agent + Quick Analysis)")
        print("💡 Use detailed_analysis=true for Multi-Agent")
        print("💡 Use detailed_analysis=false for Quick Analysis")
    else:
        print("⚠️  Mode: Quick Analysis Only (CrewAI not available)")
        print("💡 All requests will use Quick Analysis")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )