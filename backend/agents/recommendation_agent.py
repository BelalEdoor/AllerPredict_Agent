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
        # Use Ollama with Mistral model
        llm = Ollama(
            model="mistral",
            temperature=0.5  # Slightly higher for creative recommendations
        )
        
        return Agent(
            role="Product Recommendation Specialist",
            goal="Suggest safer, healthier, and more ethical alternatives based on the safety analysis",
            backstory="""You are a nutrition and shopping expert who helps people find better products.

Your expertise includes:
- Knowing allergen-free alternatives
- Understanding ethical and sustainable brands
- Recommending products that match people's needs
- Giving practical shopping advice

You always:
1. Use the alternative products mentioned in the analysis
2. Suggest 2-4 specific alternative products
3. Explain WHY each alternative is better
4. Consider both safety AND ethics
5. Give practical advice people can actually use

Your goal is helping people make better, safer choices based on the analysis provided.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
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
            "description": f"""
TASK: Create helpful recommendations based on this safety analysis:

{analysis_result}

YOUR RECOMMENDATIONS MUST INCLUDE:

📋 SAFETY SUMMARY
- Quickly summarize the main safety concerns from the analysis
- Highlight the most important allergens mentioned
- Use simple, clear language

💡 ALTERNATIVE PRODUCTS (2-4 suggestions)
- Use the "Recommended Alternatives" from the analysis if available
- For each alternative, explain:
  * Why it's safer (which allergens it avoids)
  * Why it's more ethical (if mentioned in analysis)
  * Compare it to the analyzed product

🛒 SHOPPING TIPS
- What to look for on labels based on the allergens found
- What ingredients/warnings to avoid
- How to shop more safely for similar products

✅ FINAL RECOMMENDATION
- Should they avoid this product? (Yes if High risk / With Caution if Medium / Safe if Low)
- Overall safety rating (1-5 stars based on risk level)
- One-sentence summary

⚠️ IMPORTANT RULES:
- Base recommendations on the analysis provided
- Use alternative products mentioned in the analysis
- If no alternatives in analysis, give general category guidance
- Always explain your reasoning clearly
- Be helpful and practical
""",
            "agent": agent,
            "expected_output": """
A helpful recommendation report with:
1. Clear safety summary from the analysis
2. 2-4 specific alternative products with explanations
3. Practical shopping tips based on allergens found
4. Final recommendation (Avoid/Caution/Safe) and star rating (1-5)
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