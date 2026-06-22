import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        pages.append({"page": page_num, "text": page.get_text()})
    return pages

def chunk_text(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    
    all_chunks = []
    all_metadata = []
    
    for page in pages:
        page_chunks = splitter.split_text(page["text"])
        for chunk in page_chunks:
            all_chunks.append(chunk)
            all_metadata.append({"page": page["page"]})
    
    return all_chunks, all_metadata

def embed_chunks(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings

def store_in_chroma(chunks, embeddings, metadata):
    client = chromadb.PersistentClient(path="./chroma_db")
    
    if "pdf_chunks" in [c.name for c in client.list_collections()]:
        client.delete_collection("pdf_chunks")
    
    collection = client.create_collection(name="pdf_chunks")
    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection

def load_existing_collection():
    import os
    if not os.path.exists("./chroma_db") or not os.path.exists("last_doc.txt"):
        return None, None
    
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection_names = [c.name for c in client.list_collections()]
        
        if "pdf_chunks" not in collection_names:
            return None, None
        
        collection = client.get_collection("pdf_chunks")
        
        with open("last_doc.txt", "r") as f:
            filename = f.read().strip()
        
        return collection, filename
    
    except Exception:
        return None, None

def ingest_pdf(pdf_path, original_filename="document.pdf"):
    print("Extracting text from PDF...")
    pages = extract_text(pdf_path)
    total_chars = sum(len(p["text"]) for p in pages)
    print(f"Extracted {total_chars} characters from {len(pages)} pages")

    if total_chars < 50:
        raise ValueError(
            "This PDF appears to have no readable text. "
            "It might be a scanned document or an image-based PDF. "
            "Please upload a digital PDF instead."
        )

    print("Chunking text...")
    chunks, metadata = chunk_text(pages)
    print(f"Created {len(chunks)} chunks")

    print("Embedding chunks...")
    embeddings = embed_chunks(chunks)
    print("Embedding complete")

    print("Storing in ChromaDB...")
    collection = store_in_chroma(chunks, embeddings, metadata)
    print(f"Stored {collection.count()} chunks in ChromaDB")

    with open("last_doc.txt", "w") as f:
        f.write(original_filename)

    return collection

if __name__ == "__main__":
    collection = ingest_pdf("sample_docs/contract.pdf")
    print("Phase 1 complete. Ready for querying.")