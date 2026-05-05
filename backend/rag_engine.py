# rag_engine.py
import json
from config import (
    LLM_MODEL, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
    DATA_DIR, CHROMA_DB_DIR
)
from prompt import prompt
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama, OllamaEmbeddings


def setup_vector_db():
    """
    Reads text files from DATA_DIR, chunks them, and saves them to a Chroma database.
    """
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

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    print("Database setup complete")


_embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
_vector_db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=_embeddings)
_retriever = _vector_db.as_retriever(search_kwargs={"k": 3})
_llm = ChatOllama(model=LLM_MODEL, format="json", temperature=0)
_chain = prompt | _llm | StrOutputParser()


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def process_patient_notes(raw_notes: str) -> dict:
    """
    Takes the rough notes, retrieves relevant medical templates,
    and asks the local LLM to return a structured JSON response.
    """
    retrieved_docs = _retriever.invoke(raw_notes)
    print(retrieved_docs)
    context = _format_docs(retrieved_docs)

    response = None
    try:
        response = _chain.invoke({"context": context, "notes": raw_notes})
        print("LLM Response:", response)  
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        return {
            "error": "The AI failed to format the output correctly.",
            "raw_response": response,
        }

    structured_data["sources"] = [
        {
            "source": doc.metadata.get("source", "unknown"),
            "snippet": doc.page_content[:200],
        }
        for doc in retrieved_docs
    ]
    return structured_data


if __name__ == "__main__":
    setup_vector_db()
