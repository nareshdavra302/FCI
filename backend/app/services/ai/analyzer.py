from app.services.ai.llm_provider import build_rule_based_report, enrich_with_llm
from app.services.ai.planner import IncidentGroup, compute_signals
from app.services.ai.rule_engine import analyze_group


async def analyze_incident_group(group: IncidentGroup) -> tuple[dict, str]:
    signals = compute_signals(group)
    findings = analyze_group(group)
    rule_report = build_rule_based_report(group, findings, signals)

    llm_report = await enrich_with_llm(group, findings, signals)
    if llm_report:
        merged = {
            "summary": llm_report.get("summary", rule_report["summary"]),
            "root_cause_hypotheses": llm_report.get("root_cause_hypotheses", rule_report["root_cause_hypotheses"]),
            "recommendations": llm_report.get("recommendations", rule_report["recommendations"]),
            "remediation_steps": llm_report.get("remediation_steps", rule_report["remediation_steps"]),
            "risk_level": llm_report.get("risk_level", rule_report["risk_level"]),
            "operational_signals": signals,
        }
        return merged, "hybrid"

    return rule_report, "rule_engine"
