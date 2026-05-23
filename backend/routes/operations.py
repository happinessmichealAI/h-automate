"""
H-Automate — operations.py
Smart Operations API route — handles business problem analysis.

Endpoint: POST /api/operations
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq_client import client


router = APIRouter()


# ─────────────────────────────────────────────
# REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────
class OperationsRequest(BaseModel):
    """Request model for operations analysis"""
    problem_description: str
    business_type: str


class OperationsResponse(BaseModel):
    """Response model for operations analysis"""
    status: str
    situation_summary: str
    likely_causes: list
    recommended_actions: list
    workflow: list
    expected_outcome: str


# ─────────────────────────────────────────────
# OPERATIONS SYSTEM PROMPT
# ─────────────────────────────────────────────
OPERATIONS_SYSTEM_PROMPT = """
You are a business operations consultant specializing in Nigerian SMEs.

Your job is to analyze operational challenges and provide practical, actionable solutions
that a small business owner can implement without technology or significant capital.

STRICT RULES:
1. Keep language simple — no jargon like "KPIs", "synergy", "leverage"
2. All recommendations must be implementable with basic tools (notebook, phone, WhatsApp)
3. Never suggest building software systems or quote implementation costs
4. Reference Nigerian market realities (cash-dominant, informal markets, supply chain challenges)
5. Each workflow step must specify WHEN and WHAT exactly
6. Expected outcomes must be realistic — no fake precision like "increase sales by 37%"
7. Actions must be tiered: Easy / Medium / Hard difficulty
8. Every recommendation must be specific to the problem described

WORKFLOW RULES:
- Each step must be completable in under 10 minutes
- Specify exact timing (daily, every Monday, every Sunday evening)
- Use simple operational habits, not technology solutions

OUTCOME RULES:
- Never promise specific percentage increases unless evidence-backed
- Use phrases like "may improve", "likely to reduce", "could help"
- Acknowledge uncertainty where appropriate
"""


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def build_operations_prompt(business_type: str, problem_description: str) -> str:
    """Build user prompt for operations analysis"""
    return f"""
A {business_type} owner in Nigeria has described this operational challenge:

"{problem_description}"

Provide a structured operational analysis in this exact format:

---
SITUATION SUMMARY
[2-3 sentences understanding the problem from the owner's perspective.
Show empathy and acknowledge the challenge.]

---
LIKELY CAUSES
[3-5 numbered causes. Each must have:
- A clear title
- 2-3 sentences explaining why this might be happening
- Reference to Nigerian market context where relevant]

1. [Cause Title]
   [Explanation]

2. [Cause Title]
   [Explanation]

---
RECOMMENDED ACTIONS
[3-5 actions, each with difficulty level. Format:]

Action 1: [Title]
Difficulty: [Easy / Medium / Hard]
Why it matters: [2-3 sentences]
How to do it: [Specific steps]

Action 2: [Title]
Difficulty: [Easy / Medium / Hard]
Why it matters: [2-3 sentences]
How to do it: [Specific steps]

---
SUGGESTED WORKFLOW
[4-6 step timeline. Each step must specify WHEN and WHAT.]

Step 1: [When] — [What to do]
Step 2: [When] — [What to do]
Step 3: [When] — [What to do]
Step 4: [When] — [What to do]

---
EXPECTED BUSINESS OUTCOME
[2-3 sentences describing realistic expected results.
Use cautious language: "may improve", "likely to", "could help".
Never promise specific percentages unless evidence-backed.
Acknowledge that results depend on consistent execution.]

---
IMPORTANT NOTE
End with: "These recommendations are based on common operational patterns in Nigerian SMEs.
Results will vary based on your specific circumstances, market conditions, and consistency
of implementation. Start with the easiest actions first and adjust based on what works."
"""


def validate_business_type(business_type: str) -> str:
    """Validate and normalize business type"""
    valid_types = ["mini-mart", "pharmacy", "pos-agent", "restaurant", "fashion-store"]
    
    business_type = business_type.lower().strip()
    
    if business_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid business type. Must be one of: {', '.join(valid_types)}"
        )
    
    return business_type


def parse_operations_response(response_text: str) -> dict:
    """Parse structured operations response into JSON"""
    sections = {
        "situation_summary": "",
        "likely_causes": [],
        "recommended_actions": [],
        "workflow": [],
        "expected_outcome": ""
    }
    
    # Split by section headers
    parts = response_text.split("---")
    
    for part in parts:
        part = part.strip()
        
        if part.startswith("SITUATION SUMMARY"):
            sections["situation_summary"] = part.replace("SITUATION SUMMARY", "").strip()
        
        elif part.startswith("LIKELY CAUSES"):
            causes_text = part.replace("LIKELY CAUSES", "").strip()
            # Split by numbered items
            causes = []
            for line in causes_text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    causes.append(line)
            sections["likely_causes"] = causes
        
        elif part.startswith("RECOMMENDED ACTIONS"):
            actions_text = part.replace("RECOMMENDED ACTIONS", "").strip()
            # Parse action blocks
            actions = []
            current_action = {}
            for line in actions_text.split("\n"):
                line = line.strip()
                if line.startswith("Action"):
                    if current_action:
                        actions.append(current_action)
                    current_action = {"title": line}
                elif line.startswith("Difficulty:"):
                    current_action["difficulty"] = line.replace("Difficulty:", "").strip()
                elif line.startswith("Why it matters:"):
                    current_action["why"] = line.replace("Why it matters:", "").strip()
                elif line.startswith("How to do it:"):
                    current_action["how"] = line.replace("How to do it:", "").strip()
            if current_action:
                actions.append(current_action)
            sections["recommended_actions"] = actions
        
        elif part.startswith("SUGGESTED WORKFLOW"):
            workflow_text = part.replace("SUGGESTED WORKFLOW", "").strip()
            steps = []
            for line in workflow_text.split("\n"):
                line = line.strip()
                if line and (line.startswith("Step") or line.startswith("-")):
                    steps.append(line)
            sections["workflow"] = steps
        
        elif part.startswith("EXPECTED BUSINESS OUTCOME"):
            sections["expected_outcome"] = part.replace("EXPECTED BUSINESS OUTCOME", "").strip()
    
    return sections


# ─────────────────────────────────────────────
# MAIN OPERATIONS ENDPOINT
# ─────────────────────────────────────────────
@router.post("/operations")
async def analyze_operations(request: OperationsRequest):
    """
    Analyze a business operational challenge and provide recommendations.
    
    Parameters:
        problem_description: Description of the business challenge
        business_type: One of: mini-mart, pharmacy, pos-agent, restaurant, fashion-store
    
    Returns:
        JSON with situation summary, causes, actions, workflow, and expected outcome
    """
    
    # Validate inputs
    if not request.problem_description or len(request.problem_description.strip()) < 10:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Please provide a detailed description of your business challenge (at least 10 characters)."
            }
        )
    
    business_type = validate_business_type(request.business_type)
    
    # Build prompt
    user_prompt = build_operations_prompt(business_type, request.problem_description)
    
    # Call Groq API
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.5,  # Slightly higher for more creative solutions
            messages=[
                {"role": "system", "content": OPERATIONS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response_text = response.choices[0].message.content
        
        # Parse response into structured format
        parsed = parse_operations_response(response_text)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "business_type": business_type,
                "problem_description": request.problem_description,
                **parsed,
                "raw_response": response_text  # Include full response for debugging
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error_type": "ai_unavailable",
                "message": "Analysis is taking longer than expected. Please try again shortly.",
                "details": str(e)
            }
        )


# ─────────────────────────────────────────────
# HEALTH CHECK FOR OPERATIONS ROUTE
# ─────────────────────────────────────────────
@router.get("/operations/health")
def operations_health():
    """Check if operations endpoint is ready"""
    return {
        "status": "ok",
        "endpoint": "/api/operations",
        "methods": ["POST"]
    }

# Made with Bob
