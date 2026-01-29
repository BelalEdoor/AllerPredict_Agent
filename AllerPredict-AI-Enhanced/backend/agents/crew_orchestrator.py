"""CrewAI Orchestrator - Coordinates all agents"""
from crewai import Crew, Process
from typing import Dict, List, Optional
from agents.symptom_analyzer import SymptomAnalyzerAgent
from agents.allergen_predictor import AllergenPredictorAgent
from agents.risk_assessor import RiskAssessorAgent
from agents.medical_advisor import MedicalAdvisorAgent
from rag.pipeline import RAGPipeline

class AllerPredictCrew:
    """Main orchestrator for multi-agent analysis"""
    
    def __init__(self, metadata_path: str = None):
        # LLM Configuration for Ollama
        self.llm_config = {
            "model": "ollama/llama3.2",
            "base_url": "http://localhost:11434",
            "temperature": 0.3
        }
        
        # Initialize RAG pipeline (will use default path if None)
        self.rag = RAGPipeline(metadata_path)
        
        # Initialize agents
        self.symptom_agent = SymptomAnalyzerAgent(self.llm_config)
        self.allergen_agent = AllergenPredictorAgent(self.llm_config)
        self.risk_agent = RiskAssessorAgent(self.llm_config)
        self.medical_agent = MedicalAdvisorAgent(self.llm_config)
    
    def analyze_product(self, query: str, user_profile: Optional[Dict] = None) -> Dict:
        """Complete multi-agent product analysis"""
        
        # Step 1: RAG retrieval
        print("🔍 Searching for product...")
        search_results = self.rag.search(query, top_k=1)
        
        if not search_results:
            return {"error": "Product not found"}
        
        product = search_results[0]
        print(f"✅ Found: {product['name']}")
        
        # Step 2: Symptom Analysis
        print("🧬 Analyzing symptoms...")
        symptom_task = self.symptom_agent.create_task(product, user_profile)
        
        # Step 3: Allergen Prediction
        print("⚠️  Predicting allergens...")
        allergen_task = self.allergen_agent.create_task(product)
        
        # Create crew for parallel execution
        analysis_crew = Crew(
            agents=[self.symptom_agent.agent, self.allergen_agent.agent],
            tasks=[symptom_task, allergen_task],
            process=Process.parallel,
            verbose=True
        )
        
        # Execute parallel analysis
        initial_results = analysis_crew.kickoff()
        symptom_analysis = str(initial_results[0])
        allergen_prediction = str(initial_results[1])
        
        # Step 4: Risk Assessment (depends on previous analyses)
        print("📊 Assessing risk level...")
        risk_task = self.risk_agent.create_task(
            product, symptom_analysis, allergen_prediction, user_profile
        )
        risk_assessment = self.risk_agent.agent.execute_task(risk_task)
        
        # Step 5: Find alternatives
        print("🔄 Finding safe alternatives...")
        alternatives = self.rag.find_alternatives(
            product.get('allergens', []), 
            product['id']
        )
        
        # Step 6: Medical Advice (final synthesis)
        print("⚕️  Generating medical advice...")
        medical_task = self.medical_agent.create_task(
            product, str(risk_assessment), alternatives, user_profile
        )
        medical_advice = self.medical_agent.agent.execute_task(medical_task)
        
        # Compile final report
        report = {
            "product": {
                "name": product['name'],
                "brand": product['brand'],
                "category": product['category'],
                "allergens": product['allergens'],
                "ethical_score": product['ethical_score']
            },
            "analysis": {
                "symptom_analysis": symptom_analysis,
                "allergen_prediction": allergen_prediction,
                "risk_assessment": str(risk_assessment),
                "medical_advice": str(medical_advice)
            },
            "alternatives": alternatives,
            "similarity_score": product.get('similarity_score', 0)
        }
        
        print("✅ Analysis complete!")
        return report
    
    def quick_analyze(self, query: str) -> Dict:
        """Quick analysis without full crew (for faster responses)"""
        search_results = self.rag.search(query, top_k=1)
        
        if not search_results:
            return {"error": "Product not found"}
        
        product = search_results[0]
        analysis = self.rag.analyze_with_llm(product, query)
        alternatives = self.rag.find_alternatives(product.get('allergens', []), product['id'])
        
        return {
            "product": product,
            "analysis": analysis,
            "alternatives": alternatives
        }