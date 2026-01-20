"""
CrewAI Workflow - Orchestrates the multi-agent system
"""
from crewai import Crew, Task, Process
from typing import Dict, Any
from .analysis_agent import AnalysisAgentConfig
from .recommendation_agent import RecommendationAgentConfig

class AllerPredictCrew:
    """
    Main CrewAI workflow that orchestrates Analysis and Recommendation agents
    """
    
    def __init__(self, rag_tool):
        """
        Initialize the crew with the RAG tool
        
        Args:
            rag_tool: The RAG analysis tool
        """
        self.rag_tool = rag_tool
        self.analysis_agent = AnalysisAgentConfig.create_agent(rag_tool)
        self.recommendation_agent = RecommendationAgentConfig.create_agent()
    
    def analyze_product(self, product_query: str) -> Dict[str, Any]:
        """
        Execute the full agent workflow for product analysis
        
        Args:
            product_query: User's product query (product name or question)
            
        Returns:
            Dict: Complete analysis and recommendations
        """
        # Step 1: Create analysis task
        analysis_task_config = AnalysisAgentConfig.create_task(
            self.analysis_agent, 
            product_query
        )
        
        analysis_task = Task(
            description=analysis_task_config["description"],
            agent=self.analysis_agent,
            expected_output=analysis_task_config["expected_output"]
        )
        
        # Step 2: Create recommendation task (depends on analysis)
        # Note: In CrewAI, we'll pass context through the crew execution
        recommendation_task = Task(
            description="""Based on the analysis from the Product Safety Analyst,
            generate comprehensive recommendations including safer alternatives
            and actionable advice for the user.""",
            agent=self.recommendation_agent,
            expected_output="""A user-friendly recommendation report with alternatives and guidance""",
            context=[analysis_task]  # This task depends on analysis_task
        )
        
        # Step 3: Create and execute the crew
        crew = Crew(
            agents=[self.analysis_agent, self.recommendation_agent],
            tasks=[analysis_task, recommendation_task],
            process=Process.sequential,  # Execute tasks in order
            verbose=True
        )
        
        # Execute the workflow
        try:
            result = crew.kickoff()
            
            # Structure the final output
            return {
                "success": True,
                "product_query": product_query,
                "analysis": str(analysis_task.output) if hasattr(analysis_task, 'output') else "Analysis completed",
                "recommendations": str(recommendation_task.output) if hasattr(recommendation_task, 'output') else str(result),
                "full_report": str(result),
                "agents_used": ["Product Safety Analyst", "Product Recommendation Specialist"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "product_query": product_query,
                "error": str(e),
                "message": "An error occurred during agent workflow execution"
            }
    
    def validate_query(self, query: str) -> tuple[bool, str]:
        """
        Validate user query before processing
        
        Args:
            query: User input
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not query or not query.strip():
            return False, "Please provide a product name or question"
        
        if len(query.strip()) < 2:
            return False, "Query too short. Please provide a product name"
        
        if len(query) > 200:
            return False, "Query too long. Please keep it under 200 characters"
        
        return True, "Valid query"
    
    async def analyze_product_async(self, product_query: str) -> Dict[str, Any]:
        """
        Async version of analyze_product for better performance
        
        Args:
            product_query: User's product query
            
        Returns:
            Dict: Complete analysis and recommendations
        """
        # Validate query first
        is_valid, message = self.validate_query(product_query)
        
        if not is_valid:
            return {
                "success": False,
                "product_query": product_query,
                "error": message
            }
        
        # Execute analysis (CrewAI will handle this synchronously)
        return self.analyze_product(product_query)