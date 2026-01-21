"""
Simplified Crew Manager
Coordinates the two AI agents to analyze products
"""
from crewai import Crew, Task, Process
from typing import Dict, Any

class ProductAnalysisCrew:
    """
    Manages the team of AI agents that analyze products
    Simple and reliable workflow
    """
    
    def __init__(self, analysis_tool):
        """
        Set up the crew with both agents
        
        Args:
            analysis_tool: The product analysis tool
        """
        # Import agent creators
        from agents.analysis_agent import SafetyAnalysisAgent, RecommendationAgent
        
        # Create both agents
        self.safety_agent = SafetyAnalysisAgent.create(analysis_tool)
        self.recommendation_agent = RecommendationAgent.create()
        
        # Store the tool for later use
        self.analysis_tool = analysis_tool
        
        print("✅ Both AI agents ready")
    
    def validate_query(self, query):
        """
        Check if the user's query is valid
        
        Args:
            query: User's product search
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if query exists
        if not query or not query.strip():
            return False, "Please enter a product name"
        
        # Check minimum length
        if len(query.strip()) < 2:
            return False, "Product name too short. Please enter at least 2 characters"
        
        # Check maximum length
        if len(query) > 200:
            return False, "Product name too long. Please keep it under 200 characters"
        
        # Check for suspicious content
        suspicious_words = ['<script>', 'javascript:', 'DROP TABLE', 'DELETE FROM']
        query_lower = query.lower()
        for word in suspicious_words:
            if word.lower() in query_lower:
                return False, "Invalid characters in product name"
        
        return True, "Valid query"
    
    def analyze_product(self, product_query):
        """
        Main function: Analyze a product using both agents
        
        Args:
            product_query: Product name to analyze
            
        Returns:
            dict: Complete analysis with safety info and recommendations
        """
        # Step 1: Validate the query
        is_valid, error_message = self.validate_query(product_query)
        
        if not is_valid:
            return {
                "success": False,
                "product_query": product_query,
                "error": error_message,
                "analysis": "",
                "recommendations": "",
                "full_report": ""
            }
        
        # Step 2: Create safety analysis task
        from agents.analysis_agent import SafetyAnalysisAgent
        
        safety_task_config = SafetyAnalysisAgent.create_task(
            self.safety_agent,
            product_query
        )
        
        safety_task = Task(
            description=safety_task_config["description"],
            agent=self.safety_agent,
            expected_output=safety_task_config["expected_output"]
        )
        
        # Step 3: Create recommendation task (waits for safety analysis)
        from agents.analysis_agent import RecommendationAgent
        
        recommendation_task = Task(
            description=RecommendationAgent.create_task(
                self.recommendation_agent, 
                "Previous analysis results"
            )["description"],
            agent=self.recommendation_agent,
            expected_output=RecommendationAgent.create_task(
                self.recommendation_agent,
                "Previous analysis results"
            )["expected_output"],
            context=[safety_task]  # Wait for safety task to complete first
        )
        
        # Step 4: Create the crew and execute
        crew = Crew(
            agents=[self.safety_agent, self.recommendation_agent],
            tasks=[safety_task, recommendation_task],
            process=Process.sequential,  # Run tasks one after another
            verbose=True
        )
        
        # Step 5: Run the analysis
        try:
            print(f"\n🔍 Starting analysis for: {product_query}\n")
            
            result = crew.kickoff()
            
            # Extract results from both tasks
            safety_analysis = str(safety_task.output) if hasattr(safety_task, 'output') else "Safety analysis completed"
            recommendations = str(recommendation_task.output) if hasattr(recommendation_task, 'output') else str(result)
            
            return {
                "success": True,
                "product_query": product_query,
                "analysis": safety_analysis,
                "recommendations": recommendations,
                "full_report": str(result),
                "agents_used": ["Product Safety Analyst", "Product Recommendation Specialist"]
            }
            
        except Exception as error:
            print(f"❌ Error during analysis: {str(error)}")
            
            return {
                "success": False,
                "product_query": product_query,
                "error": str(error),
                "message": "An error occurred. Please try again or contact support.",
                "analysis": "",
                "recommendations": "",
                "full_report": ""
            }
    
    async def analyze_product_async(self, product_query):
        """
        Async version for web servers
        
        Args:
            product_query: Product name to analyze
            
        Returns:
            dict: Analysis results
        """
        # Validate first
        is_valid, error_message = self.validate_query(product_query)
        
        if not is_valid:
            return {
                "success": False,
                "product_query": product_query,
                "error": error_message
            }
        
        # Run the regular analysis
        # (CrewAI runs synchronously, so we just call the regular method)
        return self.analyze_product(product_query)
    
    def get_all_products(self):
        """
        Get list of all products in the database
        
        Returns:
            list: All products
        """
        if hasattr(self.analysis_tool, 'products'):
            return self.analysis_tool.products
        return []
    
    def search_products_by_category(self, category):
        """
        Find products in a specific category
        
        Args:
            category: Category name (e.g., "Cookies", "Chocolate")
            
        Returns:
            list: Products in that category
        """
        all_products = self.get_all_products()
        category_lower = category.lower()
        
        matching_products = [
            product for product in all_products
            if category_lower in product.get('category', '').lower()
        ]
        
        return matching_products
    
    def quick_allergen_check(self, product_name, specific_allergen):
        """
        Quick check if a product contains a specific allergen
        
        Args:
            product_name: Product to check
            specific_allergen: Allergen to look for (e.g., "peanuts")
            
        Returns:
            dict: Quick check result
        """
        # Get analysis
        result = self.analyze_product(product_name)
        
        if not result["success"]:
            return {
                "contains_allergen": False,
                "certainty": "unknown",
                "message": result.get("error", "Product not found")
            }
        
        # Parse allergens from analysis
        analysis_text = result["analysis"].lower()
        allergen_lower = specific_allergen.lower()
        
        contains = allergen_lower in analysis_text
        
        return {
            "product": product_name,
            "allergen": specific_allergen,
            "contains_allergen": contains,
            "certainty": "high" if result["success"] else "unknown",
            "recommendation": "Avoid this product" if contains else "Safe from this allergen",
            "full_analysis_available": True
        }