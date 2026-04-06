
def detect_lang(query):
    query_lower = query.lower()
    target_lang = "English"
    if any(0x0900 <= ord(c) <= 0x097F for c in query):
        target_lang = "Hindi (Devanagari Script)"
    elif any(0x0A80 <= ord(c) <= 0x0AFF for c in query):
        target_lang = "Gujarati (Gujarati Script)"
    # New logic
    guj_words = ["pachhi", "shun", "che", "kyare", "ketla", "nu", "kya che", "kem cho"]
    hin_words = ["kya hai", "kaun sa", "kaisa hai", "hai", "kaun", "kab", "kahan"]
    
    if any(word in query_lower for word in guj_words):
        target_lang = "Gujarati (Gujarati Script)"
    elif any(word in query_lower for word in hin_words):
        target_lang = "Hindi (Devanagari Script)"
    return target_lang

test1 = "Graduate course pachhi placement nu"
test2 = "fees kya hai"
test3 = "How are you?"
print(f"Test 1: {detect_lang(test1)}")
print(f"Test 2: {detect_lang(test2)}")
print(f"Test 3: {detect_lang(test3)}")
