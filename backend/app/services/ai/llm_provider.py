import json
from dataclasses import asdict

from app.config import get_settings
from app.services.ai.planner import IncidentGroup
from app.services.ai.rule_engine import RuleFinding, analyze_group, derive_risk_level


async def enrich_with_llm(group: IncidentGroup, findings: list[RuleFinding], signals: dict) -> dict | None:
    settings = get_settings()
    if not settings.llm_enabled:
        return None

    context = {
        "signals": signals,
        "findings": [asdict(f) for f in findings],
        "sample_errors": [f.error_message for f in group.failures[:5]],
        "services": sorted(group.service_names),
        "categories": sorted(group.categories),
    }
    prompt = (
        "You are an SRE assistant analyzing production HTTP 500 failures. "
        "Given the operational context below, return JSON with keys: "
        "summary (string), root_cause_hypotheses (array of strings), "
        "recommendations (array of strings), remediation_steps (array of strings), risk_level (low|medium|high|critical).\n\n"
        f"Context:\n{json.dumps(context, indent=2)}"
    )

    try:
        if settings.llm_provider == "openai":
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.llm_api_key)
            model = settings.llm_model or "gpt-4o-mini"
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content or "{}")

        if settings.llm_provider == "anthropic":
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=settings.llm_api_key)
            model = settings.llm_model or "claude-3-5-haiku-latest"
            response = await client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt + "\n\nRespond with valid JSON only."}],
            )
            text = response.content[0].text
            return json.loads(text)
    except Exception:
        return None

    return None


def build_rule_based_report(group: IncidentGroup, findings: list[RuleFinding], signals: dict) -> dict:
    return {
        "summary": (
            f"{len(group.failures)} failures across {', '.join(sorted(group.service_names))} "
            f"({', '.join(sorted(group.categories))})"
        ),
        "root_cause_hypotheses": [f.hypothesis for f in findings],
        "recommendations": [f.recommendation for f in findings],
        "remediation_steps": [
            "Confirm alert thresholds and on-call notification",
            "Inspect recent deployments and config changes",
            "Validate dependency health checks and circuit breaker state",
        ],
        "risk_level": derive_risk_level(group, findings),
        "operational_signals": signals,
    }
