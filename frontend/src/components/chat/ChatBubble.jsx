import { cn } from "@/lib/utils";
import { Bot, Car, Shield, User, Calculator, FileText, Cpu, CheckCircle, ArrowRight, Zap } from "lucide-react";

const AGENT_CONFIG = {
  orchestrator: { name: "Orchestrator Agent", shortName: "Jiffy Jane", icon: Bot, color: "bg-orange-500", textColor: "text-orange-600" },
  intake: { name: "Vehicle Agent", shortName: "Vehicle Agent", icon: Car, color: "bg-blue-500", textColor: "text-blue-600" },
  coverage: { name: "Coverage Agent", shortName: "Coverage Agent", icon: Shield, color: "bg-green-500", textColor: "text-green-600" },
  driver_identity: { name: "Identity Agent", shortName: "Identity Agent", icon: User, color: "bg-purple-500", textColor: "text-purple-600" },
  driver_eligibility: { name: "Eligibility Agent", shortName: "Eligibility Agent", icon: CheckCircle, color: "bg-indigo-500", textColor: "text-indigo-600" },
  telematics: { name: "Telematics Agent", shortName: "Telematics Agent", icon: Cpu, color: "bg-cyan-500", textColor: "text-cyan-600" },
  risk_assessment: { name: "Risk Assessment Agent", shortName: "Risk Agent", icon: Shield, color: "bg-amber-500", textColor: "text-amber-600" },
  pricing: { name: "Pricing Agent", shortName: "Pricing Agent", icon: Calculator, color: "bg-emerald-500", textColor: "text-emerald-600" },
  document: { name: "Document Agent", shortName: "Document Agent", icon: FileText, color: "bg-rose-500", textColor: "text-rose-600" },
};

export const AgentHandoff = ({ fromAgent, toAgent }) => {
  const from = AGENT_CONFIG[fromAgent] || AGENT_CONFIG.orchestrator;
  const to = AGENT_CONFIG[toAgent] || AGENT_CONFIG.orchestrator;
  const FromIcon = from.icon;
  const ToIcon = to.icon;

  return (
    <div className="flex items-center justify-center my-4 animate-fade-in" data-testid="agent-handoff">
      <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-4 py-2 shadow-sm">
        <div className={cn("w-6 h-6 rounded-full flex items-center justify-center", from.color)}>
          <FromIcon className="w-3 h-3 text-white" />
        </div>
        <span className="text-xs font-medium text-gray-500">{from.shortName}</span>
        <ArrowRight className="w-4 h-4 text-gray-400" />
        <div className={cn("w-6 h-6 rounded-full flex items-center justify-center", to.color)}>
          <ToIcon className="w-3 h-3 text-white" />
        </div>
        <span className="text-xs font-medium text-gray-700">{to.shortName}</span>
        <Zap className="w-3 h-3 text-yellow-500" />
      </div>
    </div>
  );
};

export const AgentBadge = ({ agent, isActive = false }) => {
  const config = AGENT_CONFIG[agent] || AGENT_CONFIG.orchestrator;
  const Icon = config.icon;

  return (
    <div 
      className={cn(
        "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
        isActive 
          ? `${config.color} text-white shadow-lg` 
          : "bg-gray-100 text-gray-600"
      )}
      data-testid={`agent-badge-${agent}`}
    >
      <Icon className="w-3 h-3" />
      {config.name}
      {isActive && (
        <span className="flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-white opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
        </span>
      )}
    </div>
  );
};

export const ChatBubble = ({ message, avatarUrl, previousAgent }) => {
  const isBot = message.role === "assistant";
  const agentKey = message.agent || "orchestrator";
  const agent = AGENT_CONFIG[agentKey] || AGENT_CONFIG.orchestrator;
  const Icon = agent.icon;
  
  // Check if agent changed from previous message
  const showHandoff = isBot && previousAgent && previousAgent !== agentKey;
  
  return (
    <>
      {/* Agent Handoff Indicator */}
      {showHandoff && (
        <AgentHandoff fromAgent={previousAgent} toAgent={agentKey} />
      )}
      
      <div 
        className={cn(
          "message-row",
          !isBot && "user"
        )}
        data-testid={`chat-bubble-${message.role}`}
      >
        {isBot && avatarUrl && (
          <img 
            src={avatarUrl} 
            alt={agent.name}
            className="message-avatar"
          />
        )}
        
        <div className="message-content">
          {isBot && (
            <div className="flex items-center gap-2 mb-1.5">
              <div className={cn("w-5 h-5 rounded-full flex items-center justify-center", agent.color)}>
                <Icon className="w-3 h-3 text-white" />
              </div>
              <span className={cn("text-sm font-semibold", agent.textColor)}>
                {agent.name}
              </span>
              <span className="text-xs text-gray-400">• Active</span>
            </div>
          )}
          <div 
            className={cn(
              "message-bubble",
              isBot ? "bot" : "user"
            )}
          >
            <p className="whitespace-pre-wrap m-0">
              {message.content}
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default ChatBubble;
