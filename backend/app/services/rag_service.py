from app.schemas.chat import ChatRequest, ChatResponse
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
import time
import re

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

            # Fix Paths: data is in backend/data, this file is in backend/app/services
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(current_dir, "..", "..", "data", "kpgu_extended_info.txt")

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
                        loader = TextLoader(data_file)
                        docs = loader.load()
                        self.vector_store.add_documents(RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs))
                    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
                except:
                    embeddings = None

            # 3. LLMs
            if use_gemini:
                self.llm_models = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash", "gemini-1.5-pro"]
                for m in self.llm_models:
                    try:
                        obj = ChatGoogleGenerativeAI(model=m, temperature=0.2, google_api_key=self.google_key, convert_system_message_to_human=True)
                        self.llms.append(obj)
                    except: pass
                self.llm = self.llms[0] if self.llms else None
            else:
                self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, api_key=self.openai_key)
            
            # 4. Fallback Chunks
            loader = TextLoader(data_file)
            self.fallback_chunks = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300).split_documents(loader.load())
            
        except Exception as e:
            print(f"Startup Error: {e}")

    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        query_raw = request.query.strip()
        query = query_raw.lower()
        now = self.time.time()

        # Instant Greeting Mocker
        if query in ["hi", "hii", "hiii", "hello", "hey", "namaste"]:
            return ChatResponse(
                response="Hello! I am your KPGU Assistant. 🎓 I can help you with information about admissions, courses, and college fees. How can I assist you today?",
                sources=["System Wisdom"],
                detected_language="en"
            )

        # Cache Check
        if query in self.response_cache:
            return self.response_cache[query]

        if not self.is_ready:
            return ChatResponse(response="⚙️ System is warming up university records. Please try again in 5 seconds! 🎓", sources=[], detected_language="en")

        # 1. Retrieval
        docs = []
        try:
            if self.retriever:
                docs = self.retriever.invoke(query_raw)
            if not docs and self.fallback_chunks:
                q_words = set(query.split())
                matches = [(sum(2 if w in c.page_content.lower() else 0 for w in q_words), c) for c in self.fallback_chunks]
                docs = [m[1] for m in sorted([x for x in matches if x[0] > 0], key=lambda x: x[0], reverse=True)[:3]]
        except: pass

        if not docs:
            return ChatResponse(response="I couldn't find specific details for that in the university records. Could you please specify if you're asking about B.Tech, Fees, or Admissions? 🎓", sources=[], detected_language="en")

        context_text = "\n\n".join([d.page_content for d in docs])
        sources = list(set([str(d.metadata.get("source", "KPGU Portal")) for d in docs]))

        # 2. AI Execution
        template = """
        You are KPGU Assistant. Answer based on the context.
        Context: {context}
        Question: {question}
        Reply professionally in the user's language.
        """
        prompt = self.ChatPromptTemplate.from_template(template)
        
        models_to_try = []
        if self.llms:
            for idx, m in enumerate(self.llms):
                if self.model_cooldowns.get(self.llm_models[idx], 0) < now:
                    models_to_try.append((m, self.llm_models[idx]))
        elif self.llm:
            models_to_try = [(self.llm, "default")]

        resp_text = None
        for model_obj, m_name in models_to_try:
            try:
                @retry(
                    retry=retry_if_exception_type(self.google_exceptions.ResourceExhausted) if self.google_exceptions else retry_if_exception_type(Exception),
                    wait=wait_exponential(multiplier=1, min=0.5, max=1.2),
                    stop=stop_after_attempt(3)
                )
                async def run():
                    chain = prompt | model_obj | self.StrOutputParser()
                    return await chain.ainvoke({"context": context_text, "question": query_raw})
                
                resp_text = await run()
                if resp_text: 
                    print(f"SUCCESS: Response generated using model {m_name}")
                    break
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "exhausted" in err_msg.lower():
                    print(f"WARNING: Model {m_name} is busy. Cooling down...")
                    self.model_cooldowns[m_name] = now + 60
                continue

        # --- CONVERSATIONAL FALLBACK (Zero-Failure) ---
        if not resp_text:
            print("INFO: AI Limit reached. Using conversational local brain.")
            best_info = docs[0].page_content
            # Clean and polish for a professional conversational look
            best_info = re.sub(r'#+\s*', '', best_info).replace('\n', ' ').strip()
            resp_text = f"According to university records: {best_info[:650]}... \n\nI hope this helps! Feel free to ask more specific questions about this topic. 🎓"

        # Lang Detect & Cache
        lang = "gu" if any(0x0A80 <= ord(c) <= 0x0AFF for c in resp_text[:100]) else ("hi" if any(0x0900 <= ord(c) <= 0x097F for c in resp_text[:100]) else "en")
        res_obj = ChatResponse(response=resp_text, sources=sources, detected_language=lang)
        if len(self.response_cache) < 150: self.response_cache[query] = res_obj
        return res_obj

rag_service = RAGService()
