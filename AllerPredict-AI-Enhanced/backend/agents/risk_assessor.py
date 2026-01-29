"""Risk Assessment Agent"""
from crewai import Agent, Task
from langchain_community.llms import Ollama
from typing import Dict

class RiskAssessorAgent:
    """Agent specialized in assessing health risks"""
    
    def __init__(self, llm_config: Dict):
        # Create Ollama LLM instance
        llm = Ollama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        self.agent = Agent(
            role='Risk Assessment Specialist',
            goal='Evaluate overall health risk level of products',
            backstory="""You are a public health specialist with expertise in 
            food safety and risk assessment. You evaluate products based on 
            ingredient safety, allergen severity, and potential health impacts.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_task(self, product_data: Dict, symptom_analysis: str, 
                   allergen_prediction: str, user_profile: Dict = None) -> Task:
        """Create risk assessment task"""
        
        description = f"""Assess the overall risk level for this product:

Product: {product_data.get('name', 'Unknown')}
Ethical Score: {product_data.get('ethical_score', 'N/A')}/10
Certifications: {', '.join(product_data.get('certifications', []))}

Symptom Analysis:
{symptom_analysis}

Allergen Prediction:
{allergen_prediction}

{f"User Known Allergies: {user_profile.get('allergies', [])}" if user_profile else ""}
{f"User Sensitivity Level: {user_profile.get('sensitivity', 'Unknown')}" if user_profile else ""}

Task:
1. Calculate overall risk score (0-100)
2. Categorize risk level (Low/Medium/High/Critical)
3. Identify primary risk factors
4. Assess severity of potential reactions
5. Evaluate product quality and safety standards
6. Consider ethical and manufacturing concerns
7. Provide risk mitigation strategies

Risk Factors to Consider:
- Allergen severity and prevalence
- Symptom seriousness
- Manufacturing quality standards
- Cross-contamination likelihood
- Ingredient transparency
- Company safety record
- Certification credibility

Output format:
- Risk Score: [0-100]
- Risk Level: [Low/Medium/High/Critical]
- Primary Risk Factors: [ranked list]
- Severity Analysis: [detailed]
- Safe for Consumption: [Yes/No/With Precautions]
- Recommended Actions: [list]
"""
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="Comprehensive risk assessment with actionable recommendations"
        )
    
    def assess(self, product_data: Dict, symptom_analysis: str, 
              allergen_prediction: str, user_profile: Dict = None) -> str:
        """Run risk assessment"""
        task = self.create_task(product_data, symptom_analysis, 
                               allergen_prediction, user_profile)
        return self.agent.execute_task(task)