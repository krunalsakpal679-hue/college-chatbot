from app.schemas.chat import ChatRequest, ChatResponse
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
import time

class RAGService:
    def __init__(self):
        # Core Settings
        self.openai_key = settings.OPENAI_API_KEY
        self.google_key = settings.GOOGLE_API_KEY
        self.db_dir = settings.CHROMA_DB_DIR
        self.vector_store = None
        self.retriever = None
        self.llm = None
        self.llms = []
        self.llm_models = []
        self.fallback_chunks = []
        
        # Speed & Reliability Kit
        self.response_cache = {}
        self.model_cooldowns = {}
        self.time = time
        self.is_ready = False
        
        # Lazy Loading Slots
        self.ChatPromptTemplate = None
        self.StrOutputParser = None
        self.ChatGoogleGenerativeAI = None
        self.google_exceptions = None
        
    def initialize(self):
        self._initialize_pipeline()
        self.is_ready = True

    def _initialize_pipeline(self):
        use_gemini = False
        if (not self.openai_key or "placeholder" in self.openai_key) and (self.google_key and "placeholder" not in self.google_key):
            use_gemini = True
        elif self.openai_key and "placeholder" not in self.openai_key:
            pass
        else:
            return

        try:
            from langchain_openai import ChatOpenAI, OpenAIEmbeddings
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_chroma import Chroma
            from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
            from langchain_community.document_loaders import TextLoader
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            import google.api_core.exceptions
            
            self.ChatPromptTemplate = ChatPromptTemplate
            self.StrOutputParser = StrOutputParser
            self.ChatGoogleGenerativeAI = ChatGoogleGenerativeAI
            self.google_exceptions = google.api_core.exceptions

            # 1. Embeddings
            embeddings = None
            if use_gemini:
                for m_name in ["models/text-embedding-004", "models/embedding-001"]:
                    try:
                        v = "v1" if "001" in m_name else "v1beta"
                        test_emb = GoogleGenerativeAIEmbeddings(model=m_name, google_api_key=self.google_key, version=v)
                        test_emb.embed_query("ping")
                        embeddings = test_emb
                        break
                    except: continue
            else:
                embeddings = OpenAIEmbeddings(api_key=self.openai_key)

            # 2. Vector DB
            if embeddings:
                try:
                    self.vector_store = Chroma(persist_directory=self.db_dir, embedding_function=embeddings)
                    if not self.vector_store._collection.count():
                        loader = TextLoader("data/kpgu_extended_info.txt")
                        docs = loader.load()
                        self.vector_store.add_documents(RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs))
                    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                except:
                    embeddings = None

            # 3. LLMs
            if use_gemini:
                # Highly Stable Flash Models
                self.llm_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b"]
                for m in self.llm_models:
                    try:
                        obj = ChatGoogleGenerativeAI(model=m, temperature=0.3, google_api_key=self.google_key, convert_system_message_to_human=True)
                        self.llms.append(obj)
                    except: pass
                self.llm = self.llms[0] if self.llms else None
            else:
                self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, api_key=self.openai_key)
            
            # 4. Fallback Chunks
            loader = TextLoader("data/kpgu_extended_info.txt")
            self.fallback_chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(loader.load())
            
        except Exception as e:
            print(f"Startup Error: {e}")

    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        query = request.query.strip().lower()
        now = self.time.time()

        # Instant Greeting Mocker
        if query in ["hi", "hii", "hiii", "hello", "hey", "namaste"]:
            return ChatResponse(response="Hello! I am your KPGU Assistant. 🎓 I can help with info on fees, courses, and admissions. How can I assist you?", sources=["System"], detected_language="en")

        # Cache Check
        if query in self.response_cache:
            return self.response_cache[query]

        if not self.is_ready:
            return ChatResponse(response="⚙️ System is warming up university records. Please try again in 10 seconds! 🎓", sources=[], detected_language="en")

        # 1. Retrieval
        docs = []
        try:
            if self.retriever:
                docs = self.retriever.invoke(request.query)
            if not docs and self.fallback_chunks:
                q_words = set(query.split())
                matches = [(sum(1 for w in q_words if w in c.page_content.lower()), c) for c in self.fallback_chunks]
                docs = [m[1] for m in sorted([x for x in matches if x[0] > 0], key=lambda x: x[0], reverse=True)[:3]]
        except: pass

        if not docs:
            return ChatResponse(response="I couldn't find specific records for that. Could you try asking in a different way? (Example: 'Fees' or 'B.Tech courses')", sources=[], detected_language="en")

        context_text = "\n\n".join([d.page_content for d in docs])
        sources = list(set([str(d.metadata.get("source", "KPGU Portal")) for d in docs]))

        # 2. AI Execution (Multi-Model Speed Rotation)
        template = "You are KPGU Assistant. Context: {context}\n\nQuestion: {question}\n\nReply clearly and concisely."
        prompt = self.ChatPromptTemplate.from_template(template)
        
        models_to_try = []
        if self.llms:
            for idx, m in enumerate(self.llms):
                if self.model_cooldowns.get(self.llm_models[idx], 0) < now:
                    models_to_try.append((m, self.llm_models[idx]))
        elif self.llm:
            models_to_try = [(self.llm, "default")]

        resp_text = None
        last_err = ""
        
        # Try AI First
        for model_obj, m_name in models_to_try:
            try:
                @retry(
                    retry=retry_if_exception_type(self.google_exceptions.ResourceExhausted) if self.google_exceptions else retry_if_exception_type(Exception),
                    wait=wait_exponential(multiplier=1, min=0.5, max=1.2),
                    stop=stop_after_attempt(2)
                )
                async def run():
                    chain = prompt | model_obj | self.StrOutputParser()
                    return await chain.ainvoke({"context": context_text, "question": request.query})
                
                resp_text = await run()
                if resp_text: break
            except Exception as e:
                last_err = str(e)
                if "429" in last_err or "exhausted" in last_err.lower():
                    self.model_cooldowns[m_name] = now + 90 # Longer cooldown
                continue

        # --- FINAL ZERO-FAILURE FALLBACK: Direct Answer Extraction ---
        if not resp_text:
            print("CRITICAL: AI API Exhausted. Switching to Deterministic Fallback.")
            # Build a deterministic answer from context
            best_chunk = docs[0].page_content
            # Simple cleaning for better presentation
            clean_chunk = best_chunk.replace('\n', ' ').strip()
            if len(clean_chunk) > 500: clean_chunk = clean_chunk[:497] + "..."
            
            resp_text = f"University Records Found:\n\n{clean_chunk}\n\n(Note: Serving from local records due to high traffic.)"

        # Lang Detect & Cache
        lang = "gu" if any(0x0A80 <= ord(c) <= 0x0AFF for c in resp_text[:50]) else ("hi" if any(0x0900 <= ord(c) <= 0x097F for c in resp_text[:50]) else "en")
        res_obj = ChatResponse(response=resp_text, sources=sources, detected_language=lang)
        if len(self.response_cache) < 100: self.response_cache[query] = res_obj
        return res_obj

rag_service = RAGService()
