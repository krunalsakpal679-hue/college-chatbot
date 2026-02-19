import os
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
import asyncio
import time

async def test_model(model_name):
    print(f"\n--- Testing {model_name} ---")
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY
        )
        start = time.time()
        response = await llm.ainvoke("Hello, are you fast?")
        duration = time.time() - start
        print(f"SUCCESS: {model_name} took {duration:.2f}s")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"FAILED: {model_name} Error: {e}")
        return False

async def main():
    models_to_test = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
        "models/gemini-1.5-flash-latest" # Trying a guess
    ]
    
    for m in models_to_test:
        await test_model(m)

if __name__ == "__main__":
    asyncio.run(main())
