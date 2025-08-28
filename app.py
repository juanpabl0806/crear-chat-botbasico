import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Cargar variables de entorno (solo para desarrollo local)
load_dotenv()

# ===== CONFIGURACIÓN =====
API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_secret(key, default=None):
    if st.secrets and key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, default)

API_KEY = get_secret("DEEPSEEK_API_KEY")
MODEL = get_secret("MODEL", "deepseek-chat")
SYSTEM_PROMPT = get_secret(
    "SYSTEM_PROMPT",
    "Eres un asistente experto en electrónica, claro y breve. Responde en español."
)

if not API_KEY:
    st.error("⚠️ No se encontró la clave DEEPSEEK_API_KEY. Configúrala en Streamlit Secrets.")
    st.stop()

# ===== INTERFAZ =====
st.set_page_config(page_title="Chatbot DeepSeek", page_icon="🤖")
st.title("🤖 Chatbot DeepSeek Personalizado")

if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]

def chat_with_deepseek(prompt):
    messages = st.session_state.history + [{"role": "user", "content": prompt}]
    payload = {"model": MODEL, "messages": messages, "temperature": 0.3}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        response = data["choices"][0]["message"]["content"]
        return response
    except Exception as e:
        return f"Error: {e}"

# Mostrar historial de chat
for msg in st.session_state.history:
    if msg["role"] == "system":
        continue
    st.markdown(f"**{'Tú' if msg['role']=='user' else 'Bot'}:** {msg['content']}")

# Entrada de usuario
user_input = st.text_input("Escribe tu mensaje:", key="input")
if st.button("Enviar") and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    response = chat_with_deepseek(user_input)
    st.session_state.history.append({"role": "assistant", "content": response})
    st.experimental_rerun()

# Botón de reinicio
if st.button("Reiniciar conversación"):
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.experimental_rerun()
