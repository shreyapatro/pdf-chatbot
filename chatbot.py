import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def build_prompt(question, chunks, history):
    context = "\n\n".join(chunks)
    
    conversation = ""
    for message in history:
        role = message["role"]
        content = message["content"]
        conversation += f"{role}: {content}\n"
    
    prompt = f"""You are a helpful assistant that answers questions about a document.
Only use the information from the context below to answer.
If the answer is not in the context, say "I couldn't find that in the document."

Context from document:
{context}

Conversation so far:
{conversation}
Question: {question}

Answer:"""
    
    return prompt


def get_answer(question, chunks, history):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = build_prompt(question, chunks, history)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        return answer
    
    except Exception as e:
        return f"Sorry, I couldn't generate an answer right now. Error: {e}"


if __name__ == "__main__":
    from ingest import ingest_pdf
    from retriever import retrieve_chunks
    
    collection = ingest_pdf("sample_docs/contract.pdf")
    
    question = "what happens if payment is late?"
    chunks = retrieve_chunks(question, collection)
    
    history = []
    
    answer = get_answer(question, chunks, history)
    
    print(f"\nQuestion: {question}")
    print(f"\nAnswer: {answer}")