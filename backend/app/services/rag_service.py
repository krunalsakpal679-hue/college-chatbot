from app.schemas.chat import ChatRequest, ChatResponse
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings

class RAGService:
    def __init__(self):
        # Initialize Core Components (Keys and Dirs only)
        self.openai_key = settings.OPENAI_API_KEY
        self.google_key = settings.GOOGLE_API_KEY
        self.db_dir = settings.CHROMA_DB_DIR
        self.vector_store = None
        self.retriever = None
        self.llm = None
        self.fallback_chunks = []
        
        # References for lazy-loaded classes
        self.ChatPromptTemplate = None
        self.StrOutputParser = None
        self.ChatGoogleGenerativeAI = None # Add this
        self.google_exceptions = None
        self.llm_models = [] # Initialize this
        
    def initialize(self):
        """Public wrapper for async-safe initialization."""
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
            print("INFO: Loading AI core components...")
            from langchain_openai import ChatOpenAI, OpenAIEmbeddings
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_chroma import Chroma
            from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
            from langchain_community.document_loaders import TextLoader
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            import google.api_core.exceptions
            
            # Store references
            self.ChatPromptTemplate = ChatPromptTemplate
            self.StrOutputParser = StrOutputParser
            self.ChatGoogleGenerativeAI = ChatGoogleGenerativeAI # Fixed: Store this
            self.google_exceptions = google.api_core.exceptions

            # 1. Setup Embeddings with Multi-Layer Fallback
            embeddings = None
            if use_gemini:
                model_tries = [
                    {"name": "models/text-embedding-004", "version": "v1beta"},
                    {"name": "models/embedding-001", "version": "v1"}
                ]
                for try_cfg in model_tries:
                    try:
                        name = try_cfg["name"]
                        ver = try_cfg["version"]
                        print(f"DEBUG: Testing Gemini Embeddings ({name}, {ver})...")
                        test_emb = GoogleGenerativeAIEmbeddings(
                            model=name, 
                            google_api_key=self.google_key,
                            version=ver
                        )
                        test_emb.embed_query("test heartbeat")
                        embeddings = test_emb
                        print(f"SUCCESS: Connected to {name}")
                        break
                    except Exception as e:
                        print(f"WARNING: Model {try_cfg['name']} failed: {e}")
            else:
                embeddings = OpenAIEmbeddings(api_key=self.openai_key)

            # 2. Setup Retrieval (Vector or Keyword Fallback)
            if embeddings:
                try:
                    self.vector_store = Chroma(
                        persist_directory=self.db_dir,
                        embedding_function=embeddings
                    )
                    
                    # Auto-ingest if empty
                    if not self.vector_store._collection.count():
                        print("INFO: Vector DB empty. Ingesting...")
                        loader = TextLoader("data/kpgu_extended_info.txt")
                        docs = loader.load()
                        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                        splits = splitter.split_documents(docs)
                        self.vector_store.add_documents(splits)
                    
                    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                except Exception as e:
                    print(f"ERROR: Vector DB failure: {e}. Switching to Keyword Search.")
                    embeddings = None # Trigger keyword fallback below
            
            # FINAL FALLBACK: Keyword Search
            if not embeddings:
                print("INFO: Initializing Basic Keyword Search (Offline Mode)")
                try:
                    loader = TextLoader("data/kpgu_extended_info.txt")
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    self.fallback_chunks = splitter.split_documents(docs)
                except Exception as e:
                    print(f"ERROR: Keyword Search setup failed: {e}")

            # 3. Setup LLM with Multi-Layer Fallback
            if use_gemini:
                # Order: 2.0 (Fastest), 1.5-8b (Highest Quota), 1.5-flash (Reliable)
                self.llm_models = ["gemini-2.0-flash", "gemini-1.5-flash-8b", "gemini-1.5-flash"]
                self.llms = []
                for m_name in self.llm_models:
                    try:
                        llm = self.ChatGoogleGenerativeAI(
                            model=m_name,
                            temperature=0.3,
                            google_api_key=self.google_key,
                            convert_system_message_to_human=True
                        )
                        self.llms.append(llm)
                    except Exception as e:
                        print(f"WARNING: Could not preload {m_name}: {e}")
                
                # Set default llm to the first one
                self.llm = self.llms[0] if self.llms else None
            else:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo", 
                    temperature=0.3,
                    api_key=self.openai_key
                )
            print("SUCCESS: RAG Pipeline fully ready.")
        except Exception as e:
            print(f"CRITICAL: AI Setup failed: {e}")

    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        """Generates a response using retrieval and LLM."""
        query = request.query.strip().lower()
        
        # --- GREETING MOCKER (Save Quota) ---
        greetings = ["hi", "hii", "hiii", "hello", "hey", "hola", "namaste", "good morning", "good evening"]
        if query in greetings:
            return ChatResponse(
                response="Hello! I am your KPGU Assistant. 🎓 How can I help you today with information about admissions, courses, or college services? ✨",
                sources=["System Wisdom"],
                detected_language="en"
            )

        if not self.llm:
            return ChatResponse(response="⚠️ Bot is currently over-capacity. Please try again in 1 minute.", sources=[], detected_language="en")

        # 1. Smarter Retrieval
        docs = []
        try:
            if self.retriever:
                docs = self.retriever.invoke(request.query)
            elif self.fallback_chunks:
                # Basic Keyword Search
                q_words = set(query.split())
                matches = []
                for chunk in self.fallback_chunks:
                    score = sum(1 for w in q_words if w in chunk.page_content.lower())
                    if score > 0: matches.append((score, chunk))
                matches.sort(key=lambda x: x[0], reverse=True)
                docs = [m[1] for m in matches[:3]]
        except Exception as e:
            print(f"Retrieval error: {e}")

        if not docs:
            context_text = "No specific college records found for this query."
            sources = []
        else:
            context_text = "\n\n".join([d.page_content for d in docs])
            sources = list(set([str(d.metadata.get("source", "KPGU Registry")) for d in docs]))
            
        # 2. Response Creation
        template = """
        You are KPGU Assistant for Drs. Kiran & Pallavi Patel Global University.
        Context from records: {context}
        User Query: {question}
        
        Rules:
        - If the user asks about KPGU, use the context.
        - If general chat, be friendly.
        - Reply in the language the user uses (Hindi, Gujarati, or English).
        """
        
        try:
            prompt = self.ChatPromptTemplate.from_template(template)
            
            async def run_ai_with_chain(current_llm, context, q):
                chain = prompt | current_llm | self.StrOutputParser()
                return await chain.ainvoke({"context": context, "question": q})

            response_text = None
            last_error = ""

            # Try all pre-loaded models in sequence
            models_to_try = self.llms if hasattr(self, 'llms') and self.llms else [self.llm]
            
            for i, model in enumerate(models_to_try):
                try:
                    @retry(
                        retry=retry_if_exception_type(self.google_exceptions.ResourceExhausted) if self.google_exceptions else retry_if_exception_type(Exception),
                        wait=wait_exponential(multiplier=1, min=1, max=2),
                        stop=stop_after_attempt(2)
                    )
                    async def attempt():
                        return await run_ai_with_chain(model, context_text, request.query)
                    
                    response_text = await attempt()
                    if response_text: break
                except Exception as e:
                    last_error = str(e)
                    print(f"LLM Fallback {i+1} ({getattr(model, 'model_name', 'unknown')}) failed: {e}")
                    continue

            if not response_text:
                 if "429" in last_error or "exhausted" in last_error.lower():
                     return ChatResponse(
                        response="⚠️ **College AI is Resting:** Many students are asking questions! Google Gemini has reached its free limit. Please wait **20-30 seconds** and ask again—I'll be back online then! 🎓✨",
                        sources=[],
                        detected_language="en"
                    )
                 raise Exception(last_error)
            
            # Simple Lang Detection
            lang = "en"
            if any(0x0A80 <= ord(c) <= 0x0AFF for c in response_text[:50]): lang = "gu"
            elif any(0x0900 <= ord(c) <= 0x097F for c in response_text[:50]): lang = "hi"

            return ChatResponse(response=response_text, sources=sources, detected_language=lang)

        except Exception as e:
            print(f"Final AI Error: {e}")
            return ChatResponse(response="I am experiencing high traffic right now. Please try again in 10 seconds! 🎓", sources=[], detected_language="en")

rag_service = RAGService()
