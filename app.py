import streamlit as st
from ingest import ingest_pdf
from retriever import retrieve_chunks
from chatbot import get_answer

st.set_page_config(page_title="PDF Chatbot", page_icon="📄")
st.title("📄 Chat with your PDF")

if "collection" not in st.session_state:
    st.session_state.collection = None

if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.collection is not None:
    if st.button("🔄 Upload a new document"):
        st.session_state.collection = None
        st.session_state.history = []
        st.rerun()

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None and st.session_state.collection is None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        with st.spinner("Reading your document..."):
            st.session_state.collection = ingest_pdf("temp.pdf")
        
        st.success("Document ready! Ask me anything about it.")
    
    except ValueError as e:
        st.error(str(e))
    
    except Exception as e:
        st.error(f"Something went wrong while processing this PDF: {e}")

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask a question about the document")

if question and st.session_state.collection is not None:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    
    with st.spinner("Thinking..."):
        chunks, pages = retrieve_chunks(question, st.session_state.collection)
        answer = get_answer(question, chunks, st.session_state.history)
        unique_pages = sorted(set(pages))
        source_text = ", ".join(str(p) for p in unique_pages)
    
    st.session_state.history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
        st.caption(f"📄 Source: Page {source_text}")