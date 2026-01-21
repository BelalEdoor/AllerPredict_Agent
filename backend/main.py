"""
Simplified FastAPI Server
Easy-to-understand web API for product analysis
"""
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import JSONResponse

# Setup paths
BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_FOLDER, "backend"))

# Import our simplified components
from rag.rag_engine import ProductAnalysisTool
from agents.crew import ProductAnalysisCrew

# Create FastAPI app
app = FastAPI(
    title="AllerPredict AI - Food Safety Analyzer",
    description="Simple and accurate food product safety analysis using AI",
    version="2.0.0"
)

# Enable CORS (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load product database
DATA_FILE = os.path.join(BASE_FOLDER, "data", "metadata.json")
with open(DATA_FILE, "r", encoding="utf-8") as file:
    ALL_PRODUCTS = json.load(file)

# Initialize the AI system
print("\n" + "="*60)
print("🚀 Starting AllerPredict AI System...")
print("="*60)

analysis_tool = ProductAnalysisTool()
crew_manager = ProductAnalysisCrew(analysis_tool)

print("✅ System ready!")
print("="*60 + "\n")


# === Request/Response Models ===

class ProductRequest(BaseModel):
    """What the user sends"""
    product_name: str
    user_context: str = ""  # Optional: e.g., "I have peanut allergy"


class AnalysisResponse(BaseModel):
    """What we send back"""
    success: bool
    product_query: str
    analysis: str = ""
    recommendations: str = ""
    full_report: str = ""
    agents_used: List[str] = []
    error: str = ""


class SimpleResponse(BaseModel):
    """Simple legacy format"""
    detected_allergens: List[str]
    risk_level: str
    ethical_score: int
    recommendations: List[str]


# === Main API Endpoints ===

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_product(request: ProductRequest):
    """
    Main endpoint: Analyze a food product
    
    Example request:
    {
        "product_name": "Oreo Cookies",
        "user_context": "I have dairy allergy"
    }
    """
    try:
        # Combine product name with user context if provided
        full_query = request.product_name
        if request.user_context:
            full_query = f"{request.product_name} (User note: {request.user_context})"
        
        # Run the analysis
        result = await crew_manager.analyze_product_async(full_query)
        
        return AnalysisResponse(
            success=result["success"],
            product_query=request.product_name,
            analysis=result.get("analysis", ""),
            recommendations=result.get("recommendations", ""),
            full_report=result.get("full_report", ""),
            agents_used=result.get("agents_used", []),
            error=result.get("error", "")
        )
        
    except Exception as error:
        print(f"❌ Error: {str(error)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(error)}"
        )


# V2 Analyze endpoint (for compatibility with frontend)
@app.post("/api/v2/analyze", response_model=AnalysisResponse)
async def analyze_product_v2(request: ProductRequest):
    """V2 Analysis endpoint - same as /api/analyze"""
    return await analyze_product(request)


@app.get("/api/products")
async def get_all_products():
    """
    Get list of all products in database
    """
    return JSONResponse(content={
        "success": True,
        "total_products": len(ALL_PRODUCTS),
        "products": ALL_PRODUCTS
    })


@app.get("/api/v2/products")
async def get_all_products_v2():
    """V2 Products endpoint"""
    return JSONResponse(content={
        "success": True,
        "total_products": len(ALL_PRODUCTS),
        "products": ALL_PRODUCTS
    })


@app.get("/api/products/category/{category}")
async def get_products_by_category(category: str):
    """
    Get products in a specific category
    Example: /api/products/category/Cookies
    """
    matching = crew_manager.search_products_by_category(category)
    
    return JSONResponse(content={
        "success": True,
        "category": category,
        "count": len(matching),
        "products": matching
    })


@app.post("/api/quick-check")
async def quick_allergen_check(request: dict):
    """
    Quick check if a product contains a specific allergen
    
    Example request:
    {
        "product_name": "Nutella",
        "allergen": "nuts"
    }
    """
    product_name = request.get("product_name")
    allergen = request.get("allergen")
    
    if not product_name or not allergen:
        raise HTTPException(
            status_code=400,
            detail="Missing product_name or allergen"
        )
    
    result = crew_manager.quick_allergen_check(product_name, allergen)
    
    return JSONResponse(content=result)


@app.get("/api/health")
async def health_check():
    """
    Check if system is working
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "system": "operational",
        "agents": [
            "Product Safety Analyst",
            "Recommendation Specialist"
        ],
        "database_loaded": len(ALL_PRODUCTS) > 0,
        "total_products": len(ALL_PRODUCTS)
    }


# === Legacy Endpoints (for backward compatibility) ===

@app.get("/products")
async def legacy_get_products():
    """Old endpoint - still works"""
    return JSONResponse(content=ALL_PRODUCTS)


@app.post("/analyze_product", response_model=SimpleResponse)
async def legacy_analyze(request: ProductRequest):
    """
    Old simple format - still works
    Parses the full analysis into simple format
    """
    try:
        # Get full analysis
        result = await crew_manager.analyze_product_async(request.product_name)
        
        if not result["success"]:
            return SimpleResponse(
                detected_allergens=[],
                risk_level="error",
                ethical_score=0,
                recommendations=[result.get("error", "Analysis failed")]
            )
        
        # Parse the analysis text to extract simple data
        analysis_text = result.get("analysis", "")
        
        # Extract allergens
        allergens = []
        if "detected allergens:" in analysis_text.lower():
            allergen_section = analysis_text.lower().split("detected allergens:")[1]
            allergen_line = allergen_section.split("\n")[0]
            if "none" not in allergen_line.lower():
                allergens = [a.strip() for a in allergen_line.split(",") if a.strip()]
        
        # Extract risk level
        risk_level = "medium"
        if "risk level:" in analysis_text.lower():
            risk_section = analysis_text.lower().split("risk level:")[1]
            risk_line = risk_section.split("\n")[0].strip()
            if "low" in risk_line:
                risk_level = "low"
            elif "high" in risk_line:
                risk_level = "high"
        
        # Extract ethical score
        ethical_score = 50
        if "ethical score:" in analysis_text.lower():
            score_section = analysis_text.lower().split("ethical score:")[1]
            score_text = score_section.split("/")[0].strip()
            try:
                ethical_score = int(''.join(filter(str.isdigit, score_text)))
            except:
                ethical_score = 50
        
        # Extract recommendations
        rec_text = result.get("recommendations", "")
        recommendations = []
        if rec_text:
            # Try to find product names in recommendations
            lines = rec_text.split("\n")
            for line in lines:
                if any(word in line.lower() for word in ["alternative", "instead", "try", "recommend"]):
                    recommendations.append(line.strip())
        
        if not recommendations:
            recommendations = ["See full analysis for detailed recommendations"]
        
        return SimpleResponse(
            detected_allergens=allergens,
            risk_level=risk_level,
            ethical_score=ethical_score,
            recommendations=recommendations[:5]  # Max 5 recommendations
        )
        
    except Exception as error:
        return SimpleResponse(
            detected_allergens=[],
            risk_level="error",
            ethical_score=0,
            recommendations=[f"Error: {str(error)}"]
        )


# === Info Endpoint ===

@app.get("/")
async def api_info():
    """
    API information and instructions
    """
    return {
        "name": "AllerPredict AI",
        "version": "2.0.0",
        "description": "Simple and accurate food safety analysis",
        "status": "operational",
        
        "main_endpoints": {
            "analyze": {
                "url": "POST /api/analyze",
                "description": "Analyze a product for safety",
                "example": {
                    "product_name": "Oreo Cookies",
                    "user_context": "I have dairy allergy"
                }
            },
            "products": {
                "url": "GET /api/products",
                "description": "Get all products"
            },
            "quick_check": {
                "url": "POST /api/quick-check",
                "description": "Quick allergen check",
                "example": {
                    "product_name": "Nutella",
                    "allergen": "nuts"
                }
            },
            "health": {
                "url": "GET /api/health",
                "description": "System status"
            }
        },
        
        "features": [
            "Accurate allergen detection",
            "Risk level assessment (low/medium/high)",
            "Ethical scoring (0-100)",
            "Alternative product recommendations",
            "AI-powered analysis with 2 specialized agents"
        ],
        
        "documentation": "Visit /docs for interactive API documentation"
    }


# === Run Server ===

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🌐 AllerPredict AI Server")
    print("="*60)
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔍 Main API: http://localhost:8000/api/analyze")
    print("📦 Products: http://localhost:8000/api/products")
    print("❤️  Health: http://localhost:8000/api/health")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)