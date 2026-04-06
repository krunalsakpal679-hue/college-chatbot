import os
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class RAGService:
    def __init__(self):
        self.google_keys = [k.strip() for k in settings.GOOGLE_API_KEY.split(",")] if settings.GOOGLE_API_KEY else []
        self.groq_key = settings.GROQ_API_KEY or ""
        self.context_text = self._load_knowledge_base()
        print(f"KPGU RAG Service Ready | Groq: {'YES' if 'gsk_' in self.groq_key else 'NO'} | Gemini Keys: {len(self.google_keys)}")

    def _load_knowledge_base(self):
        """Load the full KPGU master dataset once at startup."""
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "kpgu_master_dataset.txt")
        if not os.path.exists(data_path):
            data_path = "data/kpgu_master_dataset.txt"
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"KB Load Error: {e}")
            return "No knowledge base loaded."

    def _get_providers(self):
        """Returns list of (name, llm) tuples in priority order: Groq first, then Gemini keys."""
        providers = []
        if self.groq_key and "gsk_" in self.groq_key:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="llama-3.3-70b-versatile", api_key=self.groq_key,
                                 base_url="https://api.groq.com/openai/v1", temperature=0.0)
                providers.append(("Groq", llm))
            except Exception:
                pass
        for i, key in enumerate(self.google_keys):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=key,
                                             temperature=0.0, convert_system_message_to_human=True)
                providers.append((f"Gemini-{i+1}", llm))
            except Exception:
                pass
        return providers

    def _detect_language(self, query):
        """Detect language from query text using word scoring."""
        import re
        q = query.lower().strip()
        # Remove punctuation for clean word matching
        q_clean = re.sub(r'[^\w\s]', '', q)
        
        # Native script detection (highest priority)
        if any(0x0900 <= ord(c) <= 0x097F for c in query):
            return "Hindi (Devanagari Script)"
        if any(0x0A80 <= ord(c) <= 0x0AFF for c in query):
            return "Gujarati (Gujarati Script)"

        words = q_clean.split()

        # Gujarati-only words (checked first — higher priority)
        guj_strong = ["pachhi","shun","che","kyare","ketla","nu","kem","kevu","tamaru","mari","ane","mane","ena","vishe","samjay","su","aapo","mate","joiye","karvu","thase"]
        guj_score = sum(1 for w in words if w in guj_strong)
        if guj_score >= 1:
            return "Gujarati (Gujarati Script)"

        # Hindi-only words (must NOT be common English)
        hin_strong = ["kese","kaise","kya","kitna","kitni","kaun","kab","kahan",
                      "bhai","aap","batao","hain","hai","ho","padhai","vibhag",
                      "karo","milta","milti","mein","ki","ka","ke","nahi"]
        hin_score = sum(1 for w in words if w in hin_strong)
        # Need 2+ Hindi words to avoid false positives on English queries
        if hin_score >= 2:
            return "Hindi (Devanagari Script)"

        return "English"

    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        query = request.query.strip()
        if not query:
            return ChatResponse(response="Please enter a question about KPGU.", sources=[], detected_language="en")

        target_lang = self._detect_language(query)
        print(f"--- LANG: {target_lang} | QUERY: {query} ---")

        # Ultra-Fast Path: Small Talk & Greetings bypass the LLM completely for 0 latency
        q_lower = query.lower().replace("?", "").strip()
        fast_responses = {
            "english": ["hi", "hello", "hey", "how are you", "how are u", "hi kpgu"],
            "hindi": ["kese ho", "kaise ho", "namaste", "pranam", "kya haal hai", "hello kpgu", "kese hai"],
            "gujarati": ["kem cho", "kem chho", "majama", "shubhechha", "namaskar", "hello kem cho"]
        }
        
        gratitude_responses = {
            "english": ["thanks", "thank you", "ok thanks", "okay thanks", "thx"],
            "hindi": ["dhanyawad", "shukriya", "thanks bhai", "bahut dhanyawad"],
            "gujarati": ["aabhar", "khub khub aabhar", "dhanyavad", "thank you"]
        }
        
        if q_lower in fast_responses["english"]:
            return ChatResponse(response="Hello! I'm KPGU Assistant. I'm doing great! 🎓 How can I help you regarding admissions, courses, or fees today? 👋", sources=[], detected_language="en")
        if q_lower in fast_responses["hindi"]:
            return ChatResponse(response="नमस्ते! मैं बिल्कुल ठीक हूँ! 🎓 बताइए, आज मैं केपीजीयू (KPGU) से संबंधित आपकी क्या सहायता कर सकता हूँ? 👋", sources=[], detected_language="hi")
        if q_lower in fast_responses["gujarati"]:
            return ChatResponse(response="નમસ્તે! હું મજામાં છું! 🎓 ચાલો, આજે KPGU ને લગતી તમે કઈ માહિતી જાણવા માંગો છો? 👋", sources=[], detected_language="gu")

        if any(g in q_lower for g in gratitude_responses["english"]) and len(q_lower) < 20:
            return ChatResponse(response="You're very welcome! 😊 Feel free to ask if you need anything else about KPGU.", sources=[], detected_language="en")
        if any(g in q_lower for g in gratitude_responses["hindi"]) and len(q_lower) < 20:
            return ChatResponse(response="आपका स्वागत है! 😊 अगर आपको KPGU के बारे में कुछ और जानना हो, तो बेझिझक पूछें।", sources=[], detected_language="hi")
        if any(g in q_lower for g in gratitude_responses["gujarati"]) and len(q_lower) < 20:
            return ChatResponse(response="તમારો આભાર! 😊 જો તમને KPGU વિશે કોઈ અન્ય માહિતી જોઈતી હોય તો જરૂરથી પૂછો.", sources=[], detected_language="gu")

        script_rules = ""
        if target_lang == "Hindi (Devanagari Script)":
            script_rules = "- CRITICAL: You MUST use the native Devanagari script. NEVER use Romanized Hindi (e.g. write 'कैसे हो' NOT 'kese ho')."
        elif target_lang == "Gujarati (Gujarati Script)":
            script_rules = "- CRITICAL: You MUST use the native Gujarati script. NEVER use Romanized Gujarati."

        template = f"""You are the Official KPGU AI Assistant — a friendly, senior university counselor. ✨

INTERACTION RULES:
- If the user greets you or asks how you are, respond warmly with emojis. Example: "I'm doing great! 🎓 How can I help you today? 👋"
- For factual questions, use ONLY the KPGU MASTER DATA below. Never guess fees.
- If the answer is not in the data, say so and suggest calling 1800 843 9999.
- Respond 100% in {{target_language}}.
{script_rules}
- Start your answer immediately. No robotic preamble.

KPGU MASTER DATA:
{{context}}

User: {{question}}

Response (in {{target_language}}):"""

        prompt = ChatPromptTemplate.from_template(template)
        providers = self._get_providers()

        if not providers:
            return ChatResponse(response="⚠️ No AI providers configured. Check API keys.", sources=[], detected_language="en")

        # Smart Model Routing: Llama-3.1-8B hallucinates/loops on Gujarati & Hindi translation. 
        # For non-English strictly prioritize Gemini 2.0 Flash.
        if target_lang != "English":
            gemini_providers = [p for p in providers if "Gemini" in p[0]]
            groq_providers = [p for p in providers if "Groq" in p[0]]
            providers = gemini_providers + groq_providers

        last_err = ""
        for name, llm in providers:
            try:
                print(f"  -> Trying {name}...")
                chain = prompt | llm | StrOutputParser()
                result = await chain.ainvoke({"context": self.context_text, "question": query, "target_language": target_lang})
                if result:
                    print(f"  -> SUCCESS via {name}")
                    gu = sum(1 for c in result if 0x0A80 <= ord(c) <= 0x0AFF)
                    hi = sum(1 for c in result if 0x0900 <= ord(c) <= 0x097F)
                    lang = "gu" if gu > 10 else "hi" if hi > 10 else "en"
                    return ChatResponse(response=result, sources=["KPGU Knowledge Base"], detected_language=lang)
            except Exception as e:
                last_err = str(e)
                print(f"  -> FAIL {name}: {last_err[:80]}")

        return ChatResponse(
            response="⚠️ All AI providers are busy. Please wait 30 seconds and try again.",
            sources=[], detected_language="en"
        )

rag_service = RAGService()
