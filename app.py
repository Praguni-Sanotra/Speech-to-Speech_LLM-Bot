import streamlit as st
import ollama as ol
from voice import record_voice
from text_to_speech import text_to_audio
import os
import time
import base64


st.set_page_config(page_title="🎙️ Voice Bot", layout="wide")
st.title("🎙️ Speech Bot")
st.sidebar.title("`Speak with LLMs` \n`in any language`")


def language_selector():
    lang_options = ["ar", "de", "en", "es", "fr", "it", "ja", "nl", "pl", "pt", "ru", "zh"]
    with st.sidebar: 
        return st.selectbox("Speech Language", ["en"] + lang_options)

def llm_selector():
    ollama_models = [m['name'] for m in ol.list()['models']]
    with st.sidebar:
        return st.selectbox("LLM", ollama_models)


def print_txt(text):
    if any("\u0600" <= c <= "\u06FF" for c in text): # check if text contains Arabic characters
        text = f"<p style='direction: rtl; text-align: right;'>{text}</p>"
    st.markdown(text, unsafe_allow_html=True)


def print_chat_message(message):
    text = message["content"]
    if message["role"] == "user":
        with st.chat_message("user", avatar="🎙️"):
            print_txt(text)
    else:
        with st.chat_message("assistant", avatar="🦙"):
            print_txt(text)

from text_to_speech import text_to_audio  # Add this to your imports
import os
import time

def main():
    model = llm_selector()

    with st.sidebar:
        selected_lang = language_selector()
        question = record_voice(language=selected_lang)

    # Init chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if model not in st.session_state.chat_history:
        st.session_state.chat_history[model] = []
    
    chat_history = st.session_state.chat_history[model]

    # Show existing chat
    for message in chat_history:
        print_chat_message(message)

    # Handle new question
    if question:
        user_message = {"role": "user", "content": question}
        print_chat_message(user_message)
        chat_history.append(user_message)

        # Get assistant response
        response = ol.chat(model=model, messages=chat_history)
        answer = response['message']['content']
        ai_message = {"role": "assistant", "content": answer}
        print_chat_message(ai_message)
        chat_history.append(ai_message)

        # 🎧 Convert response to speech
        audio_path = text_to_audio(answer, lang=selected_lang)
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            b64_audio = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        os.remove(audio_path)

        # Keep chat history short
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]

        st.session_state.chat_history[model] = chat_history


if __name__ == "__main__":
    main()