from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
import sys

# Force load settings
from dotenv import load_dotenv
load_dotenv()

def debug_retrieval(query):
    print(f"--- Debugging Query: '{query}' ---")
    
    # Setup Embeddings (Gemini)
    if not settings.GOOGLE_API_KEY or "placeholder" in settings.GOOGLE_API_KEY:
        print("ERROR: Google API Key missing.")
        return

    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=settings.GOOGLE_API_KEY)
        
        # Connect to DB
        vector_store = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=embeddings
        )
        
        # Check Count
        count = vector_store._collection.count()
        print(f"Total Docs in DB: {count}")
        
        if count == 0:
            print("DB IS EMPTY! Ingestion failed.")
            return

        # Perform Search
        results = vector_store.similarity_search_with_score(query, k=3)
        
        print(f"\nTop {len(results)} Results:")
        for i, (doc, score) in enumerate(results):
            print(f"\n[Result {i+1}] (Score: {score:.4f})")
            print(f"Content: {doc.page_content[:200]}...") # Show first 200 chars
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "fees"
    debug_retrieval(q)
