import streamlit as st
from chatbot import chat
import time

st.write('Hello and Welcome to the streamlit application by Varad I will be using this to make a LLM RAG app')

context = ""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today"}]
    
for message in st.session_state.messages:
    if message['role'] != 'system':
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything (I'm a RAG) "):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    formatted_context = ""
    for msg in st.session_state.messages:
        formatted_context += f"{msg['role'].capitalize()}: {msg['content']} \n\n"
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # full_response = ""
        ai_response = chat(prompt, formatted_context)
        st.markdown(ai_response)

        # for chunk in ai_response.split():
        #     full_response += chunk + " "
        #     time.sleep(0.1)
        #     message_placeholder.markdown(full_response + "| ")
        # message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})