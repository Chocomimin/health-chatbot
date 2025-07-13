import cohere
import numpy as np
from datasets import load_dataset

# 🔐 Initialize Cohere Client (replace with your real API key)
co = cohere.Client("j4eac1MsJsxGdKNELKX4LZ04mlPJaRH93fPibCN5")

# ✅ Load dataset and prepare examples
dataset = load_dataset("dair-ai/emotion")
label_names = dataset['train'].features['label'].names
emotion_examples = [
    {"text": ex["text"], "label": label_names[ex["label"]]}
    for ex in dataset["train"]
    if label_names[ex["label"]] in ["sadness", "anger", "fear"]
]

# 📐 Cosine similarity
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 🔎 Emotion detection using embeddings
def detect_emotion_with_embeddings(user_input):
    try:
        texts = [user_input] + [ex["text"] for ex in emotion_examples[:300]]
        embeddings = co.embed(texts=texts).embeddings
        user_embedding = embeddings[0]
        example_embeddings = embeddings[1:]
        similarities = [cosine(user_embedding, e) for e in example_embeddings]
        best_index = int(np.argmax(similarities))
        best_score = similarities[best_index]
        best_emotion = emotion_examples[best_index]["label"]
        return best_emotion if best_score > 0.6 else "neutral"
    except Exception as e:
        print("Emotion detection error:", e)
        return "neutral"

# 🔎 Intent detection
def detect_intent(user_input: str) -> str:
    user_input_lower = user_input.lower()

    if any(word in user_input_lower for word in ["hi", "hello", "hey", "how are you", "hii"]):
        return "greeting"
    
    healthcare_keywords = [
        "pain", "fever", "ache", "symptom", "health", "medicine", "doctor", "illness",
        "sprain", "injury", "cut", "wound", "dizzy", "dizziness", "bleeding", "fracture", "burn",
        "fall", "vomit", "vomiting", "nausea", "cough", "cold", "flu", "chills", "sore throat",
        "headache", "migraine", "body pain", "back pain", "chest pain", "stomach pain", "leg pain",
        "cancer", "tumor", "lump", "biopsy", "radiation", "chemotherapy",
        "diabetes", "sugar", "insulin", "blood sugar",
        "infection", "antibiotics", "inflammation", "swelling", "pus", "rash", "redness",
        "asthma", "breathing", "shortness of breath", "wheezing", "tight chest",
        "allergy", "itching", "sneezing", "runny nose", "hives", "reaction",
        "bp", "blood pressure", "high bp", "low bp", "pressure", "hypertension", "hypotension",
        "heartbeat", "palpitations", "pulse", "chest tightness",
        "mental", "stress", "anxiety", "depression", "panic", "sad", "fear", "crying",
        "nosebleed", "nose bleed", "bleed from nose", "blood from nose", "bloody nose",
        "fatigue", "weakness", "tired", "insomnia", "trouble sleeping",
        "urine", "burning urination", "frequent urination", "UTI",
        "diarrhea", "constipation", "gas", "bloating", "stomach upset",
        "period", "menstrual", "cramps", "bleeding", "spotting", "PMS",
        "pregnant", "pregnancy", "missed period", "baby", "delivery", "nausea during pregnancy",
        "skin", "acne", "eczema", "psoriasis", "itchy", "scalp", "dry skin", "skin infection",
        "eye", "vision", "blurry", "red eye", "itchy eyes", "eye pain",
        "ear", "hearing", "earache", "ear infection", "blocked ear",
        "throat", "tonsil", "voice", "hoarseness", "sore throat",
        "covid", "corona", "coronavirus", "covid symptoms", "loss of smell", "loss of taste"
    ]

    if any(word in user_input_lower for word in healthcare_keywords):
        return "healthcare"

    if any(word in user_input_lower for word in ["diet", "nutrition", "meal", "calories", "weight loss", "plan", "healthy food", "eating"]):
        return "diet"

    if any(word in user_input_lower for word in ["can i", "how to", "what is this", "use this app"]):
        return "smalltalk"

    if any(word in user_input_lower for word in ["when", "while", "then", "i was", "i felt", "yesterday"]):
        return "neutral_concern"

    return "unknown"

# 💬 Smalltalk handler
def handle_smalltalk(intent, question):
    if intent == "greeting":
        return "👋 Hello! I'm your healthcare assistant. How can I help you?"
    elif intent == "smalltalk":
        return "🙂 I'm happy to chat! Tell me more about your concerns."
    return "I'm here to help you with health-related questions."

# 🩺 Healthcare chatbot logic (with chat history)
def ask_healthcare_bot(question: str, history: list):
    try:
        response = co.chat(
            model="command-nightly",
            message=question,
            temperature=0.5,
            chat_history=history
        )
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# 🧠 (Optional) suggestion generator for user queries
def suggest_options_based_on_input(user_input):
    user_input = user_input.lower()
    options = []
    if "run" in user_input or "walk" in user_input:
        options.append("1️⃣ Sprain or muscle strain")
        options.append("2️⃣ Shortness of breath")
    if "fell" in user_input or "hit" in user_input:
        options.append("3️⃣ Possible injury or fracture")
    if "fear" in user_input or "panic" in user_input:
        options.append("4️⃣ Panic or anxiety")
    if "pain" in user_input:
        options.append("5️⃣ Localized body pain (e.g., back, legs, head)")
    if not options:
        options = [
            "1️⃣ Physical discomfort or injury",
            "2️⃣ Mental stress or anxiety",
            "3️⃣ Breathing issue",
            "4️⃣ Something else"
        ]
    return options
