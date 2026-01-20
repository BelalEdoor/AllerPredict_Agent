"""
Updated FastAPI Backend - Integrates with MCP Server and maintains REST compatibility
"""
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Any
from fastapi.responses import JSONResponse

# Add paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from agents.crew import AllerPredictCrew
from mcp.tool import create_product_analysis_tool, ProductAnalysisInput
from rag.rag_engine import RAGTool

# Initialize FastAPI
app = FastAPI(
    title="AllerPredict AI - Agentic Product Analysis API",
    description="Agentic AI system for food product safety and ethical analysis",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load product data
DATA_PATH = os.path.join(BASE_DIR, "data", "metadata.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

# Initialize system
print("🚀 Initializing AllerPredict AI System...")
_rag_tool = RAGTool()
_crew = AllerPredictCrew(_rag_tool)
_mcp_tool = create_product_analysis_tool(_crew)
print("✅ System ready!\n")

# ==== Request/Response Models ====
class ProductQuery(BaseModel):
    product_name: str
    user_context: str = ""

class AgenticAnalysisResponse(BaseModel):
    success: bool
    product_query: str
    analysis: str = ""
    recommendations: str = ""
    full_report: str = ""
    agents_used: List[str] = []
    error: str = ""

class LegacyAnalysisOut(BaseModel):
    detected_allergens: List[str]
    risk_level: str
    ethical_score: int
    recommendations: List[str]

# ==== New Agentic Endpoints ====
@app.post("/api/v2/analyze", response_model=AgenticAnalysisResponse)
async def analyze_with_agents(query: ProductQuery):
    """
    NEW: Analyze product using multi-agent system (CrewAI + MCP)
    
    This endpoint uses the full agentic workflow:
    - Product Safety Analyst Agent
    - Recommendation Specialist Agent
    - Returns comprehensive analysis and recommendations
    """
    try:
        input_data = ProductAnalysisInput(
            product_query=query.product_name,
            user_context=query.user_context
        )
        
        result = await _mcp_tool.execute(input_data)
        
        return AgenticAnalysisResponse(
            success=result.success,
            product_query=result.product_query,
            analysis=result.analysis,
            recommendations=result.recommendations,
            full_report=result.full_report,
            agents_used=result.agents_used,
            error=result.error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/products")
async def get_products_v2():
    """
    Get list of all available products
    """
    return JSONResponse(content={
        "success": True,
        "count": len(PRODUCTS),
        "products": PRODUCTS
    })

@app.get("/api/v2/health")
async def health_check():
    """
    Check system health and status
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "system": "agentic",
        "agents": ["Product Safety Analyst", "Recommendation Specialist"],
        "rag_loaded": True,
        "crew_initialized": True
    }

# ==== Legacy Endpoints (Backward Compatibility) ====
@app.get("/products")
async def get_products_legacy():
    """
    LEGACY: Get products (maintains compatibility with old frontend)
    """
    return JSONResponse(content=PRODUCTS)

@app.post("/analyze_product", response_model=LegacyAnalysisOut)
async def analyze_product_legacy(query: ProductQuery):
    """
    LEGACY: Analyze product using direct RAG (backward compatible)
    
    Note: This endpoint is maintained for backward compatibility.
    Use /api/v2/analyze for full agentic capabilities.
    """
    try:
        # Use RAG tool directly for legacy support
        analysis_text = _rag_tool(query.product_name)
        
        # Parse the analysis text to extract structured data
        # This is a simplified version - in production, you'd parse more carefully
        allergens = []
        risk_level = "medium"
        ethical_score = 50
        recommendations = []
        
        if "Detected Allergens:" in analysis_text:
            allergen_line = analysis_text.split("Detected Allergens:")[1].split("\n")[0]
            if allergen_line.strip() and "None" not in allergen_line:
                allergens = [a.strip() for a in allergen_line.split(",")]
        
        if "Risk Level:" in analysis_text:
            risk_line = analysis_text.split("Risk Level:")[1].split("\n")[0]
            risk_level = risk_line.strip().lower().replace("*", "")
        
        if "Ethical Score:" in analysis_text:
            score_line = analysis_text.split("Ethical Score:")[1].split("/")[0]
            try:
                ethical_score = int(score_line.strip())
            except:
                ethical_score = 50
        
        if "Recommended Alternatives:" in analysis_text:
            rec_line = analysis_text.split("Recommended Alternatives:")[1].split("\n")[0]
            if rec_line.strip() and "No alternatives" not in rec_line:
                recommendations = [r.strip() for r in rec_line.split(",")]
        
        return LegacyAnalysisOut(
            detected_allergens=allergens,
            risk_level=risk_level,
            ethical_score=ethical_score,
            recommendations=recommendations if recommendations else [
                "Use /api/v2/analyze for detailed agent-based recommendations"
            ]
        )
    except Exception as e:
        return LegacyAnalysisOut(
            detected_allergens=[],
            risk_level="error",
            ethical_score=0,
            recommendations=[f"Error: {str(e)}"]
        )

# ==== Info Endpoints ====
@app.get("/")
async def root():
    """
    API information and available endpoints
    """
    return {
        "name": "AllerPredict AI",
        "version": "2.0.0",
        "description": "Agentic AI system for food product analysis",
        "architecture": {
            "rag": "Retrieval-Augmented Generation",
            "agents": "CrewAI Multi-Agent System",
            "mcp": "Model Context Protocol",
            "backend": "FastAPI"
        },
        "endpoints": {
            "v2_analyze": "POST /api/v2/analyze - Full agentic analysis",
            "v2_products": "GET /api/v2/products - Get all products",
            "v2_health": "GET /api/v2/health - Health check",
            "legacy_analyze": "POST /analyze_product - Legacy endpoint",
            "legacy_products": "GET /products - Legacy endpoint"
        },
        "agents": [
            "Product Safety Analyst - Allergen detection and risk assessment",
            "Recommendation Specialist - Alternative products and guidance"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("AllerPredict AI - Agentic Backend Server")
    print("=" * 60)
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔍 Legacy API: http://localhost:8000/products")
    print("🤖 Agentic API: http://localhost:8000/api/v2/analyze")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)