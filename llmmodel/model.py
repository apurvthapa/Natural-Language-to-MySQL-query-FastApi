from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    api_key=key,
    model="gpt-4.1-mini",
    temperature=0
)