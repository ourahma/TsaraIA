import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Brain, Database, Zap, MessageCircle, ArrowDown, Search, FileText, ToolCase  } from 'lucide-react';


const ChatbotInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const chatSectionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToChat = () => {
    chatSectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Remplacez cette URL par l'URL de votre backend Python
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageToSend }),
      });

      if (!response.ok) {
        throw new Error('Erreur réseau');
      }

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.summary,  
        topic: data.topic,      
        sources: data.sources,  
        tools_used: data.tools_used, 
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Erreur:', error);
      
      // Message d'erreur de fallback
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Désolé, je ne peux pas répondre pour le moment. Vérifiez que le backend est en cours d\'exécution.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const TypingIndicator = () => (
    <div className="flex items-center space-x-1 p-3">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
      <span className="text-sm text-gray-200 ml-2">Le bot réfléchit...</span>
    </div>
  );
  // Composant pour afficher les réponses de recherche structurées
  const ResearchMessage = ({ message }) => (
    <div className="flex items-start space-x-3 animate-fade-in-up">
      <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
        <Bot className="w-5 h-5 text-white" />
      </div>
      
      <div className="max-w-lg bg-white/10 text-white border border-white/20 rounded-2xl rounded-bl-md p-4">
        {/* Topic */}
        {message.topic && (
          <div className="mb-3 pb-2 border-b border-white/20">
            <div className="flex items-center space-x-2 mb-1">
              <Search className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-blue-300 uppercase tracking-wide">Sujet de recherche</span>
            </div>
            <p className="text-sm font-medium text-blue-100">{message.topic}</p>
          </div>
        )}
        
        {/* Main Content */}
        <p className="text-sm leading-relaxed mb-4">{message.content}</p>
        
        {/* Tools Used */}
        {message.tools_used && message.tools_used.length > 0 && (
          <div className="mb-3">
            <div className="flex items-center space-x-2 mb-2">
              <ToolCase  className="w-4 h-4 text-green-400" />
              <span className="text-xs text-green-300 uppercase tracking-wide">Outils utilisés</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {message.tools_used.map((tool, index) => (
                <span key={index} className="px-2 py-1 bg-green-500/20 text-green-200 text-xs rounded-full border border-green-400/30">
                  {tool}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mb-3">
            <div className="flex items-center space-x-2 mb-2">
              <FileText className="w-4 h-4 text-yellow-400" />
              <span className="text-xs text-yellow-300 uppercase tracking-wide">Sources</span>
            </div>
            <div className="space-y-1">
              {message.sources.map((source, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-1 h-1 bg-yellow-400 rounded-full"></div>
                  <span className="text-xs text-yellow-200">{source}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Timestamp */}
        <p className="text-xs text-gray-400 mt-3 pt-2 border-t border-white/10">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
  return (
    <div className="min-h-screen ">
      {/* Banner Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        
        {/* Animated Background */}
        <div className="absolute inset-0">
          <img
            src="./background.png"
            alt="Background"
            className="w-full h-full object-cover absolute inset-0 z-0"
            style={{ opacity: 0.5 }}
          />
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-red-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
          <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-amber-900 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
          <div className="absolute bottom-1/4 left-1/2 w-64 h-64 bg-red-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
          <div className="animate-fade-in-up">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="w-24 h-24 p-5 bg-red-900 rounded-2xl flex items-center justify-center shadow-2xl">
                  
                  <img src="./logo.svg" className="text-dar-red"/>
                </div>
              </div>
            </div>
            
            <h1 className="text-6xl md:text-7xl font-bold text-dark-red mb-6 bg-gradient-to-r from-dark-red-500 via-purple-400 to-beige bg-clip-text">
              Tsara IA
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-900 mb-8 max-w-3xl mx-auto leading-relaxed ">
              Découvrez la puissance de l'intelligence artificielle avec notre système RAG
              <span className="text-dark-red font-semibold"> (Retrieval-Augmented Generation)</span>
            </p>

            <div className="grid md:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:-translate-y-2">
            <Database className="w-12 h-12 text-blue-400 mb-4 mx-auto" />
            <h3 className="text-lg font-semibold text-black mb-2">
              Base de connaissances officielle
            </h3>
            <p className="text-gray-700 text-sm">
              Les données proviennent directement des plateformes gouvernementales, assurant transparence et fiabilité.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:-translate-y-2">
            <Brain className="w-12 h-12 text-purple-400 mb-4 mx-auto" />
            <h3 className="text-lg font-semibold text-black mb-2">
              IA générative
            </h3>
            <p className="text-gray-700 text-sm">
              L’intelligence artificielle renforce la précision des informations et apporte des réponses fiables en temps réel.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:-translate-y-2">
            <MessageCircle className="w-12 h-12 text-pink-400 mb-4 mx-auto" />
            <h3 className="text-lg font-semibold text-black mb-2">
              Conversation fluide
            </h3>
            <p className="text-gray-700 text-sm">
              Toutes vos informations centralisées dans un espace unique, pour une expérience claire et intuitive.
            </p>
          </div>
        </div>


            <button
              onClick={scrollToChat}
              className="group bg-dark-red-main  text-white px-8 py-4 rounded-full font-semibold text-lg shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 transform hover:-translate-y-1 hover:scale-105"
            >
              Commencer la Conversation
              <ArrowDown className="w-5 h-5 ml-2 inline-block group-hover:animate-bounce" />
            </button>
          </div>
        </div>
      </section>

      {/* Chat Section */}
      <section ref={chatSectionRef} className="h-full bg-red-950 relative">
        <div className="min-w-4xl mx-auto px-6 py-12">
          <div className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
            {/* Chat Header */}
            <div className="bg-dark-red-main p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Assistant RAG</h2>
                  <p className="text-blue-100 text-sm">En ligne • Prêt à répondre</p>
                </div>
                <div className="ml-auto">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Messages Container */}
            <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gray-900/50">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <Bot className="w-16 h-16 text-gray-500 mx-auto mb-4 opacity-50" />
                  <p className="text-gray-200 text-lg">Commencez votre conversation...</p>
                  <p className="text-gray-300 text-sm mt-2">Posez-moi une question et j'utiliserai mon système RAG pour vous répondre</p>
                </div>
              )}

               {messages.map((message) => (
                message.type === 'user' ? (
                  <div key={message.id} className="flex items-start space-x-3 flex-row-reverse space-x-reverse animate-fade-in-up">
                    <div className="w-10 h-10 rounded-full bg-gradient-darkred-beige flex items-center justify-center">
                      <User className="w-5 h-5 text-dark" />
                    </div>
                    
                    <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl bg-red-900 text-white rounded-br-md">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <p className="text-xs mt-2 text-blue-100">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ) : (
                  <ResearchMessage key={message.id} message={message} />
                )
              ))}

              {isLoading && (
                <div className="flex items-start space-x-3 animate-fade-in-up">
                  <div className="w-10 h-10 rounded-full bg-gradient-darkred-beige flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white/10 border border-white/20 rounded-2xl rounded-bl-md">
                    <TypingIndicator />
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Section */}
            <div className="border-t border-white/10 p-6">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(e)}
                  placeholder="Tapez votre message..."
                  className="flex-1 border border-black rounded-2xl px-6 bg-white py-3 text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim()}
                  className="bg-gradient-to-r from-red-500 to-yellow-600 text-white p-3 rounded-2xl hover:from-red-600 hover:to-yellow-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 active:scale-95"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ChatbotInterface;