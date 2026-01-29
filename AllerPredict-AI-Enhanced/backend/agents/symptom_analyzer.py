"""Symptom Analyzer Agent"""
from crewai import Agent, Task
from langchain_community.llms import Ollama
from typing import Dict, List

class SymptomAnalyzerAgent:
    """Agent specialized in analyzing allergy symptoms"""
    
    def __init__(self, llm_config: Dict):
        # Create Ollama LLM instance
        llm = Ollama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        self.agent = Agent(
            role='Symptom Analyzer',
            goal='Identify potential allergy symptoms from product ingredients',
            backstory="""You are an expert allergist with 15 years of experience.
            Your specialty is identifying how specific ingredients can trigger 
            allergic reactions and what symptoms to watch for.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_task(self, product_data: Dict, user_profile: Dict = None) -> Task:
        """Create analysis task for this agent"""
        allergens = product_data.get('allergens', [])
        ingredients = product_data.get('ingredients', [])
        
        description = f"""Analyze the following product for potential allergy symptoms:

Product: {product_data.get('name', 'Unknown')}
Allergens: {', '.join(allergens)}
Full Ingredients: {', '.join(ingredients)}

Task:
1. Identify which ingredients are most likely to cause reactions
2. List expected symptoms for each allergen (immediate and delayed)
3. Categorize symptoms by severity (mild, moderate, severe)
4. Note any cross-reactivity concerns
5. Provide timeline of symptom onset

{f"User Profile: Known allergies - {user_profile.get('allergies', [])}" if user_profile else ""}

Output format:
- Primary Concerns: [list]
- Expected Symptoms: [detailed list with timeline]
- Severity Assessment: [Low/Medium/High for each]
- Cross-Reactivity Warnings: [if any]
"""
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="Comprehensive symptom analysis with severity ratings"
        )
    
    def analyze(self, product_data: Dict, user_profile: Dict = None) -> str:
        """Run symptom analysis"""
        task = self.create_task(product_data, user_profile)
        return self.agent.execute_task(task)