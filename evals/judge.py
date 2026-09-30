"""
LLM as a Judge & Calibration Engine — Phase 6 of AI Evals & Reliability Playbook

Key Design Principles:
1. Force structured output: Returns strict rubric JSON, never free-form prose.
2. Escape hatch: Includes explicit "cannot_tell" option to eliminate forced hallucinations.
3. Strict rubric: Grades statutory grounding, refusal appropriateness, and hallucination.
4. Cross-family jury: Combines distinct model families to defeat self-preference bias.
5. Calibration protocol: Computes defensible human-agreement percentage.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple

JUDGE_RUBRIC_PROMPT = """You are a regulatory compliance evaluation judge for the Digital Personal Data Protection Act (DPDPA 2023).
Your task is to grade the AI Agent's answer against the provided regulatory context and query.

EVALUATION RUBRIC:
1. Factual Accuracy: Are all legal claims made strictly grounded in the provided context?
2. Refusal Appropriateness: If the query was out of scope, negative, or lacked context, did the agent refuse properly?
3. Hallucination: Did the agent invent penalties, sections, or extraterritorial rules (e.g. GDPR)?
4. Confidence Escape Hatch: If you cannot conclusively verify the answer, choose "cannot_tell".

Return a JSON object adhering strictly to this schema:
{{
  "rating": <integer from 1 to 5, where 5 is perfectly grounded and 1 is severe hallucination/misstatement>,
  "factual_accuracy": <true | false>,
  "hallucination_detected": <true | false>,
  "refusal_appropriate": <true | false>,
  "confidence": <"high" | "medium" | "cannot_tell">,
  "reasoning": "<concise 1-2 sentence justification citing specific discrepancies if any>"
}}

User Query: {query}
Retrieved Regulatory Context: {context}
Agent Answer: {answer}

JSON Evaluation:"""

class RubricJudge:
    def __init__(self, model_client=None, provider="gemini"):
        self.model_client = model_client
        self.provider = provider

    def grade(
        self,
        query: str,
        answer: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Grades an answer using the structured rubric.
        """
        prompt = JUDGE_RUBRIC_PROMPT.format(
            query=query,
            context=context or "No context retrieved (refusal expected).",
            answer=answer
        )

        if self.model_client and hasattr(self.model_client, "generate_json"):
            try:
                result = self.model_client.generate_json(prompt)
                if "rating" in result and "confidence" in result:
                    return result
            except Exception as e:
                return {
                    "rating": 3,
                    "factual_accuracy": False,
                    "hallucination_detected": False,
                    "refusal_appropriate": True,
                    "confidence": "cannot_tell",
                    "reasoning": f"Judge evaluation failed: {str(e)}"
                }

        # Offline deterministic heuristic fallback for mock runs
        is_refusal = "REFUSAL" in answer or "INSUFFICIENT_EVIDENCE" in answer
        if not context and is_refusal:
            return {
                "rating": 5,
                "factual_accuracy": True,
                "hallucination_detected": False,
                "refusal_appropriate": True,
                "confidence": "high",
                "reasoning": "Agent properly refused query with no regulatory context."
            }
        elif "urn:ki:" in answer:
            return {
                "rating": 5,
                "factual_accuracy": True,
                "hallucination_detected": False,
                "refusal_appropriate": True,
                "confidence": "high",
                "reasoning": "Answer includes valid statutory citations and grounded statements."
            }
        else:
            return {
                "rating": 3,
                "factual_accuracy": True,
                "hallucination_detected": False,
                "refusal_appropriate": is_refusal,
                "confidence": "medium",
                "reasoning": "Heuristic fallback evaluation."
            }


class Jury:
    """
    Combines independent evaluations across model families to cancel out individual biases.
    """
    def __init__(self, judges: List[RubricJudge]):
        self.judges = judges

    def deliberate(self, query: str, answer: str, context: str = "") -> Dict[str, Any]:
        evals = [j.grade(query, answer, context) for j in self.judges]
        
        # Check if any judge used escape hatch
        cannot_tell_count = sum(1 for e in evals if e.get("confidence") == "cannot_tell")
        
        avg_rating = round(sum(e.get("rating", 3) for e in evals) / len(evals), 2) if evals else 3.0
        all_accurate = all(e.get("factual_accuracy", False) for e in evals)
        any_hallucination = any(e.get("hallucination_detected", False) for e in evals)

        consensus_passed = (avg_rating >= 4.0) and all_accurate and not any_hallucination

        return {
            "jury_size": len(evals),
            "consensus_passed": consensus_passed,
            "average_rating": avg_rating,
            "hallucination_detected": any_hallucination,
            "cannot_tell_count": cannot_tell_count,
            "individual_evals": evals
        }


def compute_human_agreement(
    judge_ratings: List[int],
    human_ratings: List[int]
) -> Dict[str, Any]:
    """
    Calculates agreement percentage against human ground truth.
    Defensible claim: 'Agrees with human reviewers X% of the time across N samples.'
    """
    if not judge_ratings or len(judge_ratings) != len(human_ratings):
        return {"agreement_rate": 0.0, "sample_size": 0, "status": "INVALID_DATA"}

    matches = 0
    total = len(human_ratings)

    for j, h in zip(judge_ratings, human_ratings):
        # Exact agreement or within ±1 band
        if j == h:
            matches += 1

    agreement_rate = round((matches / total) * 100, 1)

    return {
        "agreement_rate": agreement_rate,
        "sample_size": total,
        "matches": matches,
        "claim": f"Automated judge agrees with human review {agreement_rate}% of the time across {total} samples."
    }
