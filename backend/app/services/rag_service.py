from app.schemas.chat import ChatRequest, ChatResponse
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tenacity import retry,  stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions
from app.core.config import settings

class RAGService:
    def __init__(self):
        # Initialize Core Components
        self.openai_key = settings.OPENAI_API_KEY
        self.google_key = settings.GOOGLE_API_KEY
        self.db_dir = settings.CHROMA_DB_DIR
        self.vector_store = None
        self.retriever = None
        self.llm = None
        
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initializes the LLM and Vector Store."""
        use_gemini = False
        
        # Check available keys
        if (not self.openai_key or "placeholder" in self.openai_key) and (self.google_key and "placeholder" not in self.google_key):
            use_gemini = True
            print("INFO: Using Google Gemini (Free Tier)")
        elif self.openai_key and "placeholder" not in self.openai_key:
            print("INFO: Using OpenAI")
        else:
            print("WARNING: No valid API Key found. RAG Service will operate in MOCK mode.")
            return

        try:
            # 1. Setup Embeddings
            if use_gemini:
                # Use models/embedding-001 for maximum compatibility with free tier
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.google_key)
            else:
                embeddings = OpenAIEmbeddings(api_key=self.openai_key)
            
            # 2. Setup Vector DB (Chroma)
            self.vector_store = Chroma(
                persist_directory=self.db_dir,
                embedding_function=embeddings
            )
            
            # --- AUTO-INGESTION FOR KPGU DATA ---
            # If DB is empty, load the default dataset
            try:
                if not self.vector_store._collection.count():
                    print("INFO: Vector DB is empty. Ingesting KPGU Knowledge Base...")
                    
                    loader = TextLoader("data/kpgu_extended_info.txt")
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    splits = splitter.split_documents(docs)
                    self.vector_store.add_documents(splits)
                    print(f"SUCCESS: Ingested {len(splits)} chunks of KPGU data.")
            except Exception as e:
                print(f"WARNING: Could not ingest default data: {e}")
            
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            
            # 3. Setup LLM
            if use_gemini:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0.3,
                    google_api_key=self.google_key,
                    convert_system_message_to_human=True
                )
            else:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo", 
                    temperature=0.3,
                    api_key=self.openai_key
                )
            print("SUCCESS: RAG Pipeline Initialized.")
        except Exception as e:
            print(f"ERROR: Failed to initialize AI Pipeline: {e}")

    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        """
        Generates a response using the RAG pipeline.
        """
        query = request.query
        
        # --- FALLBACK FOR MISSING KEY ---
        if not self.llm:
            return ChatResponse(
                response="⚠️ **AI Not Configured:** I cannot access my 'brain' yet. Please double-check your **Google Gemini API Key** in the Render Environment Variables or .env file.",
                sources=["System Config"],
                detected_language="en"
            )

        if not self.retriever:
            return ChatResponse(
                response="⚠️ **System is warming up!** The Knowledge Base is currently being initialized. Please wait 10 seconds and try again.",
                sources=[],
                detected_language="en"
            )

        try:
            # 1. Retrieval
            docs = self.retriever.invoke(query)
            context_text = "\n\n".join([d.page_content for d in docs])
            sources = list(set([str(d.metadata.get("source", "Unknown Doc")) for d in docs]))
            
            # 2. Prompt Engineering (Friendly & Smart)
            template = """
            You are KPGU Assistant, a smart and friendly AI for Drs. Kiran & Pallavi Patel Global University.
            
            **Instructions:**
            1. **Primary Source**: Use the 'Context' below to answer questions about KPGU (Fees, Admissions, Rules).
            2. **General Knowledge**: If the user asks general questions (e.g., "What is coding?", "How to write a resume?", "Good Morning"), answer them helpfully using your own knowledge. **Do NOT** say "I don't have this info" for general topics.
            3. **Missing College Info**: If specific KPGU details are missing from the context, politely say: "I haven't been trained on that specific KPGU document yet."
            4. **Language Rule (CRITICAL)**: 
               - **DETECT** the language of the User's Message independently.
               - IF user writes in **Hindi** (Devanagari) OR **Hinglish** (Hindi in English letters e.g., "kya hal hai"), YOU MUST REPLY IN **HINDI** (Devanagari script).
               - IF user writes in **Gujarati** (Gujarati script or "Kem cho"), YOU MUST REPLY IN **GUJARATI**.
               - IF user writes in **English**, YOU MUST REPLY IN **ENGLISH**.
               - **DO NOT MIX LANGUAGES**.
            5. **Tone**: Be proper, respectful, and friendly. Use emojis like 🎓, 📚, ✨.
            
            Context:
            {context}
            
            User's Message: 
            {question}
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | self.llm | StrOutputParser()
            
            # 3. Generation with Retry Logic
            @retry(
                retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                stop=stop_after_attempt(3)
            )
            async def generate_with_retry():
                return await chain.ainvoke({"context": context_text, "question": query})

            try:
                response_text = await generate_with_retry()
            except google.api_core.exceptions.ResourceExhausted:
                return ChatResponse(
                    response="⚠️ **High Traffic Alert:** The AI brain is currently overloaded. Please wait 30 seconds and try again.",
                    sources=[],
                    detected_language="en"
                )
            
            # 4. Language Detection (Heuristic)
            detected_lang = "en"
            if any(0x0A80 <= ord(char) <= 0x0AFF for char in response_text[:50]): # Check for Gujarati
                detected_lang = "gu"
            elif any(0x0900 <= ord(char) <= 0x097F for char in response_text[:50]): # Check for Hindi/Devanagari
                detected_lang = "hi"

            return ChatResponse(
                response=response_text,
                sources=sources,
                detected_language=detected_lang
            )

        except Exception as e:
            error_msg = str(e).lower()
            print(f"CRITICAL RAG ERROR: {error_msg}")
            
            # Catch Resource Exhausted / Quota Errors
            if any(x in error_msg for x in ["429", "quota", "limit", "exhausted", "resource_exhausted"]):
                 return ChatResponse(
                    response="⚠️ **Gemini Limit Reached:** You are using the Free Tier and have sent too many messages quickly. Please wait **60 seconds** for the AI to breathe and then try again! 🎓",
                    sources=[],
                    detected_language="en"
                )
            
            # Catch Context Window / Token Errors
            if "context_length" in error_msg or "tokens" in error_msg:
                return ChatResponse(
                    response="⚠️ **Message too long:** This question is a bit too big for me. Can you ask it in a shorter way?",
                    sources=[],
                    detected_language="en"
                )

            # Generic but tracked fallback
            return ChatResponse(
                response=f"I encountered an issue (Code: P-3). Please wait 30 seconds. If it persists, check if your API key is valid. Error: {str(e)[:50]}...",
                sources=[],
                detected_language="en"
            )

rag_service = RAGService()
