import os

from dotenv import load_dotenv
from utils.constants import LLM_MODEL

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def load_llm():

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found."
        )

    return ChatGoogleGenerativeAI(

        model=LLM_MODEL,

        google_api_key=api_key

    )

    