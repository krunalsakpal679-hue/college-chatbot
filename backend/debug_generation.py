from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
import sys

# Force load settings
from dotenv import load_dotenv
load_dotenv()

def debug_generation(model_name="gemini-pro"):
    print(f"--- Debugging Generation with model: '{model_name}' ---")
    
    if not settings.GOOGLE_API_KEY or "placeholder" in settings.GOOGLE_API_KEY:
        print("ERROR: Google API Key missing.")
        return

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )
        
        print("Attempting to invoke LLM...")
        response = llm.invoke("Hello, are you working?")
        print(f"Response: {response.content}")
        print("SUCCESS: Generation working.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "gemini-pro"
    debug_generation(m)
