from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import pandas as pd
from src.api.schemas import EvaluationRequest, BatchEvaluationRequest
from src.eval.evaluator import EmailAssistantEvaluator

router = APIRouter()

@router.post("/evaluate")
async def evaluate_single(request: EvaluationRequest) -> Dict[str, Any]:
    """Evaluate a single email response"""
    try:
        evaluator = EmailAssistantEvaluator()
        result = evaluator.evaluate_response(
            email=request.email,
            generated_response=request.generated_response,
            ground_truth=request.ground_truth
        )
        return {"success": True, "evaluation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-evaluate")
async def evaluate_batch(request: BatchEvaluationRequest) -> Dict[str, Any]:
    """Evaluate multiple email responses"""
    try:
        evaluator = EmailAssistantEvaluator()
        results = evaluator.run_evaluation_suite(request.test_cases)
        return {"success": True, "results": results.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))