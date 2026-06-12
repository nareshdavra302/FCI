from app.schemas.failure import ErrorCategoryEnum


CATEGORY_KEYWORDS: dict[ErrorCategoryEnum, list[str]] = {
    ErrorCategoryEnum.database: [
        "database", "postgres", "mysql", "sql", "connection refused", "pool exhausted",
        "deadlock", "relation does not exist", "db connection",
    ],
    ErrorCategoryEnum.timeout: [
        "timeout", "timed out", "deadline exceeded", "request timeout", "gateway timeout",
    ],
    ErrorCategoryEnum.dependency: [
        "downstream", "dependency", "circuit breaker", "503", "service unavailable",
        "dns", "upstream", "external api",
    ],
    ErrorCategoryEnum.authentication: [
        "auth", "unauthorized", "token expired", "jwt", "forbidden", "401", "403",
        "invalid credentials", "authentication",
    ],
    ErrorCategoryEnum.configuration: [
        "config", "environment", "env var", "missing key", "misconfiguration", "invalid setting",
    ],
}


def categorize_error(error_message: str, stack_trace: str | None = None) -> ErrorCategoryEnum:
    text = f"{error_message} {stack_trace or ''}".lower()
    scores: dict[ErrorCategoryEnum, int] = {cat: 0 for cat in ErrorCategoryEnum if cat != ErrorCategoryEnum.unknown}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] += 1

    if not any(scores.values()):
        return ErrorCategoryEnum.unknown

    return max(scores, key=scores.get)
