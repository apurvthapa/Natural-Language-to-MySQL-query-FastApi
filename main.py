import time
from typing import Any, Dict

from fastapi import FastAPI

from pydantic_validation.validation import input
from helper_function.helper import execution, validate_and_execute_sql
from helper_function.guardrails import pre_llm_guardrails
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message": "Welcome"
    }


@app.get("/health")
def health():

    return {
        "message": "Welcome"
    }


@app.post("/query_to_sql")  
def query_to_sql(request: input):
    start_time = time.time()
    
    guardrail_result = pre_llm_guardrails(request.user_query)

    if not guardrail_result["allowed"]:

        return {
            "query": request.user_query,
            "intent": None,
            "sql_query": None,
            "result": None,
            "message": guardrail_result["message"],
            "execution_time": guardrail_result["execution_time"]
        }

    try:
        result = execution(request.user_query)
    except Exception as error:
        return build_error_response(
            request.user_query,
            f"Query pipeline failed: {str(error)}",
            start_time,
        )

    return result

@app.post("/sql")
def validate(request: input):

    result = validate_and_execute_sql(request.user_query)
    return result


def build_error_response(
    user_query: str,
    message: str,
    start_time: float
) -> Dict[str, Any]:

    return {
        "query": user_query,
        "intent": None,
        "sql_query": None,
        "result": [],
        "success": False,
        "error": message,
        "execution_time": time.time() - start_time
    }


