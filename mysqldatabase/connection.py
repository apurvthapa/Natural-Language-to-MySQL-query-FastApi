from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

READ_ONLY_URL = os.getenv("READ_ONLY_URL")

readonly_engine = create_engine(
    READ_ONLY_URL,
    pool_pre_ping=True
)