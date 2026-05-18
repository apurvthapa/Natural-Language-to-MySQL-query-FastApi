from langchain_core.prompts import ChatPromptTemplate
from llmmodel.model import llm
from schemas.tables import schema_dict
from mysqldatabase.connection import readonly_engine
import re
import time
import pandas as pd
import ast
from typing import Any, Dict, List

def intent_finder(user_query: str) -> List[str]:
    """
    Identify relevant database tables required to answer the user query.

    Uses an LLM-based intent classifier to determine which tables
    are needed for query generation while enforcing read-only access rules.

    Args:
        user_query: Natural language query provided by the user.

    Returns:
        List of relevant table names.
    """

    intent_prompt = ChatPromptTemplate.from_template("""
You are an expert database intent classifier.

Identify which tables are needed to answer the user query.

Tables:

- shipments
  Shipment, cargo, delay and status data

- ports
  Port, country and region data

- ships
  Ship, vessel, operator and capacity data

Semantic rules:
- Routes/source port/destination port/ports/regions -> ports
- Port country/location -> ports
- Delays/cargo/status/shipment activity -> shipments
- Ships/vessels/operators/capacity/ship origin country -> ships
- Ship country/operator country/vessel country -> ships

Security rules:
- If the user asks to add, insert, create, update, edit, modify, remove, delete, drop, alter, replace, change, truncate or manipulate data/schema in any way, return []
- Only allow read/query/analysis type requests

Rules:
- Return ONLY a valid Python list
- No explanation
- Return [] if unrelated

Examples:

Top delayed routes
["shipments", "ports"]

Average delay by vessel type
["shipments", "ships"]

Who won IPL 2025
[]

Add ship name 'apurv' to ships table
[]

Delete all delayed shipments
[]

Update operator company for ship 10
[]


User Query:
{user_query}
""")

# Create final prompt
    final_intent_prompt = intent_prompt.format_messages(
        user_query=user_query
        )

    response = llm.invoke(final_intent_prompt)

    tables = ast.literal_eval(response.content)

    return tables

def final_solution(
    intent: List[str],
    user_query: str
) -> Dict[str, Any]:
    """
    Generate SQL query from user intent and execute it on the database.

    Workflow:
    - Validate identified table intent
    - Build schema context dynamically
    - Generate SQL using LLM
    - Execute query using read-only database engine
    - Return structured API response

    Args:
        intent: List of relevant database tables.
        user_query: Natural language query provided by the user.

    Returns:
        Dictionary containing generated SQL query,
        detected intent, and query results.
    """

    final_schema = ''

    # CHANGE 1:
    # Cleaner unrelated query response
    if len(intent) == 0:

        return {
            'query': user_query,
            'intent': None,
            'sql_query': None,
            'result': "Query cannot be answered using the available database"
        }

    else:

        # Existing schema retrieval
        for i in intent:
            final_schema += schema_dict[i] + '\n'

        prompt = ChatPromptTemplate.from_template("""

You are an expert MySQL query generator.

Generate ONLY valid MySQL SQL queries.

Rules:
- ONLY generate SELECT queries
- NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER
- Do not explain anything
- Do not use markdown
- Use proper JOINs using foreign keys
- Use aliases for tables
- Use LIMIT for top/bottom queries
- NEVER generate placeholder queries like SELECT NULL
- NEVER generate dummy values
- If required columns do not exist, return exactly:
INVALID_QUERY

Semantic Interpretation Rules:
- "ships" refers to ship/vessel entities from ships table
- "shipment origin/destination/source port" refers to ports table
- "country of ships" means ships.origin_country
- "country of ports" means ports.country
- "routes" means shipment source and destination ports
- "delayed ships" means ships associated with delayed shipments
- "number of delayed ships" means count delayed shipments unless explicitly asking for unique ships
- Use COUNT(*) for shipment/event counts
- Use COUNT(DISTINCT ship_id) only when explicitly asking for unique ships/vessels
- If source/destination is ambiguous, prefer destination analysis                                                 
Database Schema:
{schema}

User Question:
{user_query}

""")

        final_prompt = prompt.format_messages(
            schema=final_schema,
            user_query=user_query
        )

        # Generate SQL
        response = llm.invoke(final_prompt)

        sql_query = response.content.strip()

        # CHANGE 2:
        # Add exception handling
        try:

            df = pd.read_sql(
                sql_query,
                readonly_engine
            )

            # CHANGE 3:
            # Convert dataframe for FastAPI JSON response
            result_data = df.to_dict(orient="records")

            return {
                'query': user_query,
                'intent': intent,
                'sql_query': sql_query,

                # CHANGE 4:
                # renamed from 'correct'
                'result': result_data
            }

        except Exception as e:

            return {
                'query': user_query,
                'intent': intent,
                'sql_query': sql_query,
                'error': str(e)
            }
    
def execution(user_query: str) -> Dict[str, Any]:
    """
    Execute the complete NL-to-SQL pipeline.

    Workflow:
    - Identify relevant database tables
    - Generate SQL query
    - Execute query on database
    - Measure total execution time

    Args:
        user_query: Natural language query provided by the user.

    Returns:
        Dictionary containing query details,
        generated SQL, execution results,
        and total execution time.
    """
    start_time = time.time()
    user_intent = intent_finder(user_query)
    result = final_solution(intent = user_intent, user_query = user_query)
    end_time = time.time()
    result['execution_time']= end_time - start_time
    return result

def validate_and_execute_sql(sql_query: str) -> Dict[str, Any]:
    """
    Validate generated SQL query and execute it safely
    using a read-only database connection.

    Validation Checks:
    - Empty query protection
    - SELECT-only query enforcement
    - Dangerous SQL keyword blocking
    - SQL comment blocking
    - Multiple statement prevention

    Args:
        sql_query: SQL query generated by the LLM.

    Returns:
        Dictionary containing execution status,
        SQL query, query results, and metadata.
    """
    try:

        sql_query = sql_query.strip().rstrip(";")

        if not sql_query:
            return {
                "success": False,
                "error": "Empty SQL query"
            }

        upper_sql = sql_query.upper()

        # Only SELECT queries allowed
        if not upper_sql.startswith("SELECT"):
            return {
                "success": False,
                "error": "Only SELECT queries are allowed"
            }

        # Block dangerous keywords
        blocked_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "REPLACE",
            "MERGE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
            "CALL"
        ]

        for keyword in blocked_keywords:

            if re.search(rf"\b{keyword}\b", upper_sql):

                return {
                    "success": False,
                    "error": f"Blocked SQL keyword detected: {keyword}"
                }

        # Block SQL comments / injections
        if "--" in sql_query or "/*" in sql_query:

            return {
                "success": False,
                "error": "SQL comments are not allowed"
            }

        # Block multiple statements
        if ";" in sql_query:

            return {
                "success": False,
                "error": "Multiple SQL statements are not allowed"
            }

        # Execute query
        df = pd.read_sql(sql_query, readonly_engine)

        result_data = df.to_dict(orient="records")

        return {
            "success": True,
            "sql_query": sql_query,
            "result": result_data,
            "row_count": len(df)
        }

    except Exception as e:

        return {
            "success": False,
            "sql_query": sql_query,
            "error": str(e)
        }