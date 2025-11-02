import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector


load_dotenv()

def validate_environment_variables():
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    
    required_vars = ["PG_VECTOR_COLLECTION_NAME", "DATABASE_URL", "PDF_PATH"]
    
    if embedding_provider == "openai":
        required_vars.append("OPENAI_API_KEY")
    elif embedding_provider == "gemini":
        required_vars.append("GOOGLE_API_KEY")
    else:
        raise RuntimeError(f"EMBEDDING_PROVIDER deve ser 'openai' ou 'gemini'. Valor atual: {embedding_provider}")
    
    for k in required_vars:
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")


def load_pdf():
    pdf_path = os.getenv("PDF_PATH")
    if not pdf_path or not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF file not found at path: {pdf_path}")

    return PyPDFLoader(pdf_path).load()


def get_embeddings():
    """Retorna o provider de embeddings baseado na variável de ambiente EMBEDDING_PROVIDER"""
    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    
    if provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model)
    elif provider == "gemini":
        model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model)
    else:
        raise RuntimeError(f"EMBEDDING_PROVIDER deve ser 'openai' ou 'gemini'. Valor atual: {provider}")


def ingest_pdf():
    
    validate_environment_variables()

    docs = load_pdf()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, add_start_index=False).split_documents(docs)

    if not splitter:
        raise RuntimeError("Failed to split documents")
        
    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splitter
    ]   

    ids = [f"doc-{i}" for i in range(len(enriched))]

    embeddings = get_embeddings()

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True
    )
    store.add_documents(documents=enriched, ids=ids)

if __name__ == "__main__":
    ingest_pdf()






