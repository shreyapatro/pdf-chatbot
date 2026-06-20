from sentence_transformers import SentenceTransformer

def retrieve_chunks(question, collection):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_vector = model.encode([question]).tolist()
    
    results = collection.query(
        query_embeddings=question_vector,
        n_results=3
    )
    
    chunks = results['documents'][0]
    return chunks

if __name__ == "__main__":
    from ingest import ingest_pdf
    
    collection = ingest_pdf("sample_docs/contract.pdf")
    
    question = "what is this document about?"
    chunks = retrieve_chunks(question, collection)
    
    print(f"\nQuestion: {question}")
    print(f"\nTop {len(chunks)} relevant chunks found:\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print()

