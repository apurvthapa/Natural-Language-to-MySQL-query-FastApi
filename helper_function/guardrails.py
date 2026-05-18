import re
import time
from typing import Any, Dict


MAX_QUERY_LENGTH = 500
EXECUTION_TIME_PRECISION = 4


BLOCKED_SQL_PATTERNS = re.compile(
    r"(union\s+select|information_schema|xp_cmdshell|shutdown|benchmark\s*\()",
    re.IGNORECASE
)

PROMPT_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+previous\s+instructions|"
    r"ignore\s+all\s+instructions|"
    r"system\s+prompt|"
    r"reveal\s+prompt|"
    r"jailbreak)",
    re.IGNORECASE
)

SQL_COMMENT_PATTERNS = re.compile(
    r"(--|/\*|\*/)"
)

DANGEROUS_SQL_OPERATIONS = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|rename)\b",
    re.IGNORECASE
)


def build_guardrail_response(
    allowed: bool,
    message: str,
    start_time: float
) -> Dict[str, Any]:
    """
    Build standardized guardrail response.
    """

    return {
        "allowed": allowed,
        "message": message,
        "execution_time": round(
            time.perf_counter() - start_time,
            EXECUTION_TIME_PRECISION
        )
    }


def pre_llm_guardrails(user_query: str) -> Dict[str, Any]:
    """
    Validate natural language query before sending it to the LLM.

    Checks:
    - Input type validation
    - Empty query protection
    - Query length restriction
    - Dangerous SQL operation detection
    - SQL injection pattern detection
    - SQL comment detection
    - Prompt injection detection
    """

    start_time = time.perf_counter()

    try:

        # Validate input type
        if not isinstance(user_query, str):
            return build_guardrail_response(
                False,
                "Invalid query format",
                start_time
            )

        cleaned_query = user_query.strip()

        # Empty query check
        if not cleaned_query:
            return build_guardrail_response(
                False,
                "Empty query is not allowed",
                start_time
            )

        # Query length protection
        if len(cleaned_query) > MAX_QUERY_LENGTH:
            return build_guardrail_response(
                False,
                "Query exceeds maximum allowed length",
                start_time
            )

        # Dangerous SQL operation detection
        if DANGEROUS_SQL_OPERATIONS.search(cleaned_query):
            return build_guardrail_response(
                False,
                "Dangerous database operations detected",
                start_time
            )

        # SQL injection pattern detection
        if BLOCKED_SQL_PATTERNS.search(cleaned_query):
            return build_guardrail_response(
                False,
                "Potential SQL injection detected",
                start_time
            )

        # SQL comment detection
        if SQL_COMMENT_PATTERNS.search(cleaned_query):
            return build_guardrail_response(
                False,
                "SQL comments are not allowed",
                start_time
            )

        # Prompt injection detection
        if PROMPT_INJECTION_PATTERNS.search(cleaned_query):
            return build_guardrail_response(
                False,
                "Prompt injection attempt detected",
                start_time
            )

        return build_guardrail_response(
            True,
            "Query passed guardrails",
            start_time
        )

    except Exception as error:

        return build_guardrail_response(
            False,
            f"Guardrail validation failed: {str(error)}",
            start_time
        )


def validate_generated_sql(sql_query: str) -> bool:
    """
    Validate generated SQL before execution.
    Only SELECT queries are allowed.
    """

    if not isinstance(sql_query, str):
        return False

    normalized_query = sql_query.strip().lower()

    # Only SELECT queries allowed
    if not normalized_query.startswith("select"):
        return False

    # Block dangerous SQL operations
    if DANGEROUS_SQL_OPERATIONS.search(normalized_query):
        return False

    return True