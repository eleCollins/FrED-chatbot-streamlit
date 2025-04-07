import streamlit as st
import pandas as pd
import requests
import json

st.title("🤖 AI-Fred - Tu Asistente Analítico")

uploaded_file = st.file_uploader("📁 Sube un archivo CSV para analizar", type="csv")

api_key = st.secrets["OPENROUTER_API_KEY"]
st.write("Clave leída (completa):", api_key)


headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://tusitio.com",
    "X-Title": "MiPrimerBot"
}

if "messages" not in st.session_state:
    st.session_state.messages = []

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    csv_text = df.head(20).to_csv(index=False)

    if not st.session_state.messages:
        system_prompt = (
            "Eres AI-Fred, un asistente analítico. Siempre responde iniciando con: "
            "'Hola soy AL, estuve trabajando y entendí esto de tu pregunta:'\n"
            "Este es el contenido del archivo CSV sobre el que debes basarte:\n\n"
            f"{csv_text}\n\n"
            "Usa esta información como referencia para todo lo que venga."
        )
        st.session_state.messages.append({"role": "system", "content": system_prompt})
        st.success("📄 Archivo cargado y procesado correctamente. ¡Haz tu pregunta!")

    for msg in st.session_state.messages[1:]:
        if msg["role"] == "user":
            st.markdown(f"**🧑 Tú:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI-Fred:** {msg['content']}")

    user_input = st.text_input("Escribe tu pregunta", key="input")

    if st.button("Enviar") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        data = {
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": st.session_state.messages
        }

        with st.spinner("AI-Fred está pensando..."):
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.error(f"Error: {response.status_code}")
            st.text(response.text)
