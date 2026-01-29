import streamlit as st
from vectorstore import VectorStore
from chatbot import Chatbot

def main():
    st.title("Document QA Bot 🤖")
    st.write("Upload a PDF and ask questions (Free RAG system)")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    with st.sidebar:
        st.header("API Keys 🔑")
        cohere_api_key = st.text_input("Cohere API Key", type="password")
        pinecone_api_key = st.text_input("Pinecone API Key", type="password")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    user_query = st.text_input("Ask a question based on the document")

    if st.button("Submit") and uploaded_file and cohere_api_key and pinecone_api_key:
        with st.spinner("Processing PDF..."):
            with open("uploaded_document.pdf", "wb") as f:
                f.write(uploaded_file.read())

            vectorstore = VectorStore("uploaded_document.pdf", cohere_api_key, pinecone_api_key)
            chatbot = Chatbot(vectorstore)

            with st.spinner("Generating answer..."):
                answer, _ = chatbot.respond(user_query)
                st.session_state["chat_history"].append((user_query, answer))

    if st.session_state["chat_history"]:
        for q, a in st.session_state["chat_history"]:
            st.write(f"**You:** {q}")
            st.write(f"**Bot:** {a}")

if __name__ == "__main__":
    main()
