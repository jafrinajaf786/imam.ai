import streamlit as st
import json
import requests
from datetime import datetime
from fuzzywuzzy import fuzz
from langdetect import detect
from deep_translator import GoogleTranslator

# ========== 1. Set Page Config (must be FIRST Streamlit command) ==========
st.set_page_config(page_title="Imam Mahdi (a.s.)313", page_icon="🕌")

# ========== 2. Sidebar - Dua ==========
st.sidebar.markdown("### 🕋 Imam e Zamana (a.s.) Dua")
st.sidebar.markdown("""
**اللّهُمّ كُنْ لِوَلِيّكَ الحُجّةِ ابْنِ الحَسَنِ**  
*Allahumma Kum le-waliyyekal Hujjatibnil Hassan*  
**O Allah, be, for Your representative, the Hujjat (proof), son of Al­Hassan,**  

**صَلَوَاتُكَ عَلَيْهِ وَعَلَى آبَائِهِ**  
*Salwaatoka A'layhe wa a'laa Aaabaa-Ehi*  
**Your blessings be on him and his forefathers,**  

**فِي هذِهِ السَّاعَةِ وَفي كُلّ سَاعَةٍ**  
*Fee haazehis saa-a'te wa fee kulle saa-a'tin*  
**in this hour and in every hour,**  

**وَلِيّاً وَحَافِظاً**  
*Waliyyawn wa Haafezawn*  
**a guardian, a protector,**  

**وَقَائِداً وَنَاصِراً**  
*Wa Qaa-edawn wa Naaserawn*  
**a leader, a helper,**  

**وَدَلِيلاً وَعَيْناً**  
*Wa Daleelawn wa A'ynan*  
**a guide and an eye.**  

**حَتَّى تُسْكِنَهُ أَرْضَكَ طَوْعاً**  
*Hattaa Tuskenahu Arzaka Taw-a'n*  

**وَتُمَتّعَهُ فِيهَا طَوِيلاً.**  
*Wa Tomatte-a'hu Feehaa Taweelaa.*  
**until You make him live on the earth, obediently, and bless him there for a long time.**
""")

# ========== 3. Title ==========
st.title("🕌 Mahadvi313.Ai")
st.markdown("Ask in **English / Hindi / Hinglish**. This bot only answers questions about **Imam Mahdi (a.s.)**.")
st.info(f"{"This Bot can make Mistakes"}\n {"Ye Bot Galti kar sakta hai"}")
# ========== 4. Load Dataset ==========
with open("imam_zamana_chatbot_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# ========== 5. Groq API Key ==========
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ========== 6. Utility Functions ==========
def detect_language(text):
    try:
        lang = detect(text)
        if all(ord(c) < 128 for c in text): return "English"
        if lang == "hi": return "Hindi"
        elif any(w in text.lower() for w in ["kya", "hai", "kaun", "kab", "kyunki", "ke", "ki", "wo", "unka", "unke"]):
            return "Hinglish"
        return "English"
    except: return "English"

def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except: return text

def translate_back(text, lang):
    if lang == "English": return text
    try:
        target = "hi" if lang in ["Hindi", "Hinglish"] else "en"
        return GoogleTranslator(source='en', target=target).translate(text)
    except: return text

def get_dataset_answer(translated_q, lang_field, threshold=70):
    best_score, best_answer = 0, None
    for item in dataset:
        score = fuzz.ratio(translated_q.lower(), item["question"].lower())
        if score > best_score and score >= threshold:
            best_score = score
            best_answer = item.get(lang_field)
    return best_answer

def is_about_mahdi(text):
    text = text.lower().strip()

    # 🌟 Core concepts, names, events, beliefs (Arabic, English, Urdu, transliteration)
    keywords = [
        "imam", "mahdi", "mehdi", "imam mahdi", "imam mehdi", "imam e zamana", "imam zaman", "imam zamanah",
        "hazrat mahdi", "hazrat mehdi", "twelfth imam", "12th imam", "hidden imam", "awaited savior",
        "al mahdi", "imam of time", "imam of our age", "imam asr", "imam zamana", "sahib uz zaman",
        "imam asr e zaman", "hujjat", "imam al hujjat", "imam hujjat", "imam hujjat ibn hasan",
        "mahdi ibn hasan", "hujjat ibn hasan", "hujjat ibn al hasan", "qaem", "al qaem", "al qaim", "qa'im",
        "imam qaim", "imam qaem", "imam al qaim", "al muntazar", "imam muntazar",

        # 🌟 Family and Lineage
        "imam hasan askari", "imam hasan askari a.s", "bibi narjis", "narjis bibi", "mother of mahdi",
        "father of mahdi", "bani hashim", "ahlulbayt", "ahlul bait", "ahlul bayt", "ahl e bait",

        # 🌟 Reappearance Events
        "zuhur", "zahoor", "reappearance", "rajat", "raj'at", "rajaat", "ghaibat", "ghaybat", "occultation",
        "minor occultation", "major occultation", "ghaibat e sughra", "ghaibat e kubra",

        # 🌟 Companions and symbols
        "313", "313 companions", "army of mahdi", "zulfiqar", "black flag", "black banner", "flag of khorasan",

        # 🌟 Signs and related figures
        "sufyani", "yamani", "dajjal", "khorasani", "shuaib ibn salih", "naqib", "abdullah", "nass", "siffin",

        # 🌟 Supplications and Surahs
        "dua", "dua ahad", "dua e ahad", "dua al ahad", "dua nudba", "dua e nudba", "sura kahf", "surah kahf",
        "ayat e wilayat", "surah baqarah", "ayat e zuhur", "zikr e mahdi", "salaam bar mahdi",

        # 🌟 Questions or curiosity terms
        "who is mahdi", "when will mahdi come", "when is imam mahdi coming", "is mahdi alive", "is imam born",
        "birth of imam mahdi", "mahdi kaun hai", "mahdi kab aayenge", "zaman kab ayega", "kab ayenge",
        "zahoor kab hoga", "imam ayenge kab", "imam ke nishaniyan", "mahdi kon hain",

        # 🌟 Events and Narrations
        "hadith mahdi", "riwayat", "narrations about mahdi", "signs of zuhur", "akhri zaman", "end times",
        "end of time", "akheri zaman", "end of days", "fitna sufyani", "imam ki rajat", "imam ki ghaibat",
        "nasl e mahdi", "rajat kab hogi", "raj'at ki nishani",

        # 🌟 Titles and respect
        "a.s", "alayhis salam", "ajtf", "aj", "imam a.s", "imam ajtf", "mahdi aj", "mahdi a.s", "mahdi ajtf"
    ]

    # 🌟 Pronouns / Indirect Question Triggers
    pronouns = [
        "unka", "unki", "unke", "unka aana", "wo", "woh", "wo kaun hain", "kaun hain wo", "uska", "uski", "uske",
        "ka", "ki", "ke", "kya", "kyu", "kyun", "kab", "kaise", "kaun", "kitne", "honge", "aayenge", "aana hai",
        "rahate hain", "zahoor hoga", "ghaibat me hain", "imam kaun hain", "kab aayenge", "kya woh",
        "kya wo aayenge", "kya mahdi aayenge", "imam kis tarah aayenge", "kyun ghaibat me hain"
    ]

    return any(k in text for k in keywords) or any(p in text for p in pronouns)

def ask_groq(question):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are a helpful Shia Islamic assistant. Only answer questions about Imam Mahdi (a.s.) accurately and briefly."},
        {"role": "user", "content": question}
    ]
    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 400
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ Groq Error: {str(e)}"

def get_response(user_input):
    user_lang = detect_language(user_input)
    translated_q = translate_to_english(user_input) if user_lang != "English" else user_input
    lang_field = "answer_hi" if user_lang in ["Hindi", "Hinglish"] else "answer_en"

    if is_about_mahdi(translated_q):
        answer = get_dataset_answer(translated_q, lang_field)
        source = "📘 From Najaf Jafri.313" if answer else "🌐 Najaf Jafri.313"
        if not answer:
            answer = ask_groq(translated_q)
    else:
        answer = "यह चैटबॉट केवल इमाम महदी (a.s.) से संबंधित सवालों का जवाब देता है।"
        source = "⚠️ Restricted Mode"

    final_answer = translate_back(answer, user_lang)
    return final_answer, source, user_lang

# ========== 7. Session State ==========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ========== 8. Input Form ==========
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Type your question here", placeholder="Ask about Imam Mahdi (a.s.)...")
    submit = st.form_submit_button("Send")

if submit and user_input:
    reply, source, lang = get_response(user_input)
    st.session_state.chat_history.append({
        "user": user_input,
        "bot": reply,
        "lang": lang,
        "source": source,
        "time": datetime.now().strftime("%I:%M %p")
    })

# ========== 9. Chat Display ==========
for chat in reversed(st.session_state.chat_history):
    with st.chat_message("user"):
        st.markdown(f"**You ({chat['lang']}):** {chat['user']}")
    with st.chat_message("assistant"):
        st.markdown(f"{chat['bot']}\n\n<sub>{chat['source']} • {chat['time']}</sub>", unsafe_allow_html=True)
