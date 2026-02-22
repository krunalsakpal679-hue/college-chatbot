import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def test_local():
    print("==========================================")
    print("🧪 KPGU BOT - INTERNAL VERIFICATION")
    print("==========================================\n")

    try:
        from backend.app.services.rag_service import rag_service
        from backend.app.schemas.chat import ChatRequest
        
        print("1. Initializing AI Engine (Wait 5s)...")
        rag_service.initialize()
        await asyncio.sleep(5)
        
        print(f"2. Testing Query: 'What is the fees of CSE?'")
        req = ChatRequest(query="What is the fees of CSE?")
        resp = await rag_service.generate_response(req)
        
        print(f"\n3. BOT RESPONSE:")
        print("-" * 40)
        print(resp.response)
        print("-" * 40)
        
        if "fees" in resp.response.lower() or "records" in resp.response.lower():
            print("\n✅ SUCCESS: Backend is generating professional answers!")
        else:
            print("\n⚠️ WARNING: Response seems incomplete. Check data files.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Make sure you are in the 'college-chatbot' folder and 'venv' is activated.")

if __name__ == "__main__":
    asyncio.run(test_local())
