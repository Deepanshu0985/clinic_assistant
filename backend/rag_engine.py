# rag_engine.py
import json
from config import (
    LLM_MODEL, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
    DATA_DIR, CHROMA_DB_DIR
)
from prompt import prompt 
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def setup_vector_db():
    """
    Reads text files from your DATA_DIR, chunks them, and saves them to a local Chroma database.
    Run this manually once before starting your FastAPI server.
    """
    print(f"Loading medical templates from {DATA_DIR}...")
    
    # 1. Load documents
    loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found! Please add your .txt files to the data/ folder.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Initialize embeddings and save to ChromaDB
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    print(f"Creating vector database at {CHROMA_DB_DIR}...")
    Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    print("Database setup complete! You are ready to run the API.")

def process_patient_notes(raw_notes: str) -> dict:
    """
    Takes the rough notes, retrieves relevant medical templates, 
    and asks the local LLM to return a structured JSON response.
    """
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
    
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    llm = ChatOllama(model=LLM_MODEL, format="json", temperature=0.1)
    
    
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "notes": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    try:
        response = chain.invoke(raw_notes)
        structured_data = json.loads(response)
        return structured_data
    except json.JSONDecodeError:
        return {
            "error": "The AI failed to format the output correctly.",
            "raw_response": response
        }

if __name__ == "__main__":
    setup_vector_db()