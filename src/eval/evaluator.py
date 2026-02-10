from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import json

class EmailAssistantEvaluator:
    def __init__(self):
        pass
        
    def evaluate_response(
        self,
        email: Dict[str, Any],
        generated_response: str,
        ground_truth: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate a generated email response"""
        
        evaluations = {}
        
        # 3. Custom metrics
        evaluations["custom_metrics"] = self._calculate_custom_metrics(
            email, generated_response
        )
        
        # 4. Hallucination check
        evaluations["hallucination_score"] = self._check_hallucinations(
            generated_response
        )
        
        return evaluations
    
    def _calculate_custom_metrics(
        self,
        email: Dict[str, Any],
        response: str
    ) -> Dict[str, float]:
        """Calculate custom evaluation metrics"""
        metrics = {}
        
        # Response length ratio
        email_length = len(email.get("body", ""))
        response_length = len(response)
        metrics["length_ratio"] = response_length / max(email_length, 1)
        
        # Question answering check
        metrics["question_answered"] = self._check_questions_answered(
            email.get("body", ""), response
        )
        
        # Tone consistency score
        metrics["tone_score"] = self._evaluate_tone_consistency(response)
        
        return metrics
    
    def _check_questions_answered(
        self,
        email_body: str,
        response: str
    ) -> float:
        """Check if questions in email are answered"""
        # Simple implementation - can be enhanced with NLP
        question_indicators = ["?", "can you", "could you", "would you"]
        email_questions = sum(1 for indicator in question_indicators 
                            if indicator in email_body.lower())
        
        if email_questions == 0:
            return 1.0
        
        # Check if response contains answer indicators
        answer_indicators = ["yes", "no", "here is", "attached", "please find"]
        answers_found = sum(1 for indicator in answer_indicators 
                          if indicator in response.lower())
        
        return answers_found / max(email_questions, 1)
    
    def _evaluate_tone_consistency(self, response: str) -> float:
        """Evaluate consistency of tone throughout response"""
        # Simple implementation
        professional_words = ["please", "thank you", "regards", "sincerely"]
        casual_words = ["hey", "hi", "thanks", "cheers"]
        
        professional_count = sum(response.lower().count(word) 
                               for word in professional_words)
        casual_count = sum(response.lower().count(word) 
                          for word in casual_words)
        
        total_words = len(response.split())
        
        if total_words == 0:
            return 0.5
        
        # Score based on consistency (higher if predominantly one style)
        diff = abs(professional_count - casual_count)
        return diff / total_words
    
    def _check_hallucinations(self, response: str) -> float:
        """Check for hallucinations in response"""
        # Implementation using fact-checking or consistency checks
        hallucination_indicators = [
            "I confirm", "as requested", "per our conversation",
            "attached you will find", "I have sent"
        ]
        
        # Simple check - count unsupported assertions
        indicator_count = sum(1 for indicator in hallucination_indicators 
                            if indicator in response.lower())
        
        # Normalize score
        return 1.0 / (1.0 + indicator_count)
    
    def run_evaluation_suite(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Run full evaluation suite on test cases"""
        results = []
        
        for test_case in test_cases:
            evaluation = self.evaluate_response(
                email=test_case["email"],
                generated_response=test_case["generated_response"],
                ground_truth=test_case.get("ground_truth")
            )
            
            # Flatten results
            flat_result = {
                "test_id": test_case["id"],
                "email_subject": test_case["email"].get("subject"),
                **self._flatten_evaluation(evaluation)
            }
            results.append(flat_result)
        
        return pd.DataFrame(results)
    
    def _flatten_evaluation(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten evaluation dictionary"""
        flat = {}
        
        for key, value in evaluation.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    flat[f"{key}_{subkey}"] = subvalue
            else:
                flat[key] = value
        
        return flat
