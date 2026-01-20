"""
Analysis Agent - Responsible for product analysis using RAG
"""
from crewai import Agent
from langchain_community.llms import Ollama
from typing import Dict, Any

class AnalysisAgentConfig:
    """Configuration for the Analysis Agent"""
    
    @staticmethod
    def create_agent(rag_tool) -> Agent:
        """
        Creates the Analysis Agent that performs allergen detection,
        ethical analysis, and risk assessment.
        
        Args:
            rag_tool: The RAG analysis tool to be used by the agent
            
        Returns:
            Agent: Configured Analysis Agent
        """
        # Use Ollama as the LLM backend
        llm = Ollama(
            model="llama2",
            temperature=0.7
        )
        
        return Agent(
            role="Product Safety Analyst",
            goal="Analyze food products for allergens, safety risks, and ethical concerns using comprehensive product data",
            backstory="""You are an expert food safety analyst with deep knowledge of:
            - Common food allergens (gluten, dairy, nuts, soy, etc.)
            - Product ingredient analysis
            - Ethical and sustainability concerns in food manufacturing
            - Risk assessment methodologies
            
            You use advanced RAG (Retrieval-Augmented Generation) technology to access 
            a comprehensive database of product information and provide accurate, 
            evidence-based analysis.
            
            Your analysis helps people with allergies, dietary restrictions, or 
            ethical concerns make informed decisions about food products.""",
            tools=[rag_tool] if rag_tool else [],  # تأكد إنو list
            verbose=True,
            allow_delegation=True,
            llm=llm
            # أزلنا max_iter لأنو مش مدعوم بهاد الإصدار
        )
    
    @staticmethod
    def create_task(agent: Agent, product_query: str) -> Dict[str, Any]:
        """
        Creates an analysis task for the agent
        
        Args:
            agent: The Analysis Agent
            product_query: User's product query
            
        Returns:
            Dict containing task configuration
        """
        return {
            "description": f"""Analyze the following product query: "{product_query}"
            
            Your analysis must include:
            1. Product identification and category
            2. Complete list of detected allergens
            3. Risk level assessment (low/medium/high)
            4. Ethical score (0-100) based on:
               - Labor practices
               - Environmental impact
               - Supply chain transparency
            5. Key concerns or warnings
            
            Use the RAG tool to retrieve accurate product information.
            If the product is not found or information is insufficient, clearly state this.
            """,
            "agent": agent,
            "expected_output": """A structured analysis containing:
            - Product name and brand
            - Detected allergens (list)
            - Risk level (low/medium/high)
            - Ethical score (0-100)
            - Detailed concerns and warnings
            """
        }