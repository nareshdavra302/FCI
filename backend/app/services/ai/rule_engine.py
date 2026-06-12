from dataclasses import dataclass

from app.services.ai.planner import IncidentGroup


@dataclass
class RuleFinding:
    pattern: str
    hypothesis: str
    recommendation: str
    confidence: str


def analyze_group(group: IncidentGroup) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    services = group.service_names
    categories = group.categories
    count = len(group.failures)

    if "database" in categories and len(services) == 1:
        service = next(iter(services))
        findings.append(
            RuleFinding(
                pattern="database_burst_single_service",
                hypothesis=f"Connection pool exhaustion or database unreachable on {service}",
                recommendation="Check database health, connection limits, and recent migrations",
                confidence="high",
            )
        )

    if "timeout" in categories and len(services) >= 2:
        findings.append(
            RuleFinding(
                pattern="timeout_multi_service",
                hypothesis="Shared dependency or gateway degradation affecting multiple services",
                recommendation="Inspect upstream gateway, load balancer, and shared infrastructure",
                confidence="high",
            )
        )

    if "authentication" in categories:
        findings.append(
            RuleFinding(
                pattern="authentication_spike",
                hypothesis="Token or auth configuration regression, possibly after a deployment",
                recommendation="Verify JWT secrets, roll back recent deployment if correlated",
                confidence="medium",
            )
        )

    if "dependency" in categories and services == {"service-c"}:
        findings.append(
            RuleFinding(
                pattern="dependency_service_c",
                hypothesis="External API outage or circuit breaker open on service-c",
                recommendation="Enable circuit breaker fallback and verify downstream SLA",
                confidence="high",
            )
        )

    if "configuration" in categories:
        findings.append(
            RuleFinding(
                pattern="configuration_error",
                hypothesis="Missing or invalid environment configuration",
                recommendation="Audit environment variables and config maps for affected services",
                confidence="medium",
            )
        )

    if len(services) >= 2 and count >= 3:
        findings.append(
            RuleFinding(
                pattern="cascading_failure",
                hypothesis=f"Cascading failure across {', '.join(sorted(services))}",
                recommendation="Trace root service and inspect shared infrastructure (DB, cache, network)",
                confidence="medium",
            )
        )

    if not findings:
        findings.append(
            RuleFinding(
                pattern="unknown_pattern",
                hypothesis="Insufficient pattern match; failures may be isolated or novel",
                recommendation="Review individual failure logs and recent deployments",
                confidence="low",
            )
        )

    return findings


def derive_risk_level(group: IncidentGroup, findings: list[RuleFinding]) -> str:
    count = len(group.failures)
    high_confidence = any(f.confidence == "high" for f in findings)

    if count >= 10 or (len(group.service_names) >= 2 and high_confidence):
        return "critical"
    if count >= 5 or high_confidence:
        return "high"
    if count >= 2:
        return "medium"
    return "low"
