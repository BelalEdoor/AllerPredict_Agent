"""
Recommendation Agent - Generates safer and more ethical alternatives
"""
from crewai import Agent
from langchain_community.llms import Ollama
from typing import Dict, Any

class RecommendationAgentConfig:
    """Configuration for the Recommendation Agent"""
    
    @staticmethod
    def create_agent() -> Agent:
        """
        Creates the Recommendation Agent that suggests safer and more ethical alternatives
        
        Returns:
            Agent: Configured Recommendation Agent
        """
        llm = Ollama(
            model="llama2",
            temperature=0.7
        )
        
        return Agent(
            role="Product Recommendation Specialist",
            goal="Provide safer, healthier, and more ethical product alternatives based on analysis results",
            backstory="""You are a product recommendation specialist with expertise in:
            - Allergen-free alternatives
            - Ethical and sustainable brands
            - Local and fair-trade products
            - Health-conscious food choices
            
            You analyze the results from the safety analyst and generate personalized 
            recommendations that prioritize:
            1. Safety (allergen-free options)
            2. Ethics (fair trade, sustainable practices)
            3. Quality and taste
            4. Availability in local markets
            
            Your recommendations help users make better choices aligned with their 
            health needs and values.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
            # أزلنا max_iter
        )
    
    @staticmethod
    def create_task(agent: Agent, analysis_result: str) -> Dict[str, Any]:
        """
        Creates a recommendation task based on analysis results
        
        Args:
            agent: The Recommendation Agent
            analysis_result: Results from the Analysis Agent
            
        Returns:
            Dict containing task configuration
        """
        return {
            "description": f"""Based on the following product analysis:

{analysis_result}

Generate a comprehensive recommendation report that includes:

1. **Safety Assessment Summary**
   - Highlight the most critical allergens or risks
   - Explain why these are concerning

2. **Alternative Products** (2-4 options)
   - Safer alternatives (allergen-free)
   - More ethical alternatives (better ethical scores)
   - Provide specific product names when available

3. **Actionable Recommendations**
   - Clear guidance for the user
   - What to look for in product labels
   - Tips for safer shopping

4. **Final Verdict**
   - Should the user avoid this product?
   - Is it safe with precautions?
   - Overall recommendation rating

Format the output as a user-friendly report that is easy to understand.
""",
            "agent": agent,
            "expected_output": """A complete recommendation report with:
            - Safety summary
            - 2-4 alternative product suggestions
            - Actionable shopping tips
            - Final verdict and rating
            """
        }
    
    @staticmethod
    def generate_final_report(analysis: Dict[str, Any], recommendations: str) -> Dict[str, Any]:
        """
        Combines analysis and recommendations into final structured output
        
        Args:
            analysis: Analysis results
            recommendations: Recommendation text
            
        Returns:
            Dict: Complete structured report
        """
        return {
            "product_analysis": analysis,
            "recommendations": recommendations,
            "status": "completed",
            "agent_workflow": "analysis → recommendation → report"
        }