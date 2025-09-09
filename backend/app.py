import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_tool_calling_agent, AgentExecutor
from src.prompt import prompt, parser
from src.rag import create_rag_chain, load_documents, split_documents, create_vectorstore
import os
from sentence_transformers import SentenceTransformer
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Assistant RAG Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 4px solid #764ba2;
    }
    
    .assistant-message {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-left: 4px solid #f5576c;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    .status-loading {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    .metrics-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        min-width: 120px;
    }
</style>
""", unsafe_allow_html=True)

# Chargement des variables d'environnement
load_dotenv()

def initialize_rag_system():
    """Initialise le système RAG avec cache Streamlit"""
    with st.spinner("🔄 Initialisation du système RAG..."):
        try:
            docs = load_documents()
            chunks = split_documents(docs)
            db = create_vectorstore(chunks)
            tool, llm = create_rag_chain(db)
            
            # Configuration de l'agent
            agent = create_tool_calling_agent(llm, tools=[], prompt=prompt)
            agent_executor = AgentExecutor(agent=agent, tools=[tool], verbose=False)
            
            return agent_executor, len(docs), len(chunks)
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation: {str(e)}")
            return None, 0, 0

@st.cache_resource
def get_rag_system():
    """Cache le système RAG pour éviter de le recharger à chaque interaction"""
    return initialize_rag_system()

def process_query(agent_executor, query):
    """Traite une requête avec l'agent RAG"""
    try:
        with st.spinner("🧠 Traitement de votre question..."):
            start_time = time.time()
            raw_response = agent_executor.invoke({"query": query, "chat_history": []})
            processing_time = time.time() - start_time
            
        try:
            structured_response = parser.parse(raw_response.get("output", ""))
            return structured_response, processing_time, True
        except Exception as parse_error:
            st.warning("⚠️ Erreur de parsing, retour de la réponse brute")
            return raw_response.get("output", "Aucune réponse disponible"), processing_time, False
            
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement: {str(e)}")
        return None, 0, False

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Assistant RAG Intelligence</h1>
        <p>Posez vos questions et obtenez des réponses intelligentes basées sur vos documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour les informations système
    with st.sidebar:
        st.header("📊 Informations Système")
        
        # Initialisation du système RAG
        if 'rag_system_initialized' not in st.session_state:
            with st.status("Initialisation du système RAG..."):
                agent_executor, num_docs, num_chunks = get_rag_system()
                if agent_executor:
                    st.session_state.agent_executor = agent_executor
                    st.session_state.num_docs = num_docs
                    st.session_state.num_chunks = num_chunks
                    st.session_state.rag_system_initialized = True
                    st.success("✅ Système initialisé avec succès!")
                else:
                    st.error("❌ Échec de l'initialisation")
                    return
        
        # Métriques
        if st.session_state.get('rag_system_initialized', False):
            st.metric("📄 Documents chargés", st.session_state.num_docs)
            st.metric("📝 Chunks créés", st.session_state.num_chunks)
            st.metric("💬 Questions posées", len(st.session_state.get('chat_history', [])))
        
        # Section configuration
        st.header("⚙️ Configuration")
        show_raw_response = st.checkbox("Afficher la réponse brute", value=False)
        show_processing_time = st.checkbox("Afficher le temps de traitement", value=True)
        
        # Bouton pour effacer l'historique
        if st.button("🗑️ Effacer l'historique", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

    # Vérification de l'initialisation
    if not st.session_state.get('rag_system_initialized', False):
        st.error("❌ Le système RAG n'est pas initialisé. Veuillez actualiser la page.")
        return

    # Initialisation de l'historique de chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Interface principale de chat
    st.header("💬 Interface de Chat")
    
    # Zone de saisie de la question
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "Posez votre question ici:",
                placeholder="Ex: Quelle est la définition de...",
                key="question_input"
            )
        
        with col2:
            ask_button = st.button("🚀 Poser la question", type="primary")
    
    # Traitement de la question
    if (ask_button or user_question) and user_question.strip():
        if user_question.strip():
            # Ajout de la question à l'historique
            st.session_state.chat_history.append({
                "type": "user",
                "content": user_question,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Traitement de la requête
            response, processing_time, parse_success = process_query(
                st.session_state.agent_executor, 
                user_question
            )
            
            if response:
                # Ajout de la réponse à l'historique
                st.session_state.chat_history.append({
                    "type": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "processing_time": processing_time,
                    "parse_success": parse_success
                })
            
            # Effacer le champ de saisie
            st.session_state.question_input = ""

    # Affichage de l'historique de chat
    if st.session_state.chat_history:
        st.header("📝 Historique des Conversations")
        
        # Affichage en ordre inverse (le plus récent en haut)
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            if message["type"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Vous ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
            else:  # assistant message
                parsing_indicator = "✅ Parsé" if message.get('parse_success', False) else "⚠️ Brut"
                time_info = f" • ⏱️ {message.get('processing_time', 0):.2f}s" if show_processing_time else ""
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant ({message['timestamp']}) {parsing_indicator}{time_info}:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # Afficher la réponse brute si demandé
                if show_raw_response and not message.get('parse_success', False):
                    with st.expander("🔍 Détails de la réponse"):
                        st.text(message['content'])
    
    else:
        # Message d'accueil
        st.info("👋 Bienvenue! Posez votre première question pour commencer la conversation.")
        
        # Suggestions de questions
        st.subheader("💡 Suggestions de questions")
        col1, col2, col3 = st.columns(3)
        
        suggestion_questions = [
            "Qu'est-ce que l'intelligence artificielle ?",
            "Expliquez-moi le concept de...",
            "Quelles sont les principales caractéristiques de..."
        ]
        
        for i, (col, suggestion) in enumerate(zip([col1, col2, col3], suggestion_questions)):
            with col:
                if st.button(f"💭 {suggestion}", key=f"suggestion_{i}"):
                    st.session_state.question_input = suggestion
                    st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px;'>
        🤖 Powered by LangChain & Streamlit | 
        📚 RAG (Retrieval-Augmented Generation) | 
        ⚡ Intelligence Artificielle
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()