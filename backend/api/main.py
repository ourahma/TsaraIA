from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.src.models import ResearchResponse
from backend.src.rag import create_rag_chain, load_documents, split_documents, create_vectorstore
from langchain.agents import create_tool_calling_agent, AgentExecutor,AgentType
from langchain_core.output_parsers import JsonOutputParser
from backend.src.prompt import prompt, parser
import logging
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="RAG Chatbot API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str


_vectorstore = None
_agent = None
_agent_executor = None


def initialize_rag_system():
    """Initialise le système RAG une seule fois au démarrage"""
    global _vectorstore, _agent,_agent_executor
    
    try:
        logging.info("initializing System rag...")
        
        # Charger et traiter les documents
        docs = load_documents()
        chunks = split_documents(docs)
        _vectorstore = create_vectorstore(chunks)
        
        # Créer le chain RAG et l'agent
        tool, llm = create_rag_chain(_vectorstore)
        
        # Créer l'agent avec le bon prompt
        _agent = create_tool_calling_agent(llm=llm,tools=[tool],prompt=prompt)
        
        _agent_executor = AgentExecutor(agent=_agent,tools=[tool],verbose=True,handle_parsing_errors=True)
        
        logging.info("Init System RAG Success")
        
    except Exception as e:
        logging.error(f"Error in init System RAG: {str(e)}")
        raise e

# Initialiser le système au démarrage de l'app
@app.on_event("startup")
async def startup_event():
    initialize_rag_system()

@app.get("/")
async def root():
    return {"message": "API RAG Chat is running"}

@app.post("/chat", response_model=ResearchResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        global _agent
        
        if _agent_executor is None:
            raise HTTPException(status_code=500, detail="System RAG not initialized")
        
        raw_response = _agent_executor.invoke({
            "input": chat_message.message,  
            "chat_history": []
        })
        print("Raaw response : ",raw_response)
        # Parser la réponse
        output_parser = JsonOutputParser()
        output_text = output_parser.invoke(raw_response)
        try:
            structured_response = parser.parse(output_text)
            return ResearchResponse(summary=structured_response.summary, topic=structured_response.topic, sources=structured_response.tools_used, tools_used=structured_response.tools_used)
        except Exception as parse_error:
            logging.error(f"Error parsing: {parse_error}")
            structured_response = output_text
            return ResearchResponse(
                summary="Je n'ai pas trouvé d'information pour cette question.",
                topic="Inconnu",
                sources=[],
                tools_used=[]
            )
        
        
    
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in treating request: {str(e)}")

@app.get("/health")
async def health_check():
    global _agent
    status = "healthy" if _agent is not None else "unhealthy"
    return {"status": status, "message": "Service is running" if status == "healthy" else "Service not initialized"}

@app.post("/reload")
async def reload_rag_system():
    try:
        initialize_rag_system()
        return {"message": "System RAG reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in reloading: {str(e)}")

