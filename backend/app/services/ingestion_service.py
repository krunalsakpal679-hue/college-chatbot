import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

class IngestionService:
    def __init__(self):
        self.data_dir = "data"
        self.db_dir = settings.CHROMA_DB_DIR
        self.api_key = settings.OPENAI_API_KEY
        
    def ingest_documents(self):
        """
        Scans data directory for supported files, processes them, and updates the Vector DB.
        """
        self.openai_key = settings.OPENAI_API_KEY
        self.google_key = settings.GOOGLE_API_KEY
        
        use_gemini = False
        if (not self.openai_key or "placeholder" in self.openai_key) and (self.google_key and "placeholder" not in self.google_key):
            use_gemini = True
        elif not (self.openai_key and "placeholder" not in self.openai_key):
             return {"status": "error", "message": "No valid API Key (OpenAI or Google) found."}

        # 1. Load Documents
        documents = []
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        files = [f for f in os.listdir(self.data_dir) if os.path.isfile(os.path.join(self.data_dir, f))]
        
        if not files:
            return {"status": "warning", "message": "No files found in 'data' directory."}

        print(f"INFO: Found {len(files)} files to ingest.")

        for file in files:
            file_path = os.path.join(self.data_dir, file)
            try:
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith(".txt"):
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith(".docx"):
                    loader = Docx2txtLoader(file_path)
                    documents.extend(loader.load())
            except Exception as e:
                print(f"ERROR: Failed to load {file}: {e}")

        if not documents:
            return {"status": "warning", "message": "No valid documents loaded."}

        # 2. Split Text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        try:
            embeddings = None
            if use_gemini:
                try:
                    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=self.google_key)
                    # Test
                    embeddings.embed_query("test")
                except Exception:
                    print("WARNING: Ingestion falling back to HuggingFace embeddings.")
                    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            else:
                embeddings = OpenAIEmbeddings(api_key=self.openai_key)
                
            vector_store = Chroma(
                persist_directory=self.db_dir,
                embedding_function=embeddings
            )
            vector_store.add_documents(splits)
            
            return {
                "status": "success", 
                "message": f"Successfully processed {len(files)} files into {len(splits)} chunks using {'Gemini' if use_gemini else 'OpenAI'}.",
                "files": files
            }
        except Exception as e:
            return {"status": "error", "message": f"Vector DB Error: {str(e)}"}

ingestion_service = IngestionService()
