"""Medical Advisor Agent"""
from crewai import Agent, Task
from langchain_community.llms import Ollama
from typing import Dict, List

class MedicalAdvisorAgent:
    """Agent specialized in providing medical advice and alternatives"""
    
    def __init__(self, llm_config: Dict):
        # Create Ollama LLM instance
        llm = Ollama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        self.agent = Agent(
            role='Medical Advisor',
            goal='Provide medical guidance and safe product alternatives',
            backstory="""You are a licensed nutritionist and medical advisor 
            specializing in food allergies and dietary restrictions. You provide 
            evidence-based recommendations and safe alternatives.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_task(self, product_data: Dict, risk_assessment: str, 
                   alternatives: List[Dict], user_profile: Dict = None) -> Task:
        """Create medical advice task"""
        
        alt_text = "\n".join([
            f"- {alt['name']} by {alt['brand']} (Score: {alt['ethical_score']}/10, Allergens: {', '.join(alt['allergens']) if alt['allergens'] else 'None'})"
            for alt in alternatives
        ])
        
        description = f"""Provide medical guidance for this product:

Product: {product_data.get('name', 'Unknown')}

Risk Assessment Summary:
{risk_assessment}

Available Safe Alternatives:
{alt_text}

{f"User Profile: {user_profile}" if user_profile else ""}

Task:
1. Provide clear medical recommendations (consume/avoid/caution)
2. Explain health implications in simple terms
3. Suggest immediate actions if consumed
4. Recommend best alternative products with rationale
5. Provide dietary substitution strategies
6. Suggest preventive measures
7. Indicate when to seek medical attention

Medical Guidance Areas:
- Consumption safety verdict
- What to do if already consumed
- Emergency response plan
- Long-term dietary advice
- Nutritional equivalents
- Lifestyle modifications
- Monitoring recommendations

Output format:
- Medical Verdict: [Safe/Caution/Avoid/Emergency]
- If Consumed: [immediate actions]
- Recommended Alternatives: [ranked with reasons]
- Dietary Advice: [specific guidance]
- Emergency Indicators: [when to call doctor]
- Preventive Measures: [actionable steps]
- Follow-up Recommendations: [monitoring advice]

Note: Always include disclaimer about consulting healthcare providers.
"""
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="Medical recommendations with safe alternatives and action plan"
        )
    
    def advise(self, product_data: Dict, risk_assessment: str, 
              alternatives: List[Dict], user_profile: Dict = None) -> str:
        """Provide medical advice"""
        task = self.create_task(product_data, risk_assessment, alternatives, user_profile)
        return self.agent.execute_task(task)