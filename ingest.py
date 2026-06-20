import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    return chunks

def embed_chunks(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings

def store_in_chroma(chunks, embeddings):
    client = chromadb.Client()
    collection = client.create_collection(name="pdf_chunks")
    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection

def ingest_pdf(pdf_path):
    print("Extracting text from PDF...")
    text = extract_text(pdf_path)
    print(f"Extracted {len(text)} characters")

    print("Chunking text...")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    print("Embedding chunks...")
    embeddings = embed_chunks(chunks)
    print("Embedding complete")

    print("Storing in ChromaDB...")
    collection = store_in_chroma(chunks, embeddings)
    print(f"Stored {collection.count()} chunks in ChromaDB")

    return collection


if __name__ == "__main__":
    collection = ingest_pdf("sample_docs/contract.pdf")
    print("Phase 1 complete. Ready for querying.")