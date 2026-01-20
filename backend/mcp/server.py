"""
MCP Server - Exposes the Product Analysis tool via FastMCP
"""
import os
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from agents.crew import AllerPredictCrew
from mcp.tool import create_product_analysis_tool, ProductAnalysisInput
from rag.rag_engine import RAGTool

# Initialize FastMCP server
mcp = FastMCP("AllerPredict AI Server")

# Global instances
_crew_instance = None
_rag_tool = None

def initialize_system():
    """Initialize the RAG system and CrewAI workflow"""
    global _crew_instance, _rag_tool
    
    if _crew_instance is None:
        print("🚀 Initializing AllerPredict AI System...")
        
        # Initialize RAG tool
        _rag_tool = RAGTool()
        print("✅ RAG System loaded")
        
        # Initialize CrewAI workflow
        _crew_instance = AllerPredictCrew(_rag_tool)
        print("✅ CrewAI Agents initialized")
        print("✅ MCP Server ready\n")
    
    return _crew_instance

@mcp.tool()
async def analyze_product(product_query: str, user_context: str = "") -> dict[str, Any]:
    """
    Analyze a food product for allergens, safety, and ethical concerns.
    
    Args:
        product_query: Name of the product or question about a product
        user_context: Optional user-specific context (allergies, preferences)
    
    Returns:
        Complete analysis with recommendations from AI agents
    """
    # Initialize system if needed
    crew = initialize_system()
    
    # Create tool and execute
    tool = create_product_analysis_tool(crew)
    input_data = ProductAnalysisInput(
        product_query=product_query,
        user_context=user_context
    )
    
    result = await tool.execute(input_data)
    
    # Return as dictionary
    return {
        "success": result.success,
        "product_query": result.product_query,
        "analysis": result.analysis,
        "recommendations": result.recommendations,
        "full_report": result.full_report,
        "agents_used": result.agents_used,
        "error": result.error
    }

@mcp.tool()
async def get_products() -> dict[str, Any]:
    """
    Get list of available products in the database.
    
    Returns:
        List of products with basic information
    """
    crew = initialize_system()
    
    # Access product data from RAG tool
    if _rag_tool and hasattr(_rag_tool, 'products'):
        return {
            "success": True,
            "products": _rag_tool.products,
            "count": len(_rag_tool.products)
        }
    
    return {
        "success": False,
        "error": "Products not loaded",
        "products": []
    }

@mcp.resource("allerpredict://system/info")
async def get_system_info() -> str:
    """
    Get information about the AllerPredict AI system.
    
    Returns:
        System information and capabilities
    """
    return """
    # AllerPredict AI - Agentic Product Analysis System
    
    ## Overview
    AllerPredict AI is an advanced agentic system that analyzes food products for:
    - Allergen detection and safety assessment
    - Ethical and sustainability concerns
    - Alternative product recommendations
    
    ## Architecture
    - **RAG Pipeline**: Retrieval-Augmented Generation for accurate product data
    - **Multi-Agent System**: CrewAI-powered analysis and recommendation workflow
    - **MCP Server**: Model Context Protocol for tool exposure
    
    ## Agents
    1. **Product Safety Analyst**: Analyzes allergens and risks
    2. **Recommendation Specialist**: Suggests safer alternatives
    
    ## Capabilities
    - Real-time product analysis
    - Personalized recommendations
    - Evidence-based risk assessment
    - Ethical scoring (0-100)
    
    ## Usage
    Use the `analyze_product` tool with a product name or question.
    """

@mcp.prompt()
async def product_analysis_prompt(product_name: str) -> str:
    """
    Generate a structured prompt for product analysis.
    
    Args:
        product_name: Name of the product to analyze
    
    Returns:
        Formatted prompt for the AI agents
    """
    return f"""
    Please analyze the product: {product_name}
    
    Provide:
    1. Allergen detection
    2. Safety risk assessment
    3. Ethical score and concerns
    4. Recommended alternatives
    
    Format the response in a user-friendly way.
    """

# Health check endpoint
@mcp.tool()
async def health_check() -> dict[str, Any]:
    """
    Check if the MCP server and all systems are operational.
    
    Returns:
        System health status
    """
    try:
        crew = initialize_system()
        return {
            "status": "healthy",
            "rag_loaded": _rag_tool is not None,
            "crew_initialized": _crew_instance is not None,
            "server": "FastMCP",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    # Run the MCP server
    print("=" * 50)
    print("AllerPredict AI - MCP Server")
    print("=" * 50)
    initialize_system()
    mcp.run()