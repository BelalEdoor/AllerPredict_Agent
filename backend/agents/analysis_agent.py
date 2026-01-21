"""
Simplified Analysis Agent
Clear, easy-to-understand AI agent for product safety analysis
"""
from crewai import Agent
from langchain_community.llms import Ollama

class SafetyAnalysisAgent:
    """
    Creates and manages the Product Safety Analyst agent
    Simple and focused on accuracy
    """
    
    @staticmethod
    def create(analysis_tool):
        """
        Create the safety analyst agent
        
        Args:
            analysis_tool: The product analysis tool
            
        Returns:
            Agent: Configured safety analyst
        """
        # Create AI language model
        ai_model = Ollama(
            model="mistral",
            temperature=0.3  # Lower temperature = more focused and accurate
        )
        
        return Agent(
            role="Product Safety Analyst",
            
            goal="Find and analyze food products to identify allergens, safety risks, and provide accurate health information",
            
            backstory="""You are a professional food safety expert who helps people stay safe.

Your expertise includes:
- Identifying all types of food allergens (nuts, dairy, gluten, soy, eggs, etc.)
- Understanding ingredient lists and food labels
- Assessing risk levels for people with allergies
- Providing clear, accurate safety information

You always:
1. Search the database carefully to find the exact product
2. List ALL allergens clearly
3. Explain risks in simple language
4. Be honest if information is missing or uncertain

Your priority is keeping people safe through accurate information.""",
            
            tools=[analysis_tool],
            verbose=True,
            allow_delegation=True,
            llm=ai_model
        )
    
    @staticmethod
    def create_task(agent, product_name):
        """
        Create a clear analysis task
        
        Args:
            agent: The safety analyst agent
            product_name: Product to analyze
            
        Returns:
            dict: Task configuration
        """
        return {
            "description": f"""
TASK: Analyze this product for safety: "{product_name}"

STEPS TO FOLLOW:
1. Use the Product Safety Analysis Tool to search for: {product_name}
2. Carefully read all the information returned
3. Create a clear safety report

YOUR REPORT MUST INCLUDE:

✅ PRODUCT IDENTIFICATION
- Exact product name
- Brand name
- Product category

⚠️ ALLERGEN INFORMATION
- List EVERY allergen found (be complete and accurate)
- If no allergens: clearly state "No allergens detected"
- Explain what each allergen means

📊 RISK ASSESSMENT
- Risk level: Low, Medium, or High
- Explain WHY this risk level was assigned
- Mention any "may contain" warnings

🌍 ETHICAL INFORMATION
- Ethical score (0-100)
- Explain the score
- Mention any concerns or positive factors

⚠️ IMPORTANT RULES:
- Do NOT make up information
- If the product is not found, say so clearly
- If information is missing, state that clearly
- Always prioritize accuracy over completeness
""",
            
            "expected_output": """
A complete safety report with:
1. Product identification (name, brand, category)
2. Complete allergen list with explanations
3. Risk level with clear reasoning
4. Ethical score with explanation
5. Any warnings or important notes
"""
        }


class RecommendationAgent:
    """
    Creates and manages the Recommendation Specialist agent
    Suggests safer alternatives
    """
    
    @staticmethod
    def create():
        """
        Create the recommendation specialist agent
        
        Returns:
            Agent: Configured recommendation specialist
        """
        ai_model = Ollama(
            model="mistral",
            temperature=0.5  # Slightly creative for recommendations
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
1. Suggest 2-4 specific alternative products when possible
2. Explain WHY each alternative is better
3. Consider both safety AND ethics
4. Give practical advice people can actually use

Your goal is helping people make better, safer choices.""",
            
            verbose=True,
            allow_delegation=False,
            llm=ai_model
        )
    
    @staticmethod
    def create_task(agent, safety_analysis):
        """
        Create a recommendation task
        
        Args:
            agent: The recommendation agent
            safety_analysis: Results from safety analysis
            
        Returns:
            dict: Task configuration
        """
        return {
            "description": f"""
TASK: Create helpful recommendations based on this safety analysis:

{safety_analysis}

YOUR RECOMMENDATIONS MUST INCLUDE:

📋 SAFETY SUMMARY
- Quickly summarize the main safety concerns
- Highlight the most important allergens or risks
- Use simple, clear language

💡 ALTERNATIVE PRODUCTS (2-4 suggestions)
- Suggest specific safer alternatives
- For each alternative, explain:
  * Why it's safer (e.g., "dairy-free", "nut-free")
  * Why it's more ethical (if applicable)
  * Where to find it (if you know)

🛒 SHOPPING TIPS
- What to look for on labels
- What ingredients/warnings to avoid
- How to shop more safely

✅ FINAL RECOMMENDATION
- Should they avoid this product? (Yes/No/With Caution)
- Overall safety rating (1-5 stars)
- One-sentence summary

⚠️ IMPORTANT RULES:
- Be specific with product names when possible
- If no alternatives are in the database, give general guidance
- Always explain your reasoning
- Be helpful and practical
""",
            
            "expected_output": """
A helpful recommendation report with:
1. Clear safety summary
2. 2-4 specific alternative products with explanations
3. Practical shopping tips
4. Final recommendation and rating
"""
        }