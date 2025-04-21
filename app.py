import os
import re
import streamlit as st
from config import APP_NAME, OPENAI_MODEL, OLLAMA_MODEL, API_URL
from llm_invocation import LLMInvocation
from vector_document import VectorDocument
from vector_store_documents import VectorStoreDocuments
from llm_model import LLMModel

import logging
logging.basicConfig(level=logging.DEBUG)

import time

from dotenv import load_dotenv
load_dotenv()
from streamlit.runtime.scriptrunner import RerunException, RerunData

AUTH_USERNAME = os.getenv("CHAT_USERNAME")
AUTH_PASSWORD = os.getenv("CHAT_PASSWORD")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title(f"🔒 Login {APP_NAME}")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == AUTH_USERNAME and password == AUTH_PASSWORD:
            st.session_state.authenticated = True
            st.success("Login successful")
            raise RerunException(rerun_data=RerunData())
        else:
            st.error("Username or password incorrect")
    st.stop()

session_id = LLMInvocation.generate_session_id()
knowledge_directory = os.path.join(os.path.dirname(__file__), "data")
txt_files = [f for f in os.listdir(knowledge_directory) if f.endswith('.txt')]

st.title(f"🔎 Chat {APP_NAME}")

st.info("BotJuraganKlod adalah asisten virtual yang dapat membantu Anda dalam berbagai hal. Silakan ajukan pertanyaan atau permintaan Anda pada kolom chat di bawah ini.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, message in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user").write(message)
    elif role == "assistant":
        st.chat_message("assistant").write(message)

user_input = st.chat_input("Ketikkan pesan Anda...")
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").write(user_input)

    with st.spinner("BotJuraganKlod sedang memproses..."):
        try:
            memory = LLMInvocation.get_session_history(session_id)
            memory.clear()
            for role, text in st.session_state.chat_history:
                if role == "user":
                    memory.add_user_message(text)
                elif role == "assistant":
                    memory.add_ai_message(text)

            output = LLMInvocation.invoke(user_input, session_id=session_id)


            assistant_reply = output
            st.session_state.chat_history.append(("assistant", assistant_reply))
            assistant_msg = st.chat_message("assistant")
            with assistant_msg:
                placeholder = st.empty()
                displayed = ""
                for ch in assistant_reply:
                    displayed += ch
                    placeholder.write(displayed)
                    time.sleep(0.02)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

if st.button("Bersihkan Riwayat Chat"):
    st.session_state.chat_history = []
    memory = LLMInvocation.get_session_history(session_id)
    memory.clear()
    LLMInvocation.clear_all_cache()
    LLMInvocation.config.update({"configurable": {"session_id": LLMInvocation.generate_session_id()}})
    session_id = LLMInvocation.get_current_session_id(LLMInvocation.config["configurable"])
    st.success("Riwayat chat telah dihapus.")

    st.rerun()

with st.sidebar:
    cm = 1

    if LLMModel.with_ollama:
        cm = 1
    else:
        cm = 0

    # st.title("LLM Model")

    # # Model selection
    # tool = st.radio("Pilih model yang ingin digunakan:", [OPENAI_MODEL, OLLAMA_MODEL], index=cm)

    # if st.button("Terapkan Model", type="primary", use_container_width=True):
    #     if tool == OLLAMA_MODEL:
    #         LLMModel.with_ollama = True
    #     else:
    #         LLMModel.with_ollama = False

    #     vector_document = VectorDocument()
    #     new_doc = vector_document.chunk_documents_by_subtopic(vector_document.load_documents())

    #     store = VectorStoreDocuments()
    #     vs = store.vector_store()
    #     vs.remove_collection()
    #     vs.store_documents(new_doc)

    #     st.session_state.chat_history = []
    #     memory = LLMInvocation.get_session_history(session_id)
    #     memory.clear()
    #     LLMInvocation.config.update({"configurable": {"session_id": LLMInvocation.generate_session_id()}})
    #     session_id = LLMInvocation.get_current_session_id(LLMInvocation.config["configurable"])
    #     st.success("Riwayat chat telah dihapus.")

    #     st.rerun()

    # st.write(f"Model yang digunakan: {tool}")

    # Link to source of information
    st.title("Sumber Aksi")
    st.link_button("Lihat sumber aksi", url=f"{API_URL}/docs", type="primary", use_container_width=True)

    st.title("Sumber Informasi")

    # Source of information
    selected_file = st.selectbox("Lihat sumber informasi dari text file:", options=[None] + txt_files, format_func=lambda x: x or "Pilih file")

    if selected_file:
        file_path = os.path.join(knowledge_directory, selected_file)

        try:
            with open(file_path, "r") as file:
                file_content = file.read()

            st.subheader(f"Isi dari {selected_file}")

            clean_content = re.sub(r"\[\/?[A-Za-z]+\]", "", file_content)
            st.write(clean_content)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")