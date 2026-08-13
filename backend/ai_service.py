import json
import os
import re
from typing import Dict, Any

import httpx


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()

    # Remove markdown code fences if the model returns them.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found")

    return json.loads(match.group(0))


# -------------------------------------------------------------------
# FALLBACK ENTERPRISE PROCESS SCORING ENGINE
# -------------------------------------------------------------------

def _fallback_analysis(
    name: str,
    industry: str,
    description: str
) -> Dict[str, Any]:

    text = f"{name} {industry} {description}".lower()

    # Strong indicators of AI/automation suitability.
    automation_keywords = {
        "forecast": 10,
        "prediction": 10,
        "classification": 9,
        "routing": 9,
        "scheduling": 8,
        "reconciliation": 8,
        "monitoring": 8,
        "tracking": 7,
        "reporting": 7,
        "inventory": 8,
        "claims": 8,
        "billing": 8,
        "fraud": 10,
        "maintenance": 8,
        "quality": 7,
        "processing": 6,
        "analysis": 7,
        "planning": 8,
        "customer service": 7,
        "support": 6,
        "document": 6,
        "extraction": 9,
        "validation": 6,
        "optimization": 10,
        "optimisation": 10,
        "recommendation": 9,
        "anomaly": 10,
        "detection": 8,
        "triage": 8,
        "workload": 6,
        "allocation": 7,
        "procurement": 7,
        "invoice": 7,
        "payment": 6,
        "compliance reporting": 6,
    }

    # Indicators that humans should remain heavily involved.
    human_keywords = {
        "clinical": 15,
        "medical": 15,
        "diagnostic": 18,
        "diagnosis": 18,
        "patient": 14,
        "safety": 18,
        "incident": 14,
        "investigation": 12,
        "regulatory": 15,
        "legal": 16,
        "compliance": 12,
        "risk": 10,
        "approval": 10,
        "discharge": 12,
        "emergency": 18,
        "ethical": 18,
        "high impact": 15,
        "human judgement": 15,
        "human judgment": 15,
    }

    # Indicators of high business benefit.
    benefit_keywords = {
        "high volume": 12,
        "volume": 7,
        "repetitive": 12,
        "manual": 10,
        "delay": 8,
        "delays": 8,
        "cost": 8,
        "expensive": 8,
        "error": 10,
        "errors": 10,
        "inconsistent": 9,
        "scalability": 10,
        "scalable": 10,
        "real-time": 10,
        "real time": 10,
        "customer": 6,
        "revenue": 9,
        "productivity": 10,
        "efficiency": 10,
    }

    def keyword_score(keywords: Dict[str, int]) -> int:
        score = 0

        for keyword, weight in keywords.items():
            if keyword in text:
                score += weight

        return min(score, 100)

    automation_hits = keyword_score(automation_keywords)
    human_hits = keyword_score(human_keywords)
    benefit_hits = keyword_score(benefit_keywords)

    # Base scores prevent everything from clustering around the same value.
    automation_score = min(95, 30 + automation_hits)

    benefit_score = min(
        95,
        40 + benefit_hits + round(automation_hits * 0.25)
    )

    human_criticality_score = min(
        95,
        25 + human_hits
    )

    # Processes with strong human-criticality should have lower
    # autonomous automation potential, while still allowing AI
    # decision support.
    effective_automation = max(
        0,
        automation_score - round(human_criticality_score * 0.35)
    )

    ai_score = round(
        (effective_automation * 0.45)
        + (benefit_score * 0.35)
        + ((100 - human_criticality_score) * 0.20),
        2
    )

    # Classify opportunity.
    if ai_score >= 68:
        potential = "High"
    elif ai_score >= 48:
        potential = "Medium"
    else:
        potential = "Low"

    # More specific opportunity description.
    opportunity_parts = []

    if any(k in text for k in ["forecast", "prediction"]):
        opportunity_parts.append("predictive forecasting")

    if any(k in text for k in ["fraud", "anomaly", "detection"]):
        opportunity_parts.append("anomaly and fraud detection")

    if any(k in text for k in ["document", "invoice", "extraction"]):
        opportunity_parts.append("document intelligence and information extraction")

    if any(k in text for k in ["classification", "routing", "triage"]):
        opportunity_parts.append("classification and intelligent routing")

    if any(k in text for k in ["optimization", "optimisation", "planning", "scheduling"]):
        opportunity_parts.append("optimization and decision support")

    if any(k in text for k in ["monitoring", "tracking"]):
        opportunity_parts.append("continuous monitoring and exception detection")

    if not opportunity_parts:
        opportunity_parts.append(
            "workflow automation, analytics and decision support"
        )

    opportunity = (
        f"AI can support {name.lower()} through "
        + ", ".join(opportunity_parts)
        + "."
    )

    # Human involvement statement.
    if human_criticality_score >= 60:
        human_involvement = (
            "Humans should retain primary accountability for high-impact "
            "decisions, exceptions, judgement-heavy cases, regulatory "
            "requirements and final approval. AI should primarily provide "
            "decision support rather than fully autonomous execution."
        )
    else:
        human_involvement = (
            "Humans should oversee exceptions, monitor model performance "
            "and retain accountability for material business decisions, "
            "while routine activities can be automated."
        )

    # Technologies.
    technologies = (
        "Machine learning, LLMs, information retrieval, "
        "workflow automation, predictive analytics and anomaly detection."
    )

    return {
        "business_purpose": (
            f"Execute {name.lower()} effectively within the "
            f"{industry.lower()} enterprise."
        ),

        "key_activities": (
            f"Capture relevant inputs; validate information; execute the "
            f"core {name.lower()} workflow; monitor exceptions; record "
            f"outcomes; communicate results."
        ),

        "current_challenges": (
            "Manual effort, inconsistent decisions, fragmented information, "
            "processing delays, exception handling and limited visibility "
            "can reduce operational efficiency."
        ),

        "ai_opportunity": opportunity,

        "automation_potential": potential,

        "human_involvement": human_involvement,

        "technologies": technologies,

        "business_benefit": (
            "Potential benefits include reduced processing time, lower "
            "operating cost, improved consistency, better scalability, "
            "higher service quality and stronger decision support."
        ),

        "risks": (
            "Model errors, biased data, weak explainability, "
            "privacy/security exposure, automation bias and inadequate "
            "human oversight."
        ),

        "ai_score": float(ai_score),
        "automation_score": float(automation_score),
        "benefit_score": float(benefit_score),
        "human_criticality_score": float(human_criticality_score),

        "reasoning": (
            f"Score derived from process characteristics. "
            f"Automation suitability={automation_score}/100, "
            f"business benefit={benefit_score}/100, "
            f"human criticality={human_criticality_score}/100. "
            f"The final AI opportunity score is {ai_score}/100, "
            f"balancing automation potential, business benefit and "
            f"the need for human judgement."
        ),
    }


# -------------------------------------------------------------------
# OPTIONAL OLLAMA AI ANALYSIS
# -------------------------------------------------------------------

async def analyze_with_ai(
    name: str,
    industry: str,
    description: str,
    evidence
) -> Dict[str, Any]:

    # Use the deterministic enterprise scoring engine by default.
    if os.getenv("OLLAMA_ENABLED", "false").lower() != "true":
        return _fallback_analysis(name, industry, description)

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:3b"
    )

    evidence_text = "\n".join(
        f"- {e['title']}: {e['snippet']} ({e['url']})"
        for e in evidence[:5]
    )

    prompt = f"""
You are an enterprise process intelligence analyst.

Industry:
{industry}

Process:
{name}

Description:
{description}

Evidence:
{evidence_text}

Analyze the process for AI-enabled transformation.

Consider:

1. Process automation potential
2. Predictive analytics opportunities
3. Document/information extraction
4. Classification and routing
5. Business value
6. Operational complexity
7. Human judgement requirements
8. Regulatory and safety considerations
9. AI implementation risks
10. Suitable AI technologies

Return ONLY valid JSON with exactly these fields:

business_purpose,
key_activities,
current_challenges,
ai_opportunity,
automation_potential,
human_involvement,
technologies,
business_benefit,
risks,
ai_score,
automation_score,
benefit_score,
human_criticality_score,
reasoning

automation_potential must be:
Low, Medium, or High.

All scores must be numbers from 0 to 100.

ai_score should balance:
- automation potential
- business benefit
- human criticality

Higher human criticality should reduce the suitability for fully autonomous automation.
"""

    print(f"[AI] Using Ollama model: {model}")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )

            response.raise_for_status()

            result = _extract_json(
                response.json()["response"]
            )

            print(f"[AI] Ollama analysis successful for: {name}")
            return result

    except Exception as exc:
        print(f"[AI] Ollama failed for {name}: {exc}")
        print("[AI] Using deterministic fallback engine.")

        return _fallback_analysis(
            name,
            industry,
            description,
        )