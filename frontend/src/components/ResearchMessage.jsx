import {
  MapPinCheck,
  PhoneForwarded,
  Mail,
  Globe,
  Bot,
  ToolCase,
  FileText,
  Search,
  Building,
} from "lucide-react";

// Composant pour afficher les entités
const EntityContact = ({ entity, index }) => (
  <div className="bg-white/5 rounded-lg p-4 border border-white/10 mb-3">
    <div className="flex items-start justify-between mb-2">
      <h4 className="font-semibold text-white text-sm">
        {index + 1}. {entity.name}
      </h4>
      {entity.type && (
        <span className="px-2 py-1 bg-purple-500/20 text-purple-200 text-xs rounded-full">
          {entity.type}
        </span>
      )}
    </div>

    <div className="space-y-2 text-sm">
      {entity.address && (
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-blue-400 rounded-full flex items-center justify-center p-4 mx-2">
            <span className="text-xs">
              <MapPinCheck className="text-white " />
            </span>
          </div>
          <span className="text-blue-200">{entity.address}</span>
        </div>
      )}

      {entity.phone && (
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-400 rounded-full flex items-center justify-center  p-4 mx-2">
            <span className="text-xs">
              <PhoneForwarded className="text-white" />
            </span>
          </div>
          <a
            href={`tel:${entity.phone}`}
            className="text-green-200 hover:text-green-100 underline"
          >
            {entity.phone}
          </a>
        </div>
      )}

      {entity.email && (
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-yellow-400 rounded-full flex items-center justify-center  p-4 mx-2">
            <span className="text-xs">
              <Mail className="text-white" />
            </span>
          </div>
          <a
            href={`mailto:${entity.email}`}
            className="text-yellow-200 hover:text-yellow-100 underline"
          >
            {entity.email}
          </a>
        </div>
      )}

      {entity.website && (
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-400 rounded-full flex items-center justify-center  p-4 mx-2">
            <span className="text-xs">
              <Globe className="text-white" />
            </span>
          </div>
          <a
            href={entity.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-red-200 hover:text-red-100 underline break-all"
          >
            {entity.website}
          </a>
        </div>
      )}
    </div>
  </div>
);

const ResearchMessage = ({ message }) => (
  <div className="flex items-start space-x-3 animate-fade-in-up">
    <div className="w-10 h-10 rounded-full bg-gradient-darkred-beige flex items-center justify-center">
      <Bot className="w-5 h-5 text-white" />
    </div>

    <div className="max-w-lg bg-white/10 text-white border border-white/20 rounded-2xl rounded-bl-md p-4">
      {/* Topic */}
      {message.topic && (
        <div className="mb-3 pb-2 border-b border-white/20">
          <div className="flex items-center space-x-2 mb-1">
            <Search className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-blue-300 uppercase tracking-wide">
              Sujet de recherche
            </span>
          </div>
          <p className="text-sm font-medium text-blue-100">{message.topic}</p>
        </div>
      )}

      {/* Main Content */}
      <p className="text-sm leading-relaxed mb-4">{message.content}</p>

      {/* Entities */}
      {message.entities && message.entities.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center space-x-2 mb-3">
            <div className="w-4 h-4 bg-red-900 rounded-full flex items-center justify-center  p-4 mx-2">
              <span className="text-xs">
                <Building className="text-white" />
              </span>
            </div>
            <span className="text-xs text-purple-300 uppercase tracking-wide">
              Entités trouvées ({message.entities.length})
            </span>
          </div>
          <div className="space-y-2">
            {message.entities.map((entity, index) => (
              <EntityContact key={index} entity={entity} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* Tools Used */}
      {message.tools_used && message.tools_used.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center space-x-2 mb-2">
            <ToolCase className="w-4 h-4 text-green-400" />
            <span className="text-xs text-green-300 uppercase tracking-wide">
              Outils utilisés
            </span>
          </div>
          <div className="flex flex-wrap gap-1">
            {message.tools_used.map((tool, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-green-500/20 text-green-200 text-xs rounded-full border border-green-400/30"
              >
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
            <span className="text-xs text-yellow-300 uppercase tracking-wide">
              Sources
            </span>
          </div>
          <div className="space-y-1">
            {message.sources.map((source, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-yellow-400 rounded-full"></div>
                <span className="text-xs text-yellow-200 break-words">
                  {source}
                </span>
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
export default ResearchMessage;
