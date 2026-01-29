"""Allergen Predictor Agent"""
from crewai import Agent, Task
from langchain_community.llms import Ollama
from typing import Dict, List

class AllergenPredictorAgent:
    """Agent specialized in predicting allergen content"""
    
    def __init__(self, llm_config: Dict):
        # Create Ollama LLM instance
        llm = Ollama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        self.agent = Agent(
            role='Allergen Predictor',
            goal='Predict and identify all potential allergens in products',
            backstory="""You are a food science expert specializing in allergen 
            identification. You can detect hidden allergens, cross-contamination 
            risks, and ingredients that commonly trigger allergies.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_task(self, product_data: Dict) -> Task:
        """Create prediction task"""
        ingredients = product_data.get('ingredients', [])
        declared_allergens = product_data.get('allergens', [])
        
        description = f"""Predict all potential allergens in this product:

Product: {product_data.get('name', 'Unknown')}
Brand: {product_data.get('brand', 'Unknown')}
Declared Allergens: {', '.join(declared_allergens)}
Ingredients List: {', '.join(ingredients)}

Task:
1. Verify all declared allergens are accounted for
2. Identify any UNDECLARED allergens from ingredients
3. Check for common cross-contamination risks
4. Identify ingredients with allergen derivatives
5. Flag any vague terms that may hide allergens (e.g., "natural flavors")
6. Assess manufacturing process risks

Categories to check:
- Milk/Dairy products
- Eggs
- Fish/Shellfish
- Tree nuts
- Peanuts
- Wheat/Gluten
- Soybeans
- Sesame
- Sulfites
- Other emerging allergens

Output format:
- Confirmed Allergens: [list]
- Potential Hidden Allergens: [list with sources]
- Cross-Contamination Risk: [Low/Medium/High]
- Vague Ingredients Requiring Clarification: [list]
- Overall Allergen Confidence: [percentage]
"""
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="Complete allergen profile with confidence scores"
        )
    
    def predict(self, product_data: Dict) -> str:
        """Run allergen prediction"""
        task = self.create_task(product_data)
        return self.agent.execute_task(task)