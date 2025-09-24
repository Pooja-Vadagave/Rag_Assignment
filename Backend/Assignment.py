# bajaj2.py
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# ----------------------------
# 1. Load API Key
# ----------------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("⚠️ Please set GROQ_API_KEY in your .env file")

# ----------------------------
# 2. Define PDF paths
# ----------------------------
file_paths = [
    r"C:\Users\PoojaVadagave\Downloads\Earnings Call Transcript FY26 - Q1.pdf",
    r"C:\Users\PoojaVadagave\Downloads\Bajaj Finserv Investor Presentation - FY2025-26 - Q1.pdf"
]

all_docs = []
for path in file_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    loader = PyPDFLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = os.path.basename(path)
    all_docs.extend(docs)

# ----------------------------
# 3. Split into chunks
# ----------------------------
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
chunks = text_splitter.split_documents(all_docs)

# ----------------------------
# 4. Embed & store in FAISS
# ----------------------------
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

# ----------------------------
# 5. Prompt template
# ----------------------------
rag_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an assistant answering ONLY from the provided PDF documents.

Context:
{context}

Question:
{question}

Instructions:
- Extract the exact answer/data , number, percentage, date, or phrase if available.
- Always mention the PDF filename and page number.
- If multiple values exist, list them all with sources.
- If the answer is not in the context, reply: "I don't know from the provided PDFs."
-If a number is present anywhere in the context, extract it as the answer.
Never say "not explicitly mentioned" if you see a number in context.


Answer:
"""
)

# ----------------------------
# 6. LLM (Groq)
# ----------------------------
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0.0
)
rag_chain = rag_prompt | llm

# ----------------------------
# 7. Helper: regex numeric extractor
# ----------------------------
def extract_numbers(text):
    return re.findall(r"\d+(\.\d+)?%|₹\s?\d[\d,]*", text)

# ----------------------------
# 8. Function to get answer (for FastAPI)
# ----------------------------
def get_answer(question: str) -> str:
    retrieved_docs = vectorstore.similarity_search(question, k=10)[:3]
    if not retrieved_docs:
        return "I couldn't retrieve any relevant text."

    context = "\n\n".join([
        f"From {doc.metadata.get('source', 'Unknown')} (page {doc.metadata.get('page', '?')}):\n{doc.page_content}"
        for doc in retrieved_docs
    ])

    candidates = []
    for doc in retrieved_docs:
        candidates.extend(extract_numbers(doc.page_content))
    if candidates:
        context += f"\n\nPossible numeric values mentioned: {candidates}"

    result = rag_chain.invoke({"context": context, "question": question})
    return result.content

# ----------------------------
# 9. Optional: keep original chatbot CLI
# ----------------------------
if __name__ == "__main__":
    from pprint import pprint
    print("🤖 RAG ChatBot ready! Type your question (or 'exit' to quit)\n")
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            print("ChatBot: Goodbye!")
            break
        answer = get_answer(query)
        pprint(answer)
