from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
import os
from dotenv import load_dotenv
import chardet
load_dotenv()

##  every file has a different encoding that is why i detect the encoding first 
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
    result = chardet.detect(raw_data)
    return result["encoding"]

## loading the data

def load_documents():
    documents = []
    folder_data = "backend/data/"
  
    for file_name in os.listdir(folder_data):
        
        file_path = os.path.join(folder_data, file_name)
        if file_name.endswith(".csv"):
            encoding = detect_encoding(file_path)
            loader = CSVLoader(file_path,encoding=encoding)
            documents.extend(loader.load())
    
    return documents

## split documents into chunks
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    
    return text_splitter.split_documents(documents)

## create Vectorial DB with Hugging Face Embeddings
def create_vectorstore(docs):
    embeddings = HuggingFaceEmbeddings(model_name="./backend/models/all-MiniLM-L6-v2",cache_folder="./backend/models")
    ## stocke in a db in directory 
    db_path = "./backend/db"
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        db = Chroma.from_documents(docs,embeddings,collection_name="tsaraia",persist_directory=db_path)
        
    else:
        db = Chroma(collection_name="tsaraia",persist_directory=db_path,embedding_function=embeddings)
    return db

## the rag chain
def create_rag_chain(db):
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        llm = ChatOpenAI(model="meta-llama/llama-4-scout:free", temperature=0.5,api_key=api_key,base_url="https://openrouter.ai/api/v1")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k":3}),
            return_source_documents=True
        )
        
        tool = Tool(
            name="RAG_Chain",
            func=qa_chain.run,
            description="useful for when you need to answer questions about the context"
        )
        return tool,llm
    except Exception as e:
        print(f"Error creating RAG chain: {e}")
        return None,None