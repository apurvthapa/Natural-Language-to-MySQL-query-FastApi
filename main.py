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


@app.post("/query_to_sql")  
def query_to_sql(request: input):
    
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

    result = execution(request.user_query)

    return result

@app.post("/sql")
def validate(request: input):

    result = validate_and_execute_sql(request.user_query)
    return result


