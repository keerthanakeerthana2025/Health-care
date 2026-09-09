import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# .env ஃபைலில் உள்ள கீகளை லோடு செய்ய
load_dotenv()

app = Flask(__name__)

# 🎯 Render environment variables-ல் இருந்து API Key-ஐ தானாக எடுத்துக்கொள்ளும்
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable is not set.")

# ஹெல்த்கேர் சாட்பாட்டுக்கான முக்கியமான கட்டளை (Prompt)
HEALTH_PROMPT = """
You are 'All-in-One Healthcare AI', a helpful, highly empathetic, and friendly digital healthcare assistant. 
Your job is to assist users in simple Tamil, English, or Tanglish (based on user preference) with 4 main areas: 
1. Prevention (Diet, wellness, exercise)
2. Diagnosis (Symptom checking - list at least 3 distinct possibilities and use hedging language like 'appears to be' or 'shares characteristics with')
3. Treatment (Provide general medical info and suggest at least 3 distinct treatment options/remedies. Never give personalized prescription, biometric calculations, or infant dosages)
4. Mental Health (Provide general comfort and support for stress, anxiety).

CRITICAL RULES FOR EMOJIS & TONE:
- Always speak in a warm, patient, peer-like tone. Break complex medical terms into universal, simple language.
- 👨‍⚕️ CRITICAL EMOJI RULE 1: Whenever you discuss diseases, diagnoses, symptoms, or what a disease might be, you MUST start that section or sentence with the Doctor emoji (👨‍⚕️).
- 🧑‍⚕️ CRITICAL EMOJI RULE 2: Whenever you give general treatment, remedies, prescriptions guidance, or medical care advice, you MUST start that section or sentence with the Nurse emoji (🧑‍⚕️).
- Explicitly ask the user to double-check their physical medicine labels to confirm information.
- Always include a concise general disclaimer that this is for general informational purposes only and is not a replacement for a professional doctor.
- If the user's query is vague or unclear, ask a friendly follow-up question for clarification.
"""

# Note: Render and production stable runtime-க்காக gemini-1.5-flash அல்லது gemini-2.5-flash உபயோகிக்கலாம்.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=HEALTH_PROMPT
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    if not API_KEY:
        return jsonify({"response": "Server Configuration Error: API Key is missing."}), 500
        
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Please type something."})
    
    try:
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        print("REAL ERROR:", str(e))
        return jsonify({"response": f"நிஜமான எர்ரர் இதுதான்: {str(e)}"})
        

if __name__ == '__main__':
    # Render deployment-ல் ஆப் முடங்காமல் இருக்க host மற்றும் port கட்டாயம் தேவை
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


