import os
import glob
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_all_documents(data_folder: str) -> str:
    all_text = ""
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {data_folder}")

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"Loading: {filename}")
        reader = PdfReader(pdf_path)
        doc_text = ""
        for page in reader.pages:
            doc_text += page.extract_text() + "\n"
        all_text += f"\n--- Source: {filename} ---\n{doc_text}\n"
        print(f"  {len(reader.pages)} pages extracted from {filename}")

    print(f"\nTotal documents loaded: {len(pdf_files)}")
    print(f"Total characters extracted: {len(all_text)}")
    return all_text

def build_vector_store(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    print(f"Text split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_texts(chunks, embeddings)
    print("Vector store built successfully")
    return vector_store

def build_qa_chain(vector_store):
    def qa_chain(question: str) -> str:
        docs = vector_store.similarity_search(question, k=5)
        context = "\n\n".join(doc.page_content for doc in docs)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a banking compliance and financial intelligence assistant.
You have access to Nedbank 2024 Annual Reports, Integrated Report, POPIA (Protection of Personal Information Act), and BCBS 239 (Banking Data Principles).
Answer questions accurately and professionally using only the provided context.
If the answer is not in the context, say so honestly.
Always cite which document your answer comes from."""
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    return qa_chain