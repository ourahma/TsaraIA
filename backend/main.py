from dotenv import load_dotenv
from langchain.agents import create_tool_calling_agent, AgentExecutor
from src.prompt import prompt,parser
from src.rag import create_rag_chain, load_documents, split_documents, create_vectorstore
import os
from sentence_transformers import SentenceTransformer

load_dotenv()

def main(query:str):
    docs = load_documents()
    chunks = split_documents(docs)
    db = create_vectorstore(chunks)
    tool,llm = create_rag_chain(db)
    
    agent = create_tool_calling_agent(llm,tools=[],prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[tool], verbose=True)
    raw_response = agent_executor.invoke({"query": query, "chat_history": []})
    print(raw_response)
    try:
        structured_response = parser.parse(raw_response.get("output",""))
        return structured_response
    except Exception as e:
        print("$"*100)
        print(f"Error parsing response: {e}")

 
if __name__ == "__main__":
   while True:
       user_input = input("Quelle question avez vous ? (tapez (q, quiet, exit) pour quitter) ")
       if user_input.lower() in ["quit","q","exit"]:
           break
       
       response = main(user_input)
       print("La réponse d'Agent : ", response)
