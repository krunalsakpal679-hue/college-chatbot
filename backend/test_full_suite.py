
import asyncio
import os
import sys
from app.services.rag_service import rag_service
from app.schemas.chat import ChatRequest

# Define the 30 test questions (10 per language)
TEST_SUITE = {
    "English": [
        "What are the engineering courses available at KPGU?",
        "What is the fee structure for B.Tech CSE?",
        "How can I get admission to the B.A.M.S. course?",
        "What is the average and highest placement package at KPGU?",
        "Tell me about the campus facilities and hostel details.",
        "What are the eligibility criteria for MBA?",
        "Who are the top recruiters visiting the campus?",
        "Are there any scholarships available for Gujarat students?",
        "What is the attendance rule for students?",
        "Where is the university located and how can I contact them?"
    ],
    "Hindi": [
        "केपीजीयू में कौन-कौन से इंजीनियरिंग कोर्स उपलब्ध हैं?",
        "बी.टेक सीएसई की फीस संरचना क्या है?",
        "बी.ए.एम.एस. (B.A.M.S.) कोर्स में प्रवेश कैसे मिल सकता है?",
        "केपीजीयू में औसत और उच्चतम प्लेसमेंट पैकेज क्या है?",
        "कैंपस की सुविधाओं और हॉस्टल के बारे में जानकारी दें।",
        "एमबीए के लिए पात्रता मानदंड क्या हैं?",
        "कैंपस में आने वाली टॉप कंपनियां कौन सी हैं?",
        "क्या गुजरात के छात्रों के लिए कोई छात्रवृत्ति उपलब्ध है?",
        "छात्रों के लिए उपस्थिति (attendance) का नियम क्या है?",
        "विश्वविद्यालय कहां स्थित है और मैं उनसे संपर्क कैसे कर सकता हूं?"
    ],
    "Gujarati": [
        "KPGU માં કયા એન્જિનિયરિંગ કોર્સ ઉપલબ્ધ છે?",
        "B.Tech CSE માટે ફીનું માળખું શું છે?",
        "B.A.M.S. કોર્સમાં પ્રવેશ કેવી રીતે મેળવી શકાય?",
        "KPGU માં સરેરાશ અને ઉચ્ચતમ પ્લેસમેન્ટ પેકેજ શું છે?",
        "કેમ્પસ સુવિધાઓ અને હોસ્ટેલ વિશે વિગતો આપો.",
        "MBA માટે પાત્રતાના માપદંડ શું છે?",
        "કેમ્પસમાં આવતી ટોચની કંપનીઓ કઈ છે?",
        "શું ગુજરાતના વિદ્યાર્થીઓ માટે કોઈ સ્કોલરશિપ ઉપલબ્ધ છે?",
        "વિદ્યાર્થીઓ માટે હાજરીનો નિયમ શું છે?",
        "યુનિવર્સિટી ક્યાં આવેલી છે અને હું તેમનો સંપર્ક કેવી રીતે કરી શકું?"
    ]
}

def check_script(text, lang_code):
    hi_count = sum(1 for char in text if 0x0900 <= ord(char) <= 0x097F)
    gu_count = sum(1 for char in text if 0x0A80 <= ord(char) <= 0x0AFF)
    
    if lang_code == "hi":
        return hi_count > 10
    if lang_code == "gu":
        return gu_count > 10
    if lang_code == "en":
        # For English, we expect NO Hindi/Gujarati scripts (or very few, like currency symbols if any)
        return hi_count < 5 and gu_count < 5
    return True

async def run_tests():
    print("="*60)
    print("KPGU AI ASSISTANT - FULL COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = []
    
    for lang, questions in TEST_SUITE.items():
        print(f"\n[TESTING LANGUAGE: {lang.upper()}]")
        lang_code = "en" if lang == "English" else ("hi" if lang == "Hindi" else "gu")
        
        for i, q in enumerate(questions, 1):
            print(f"Q{i}: {q}")
            try:
                request = ChatRequest(query=q)
                response = await rag_service.generate_response(request)
                
                # Validation Logic
                passed_script = check_script(response.response, lang_code)
                no_preamble = not any(p in response.response[:50] for p in ["हिन्दी में", "I will answer", "In Hindi", "In Gujarati", "ગુજરાતી માં"])
                
                status = "PASS" if passed_script and no_preamble else "FAIL"
                if not no_preamble: status += " (PREAMBLE DETECTED)"
                if not passed_script: status += " (WRONG SCRIPT)"
                
                print(f"  Result: {status}")
                if status != "PASS":
                    print(f"  Snippet: {response.response[:100]}...")
                
                results.append({
                    "lang": lang,
                    "q": q,
                    "status": status,
                    "response": response.response
                })
                
                # Increase delay to avoid Free-Tier Rate Limits
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"  Error: {e}")
                results.append({"lang": lang, "q": q, "status": f"ERROR: {e}"})

    # Summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    for lang in TEST_SUITE.keys():
        lang_results = [r for r in results if r["lang"] == lang]
        passed = sum(1 for r in lang_results if r["status"] == "PASS")
        print(f"{lang}: {passed}/10 Passed")
    
    # Save detailed log
    with open("test_results_detailed.log", "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"Language: {r['lang']}\nQuestion: {r['q']}\nStatus: {r['status']}\nResponse: {r['response']}\n" + "-"*40 + "\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
