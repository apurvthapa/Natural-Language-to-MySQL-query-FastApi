import time

def pre_llm_guardrails(user_query):
    start_time = time.time()
    user_query = user_query.strip()

    if not user_query:
        return {
            "allowed": False,
            "message": "Empty query",
            "execution_time": time.time() - start_time
        }

    # Very long query protection
    if len(user_query) > 500:
        return {
            "allowed": False,
            "message": "Query too long",
            "execution_time": time.time() - start_time
        }

    lower_query = user_query.lower()

    # Dangerous operations
    blocked_operations = [
        "add",
        "insert",
        "create",
        "update",
        "edit",
        "modify",
        "remove",
        "delete",
        "drop",
        "alter",
        "replace",
        "truncate",
        "rename"
    ]

    for word in blocked_operations:

        if word in lower_query:

            return {
                "allowed": False,
                "message": "Data modification requests are not allowed",
                "execution_time": time.time() - start_time
            }

    # SQL injection keywords
    blocked_sql_keywords = [
        "union select",
        "information_schema",
        "xp_cmdshell",
        "exec(",
        "execute(",
        "shutdown",
        "benchmark("
    ]

    for word in blocked_sql_keywords:

        if word in lower_query:

            return {
                "allowed": False,
                "message": "Unsafe query detected",
                "execution_time": time.time() - start_time
            }

    # SQL comments
    if "--" in user_query or "/*" in user_query:

        return {
            "allowed": False,
            "message": "SQL comments are not allowed",
            "execution_time": time.time() - start_time
        }

    # Multiple statement attempts
    if ";" in user_query:

        return {
            "allowed": False,
            "message": "Multiple statements are not allowed",
            "execution_time": time.time() - start_time
        }

    # Prompt injection attempts
    prompt_injection_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "reveal prompt",
        "act as",
        "jailbreak"
    ]

    for pattern in prompt_injection_patterns:

        if pattern in lower_query:

            return {
                "allowed": False,
                "message": "Prompt injection attempt detected",
                "execution_time": time.time() - start_time
            }


    return {
        "allowed": True,
        "message": "Query passed guardrails"
    }