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

# Where the cached FAISS index is stored on disk
FAISS_INDEX_PATH = "vector_store_cache"


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


def get_embeddings():
    """Shared embeddings model - same one used for building and loading the index."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def build_vector_store(text: str):
    """Builds a fresh FAISS index from raw text, then saves it to disk for reuse."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    print(f"Text split into {len(chunks)} chunks")

    embeddings = get_embeddings()
    vector_store = FAISS.from_texts(chunks, embeddings)
    print("Vector store built successfully")

    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"Vector store cached to disk at '{FAISS_INDEX_PATH}'")

    return vector_store


def load_or_build_vector_store(data_folder: str):
    """
    Loads the FAISS index from disk if a cached version exists.
    Otherwise, rebuilds it from the PDF documents and saves it for next time.
    This avoids re-processing all 7 PDFs and re-computing embeddings on every
    app restart, which is the main cause of CPU throttling on Streamlit Cloud.
    """
    if os.path.exists(FAISS_INDEX_PATH):
        print(f"Found cached vector store at '{FAISS_INDEX_PATH}' - loading from disk")
        embeddings = get_embeddings()
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True  # safe here: we created this file ourselves
        )
        print("Vector store loaded from cache successfully")
        return vector_store

    print("No cached vector store found - building fresh from PDFs")
    text = load_all_documents(data_folder)
    return build_vector_store(text)


def build_qa_chain(vector_store):
    def qa_chain(question: str) -> str:
        docs = vector_store.similarity_search(question, k=5)
        context = "\n\n".join(doc.page_content for doc in docs)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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