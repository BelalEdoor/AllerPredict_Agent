"""
MCP Tool - Wraps the CrewAI workflow as an MCP-compatible tool
"""
from typing import Dict, Any
from pydantic import BaseModel, Field

class ProductAnalysisInput(BaseModel):
    """Input schema for the Product Analysis MCP tool"""
    product_query: str = Field(
        ...,
        description="Product name or question about a food product (e.g., 'Oreo Cookies', 'Is Nutella safe for nut allergies?')",
        min_length=2,
        max_length=200
    )
    user_context: str = Field(
        default="",
        description="Optional: User's specific concerns (e.g., 'I have a peanut allergy', 'Looking for ethical brands')"
    )

class ProductAnalysisOutput(BaseModel):
    """Output schema for the Product Analysis MCP tool"""
    success: bool = Field(..., description="Whether the analysis was successful")
    product_query: str = Field(..., description="The original product query")
    analysis: str = Field(default="", description="Detailed product safety analysis")
    recommendations: str = Field(default="", description="Product recommendations and alternatives")
    full_report: str = Field(default="", description="Complete agent workflow report")
    agents_used: list = Field(default_factory=list, description="List of agents that processed the request")
    error: str = Field(default="", description="Error message if analysis failed")

class ProductAnalysisTool:
    """
    MCP Tool that wraps the AllerPredict AI Agentic workflow
    """
    
    name = "analyze_product_with_agents"
    description = """
    Analyzes food products for allergens, safety risks, and ethical concerns using AI agents.
    
    This tool uses a multi-agent system to:
    1. Analyze product ingredients and detect allergens
    2. Assess ethical and sustainability concerns
    3. Generate safer and more ethical alternatives
    4. Provide actionable recommendations
    
    Use this tool when users ask about:
    - Product safety and allergens
    - Ethical concerns about brands
    - Alternative product recommendations
    - Ingredient analysis
    """
    
    def __init__(self, crew_instance):
        """
        Initialize the MCP tool with a CrewAI instance
        
        Args:
            crew_instance: Instance of AllerPredictCrew
        """
        self.crew = crew_instance
    
    async def execute(self, input_data: ProductAnalysisInput) -> ProductAnalysisOutput:
        """
        Execute the product analysis using the agent workflow
        
        Args:
            input_data: ProductAnalysisInput containing product query and optional context
            
        Returns:
            ProductAnalysisOutput with complete analysis and recommendations
        """
        # Enhance query with user context if provided
        enhanced_query = input_data.product_query
        if input_data.user_context:
            enhanced_query = f"{input_data.product_query} (User context: {input_data.user_context})"
        
        # Execute agent workflow
        result = await self.crew.analyze_product_async(enhanced_query)
        
        # Map to output schema
        return ProductAnalysisOutput(
            success=result.get("success", False),
            product_query=input_data.product_query,
            analysis=result.get("analysis", ""),
            recommendations=result.get("recommendations", ""),
            full_report=result.get("full_report", ""),
            agents_used=result.get("agents_used", []),
            error=result.get("error", result.get("message", ""))
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the MCP tool schema for registration
        
        Returns:
            Dict containing tool name, description, and schemas
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": ProductAnalysisInput.model_json_schema(),
            "output_schema": ProductAnalysisOutput.model_json_schema()
        }

# Factory function to create the tool
def create_product_analysis_tool(crew_instance) -> ProductAnalysisTool:
    """
    Factory function to create a ProductAnalysisTool instance
    
    Args:
        crew_instance: Instance of AllerPredictCrew
        
    Returns:
        ProductAnalysisTool: Configured MCP tool
    """
    return ProductAnalysisTool(crew_instance)