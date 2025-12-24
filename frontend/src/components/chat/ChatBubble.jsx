import { cn } from "@/lib/utils";
import { Bot, Car, Shield, User, Calculator, FileText, Cpu } from "lucide-react";

const AGENT_CONFIG = {
  orchestrator: { name: "Jiffy Jane", icon: Bot, color: "bg-orange-500" },
  intake: { name: "Vehicle Agent", icon: Car, color: "bg-blue-500" },
  coverage: { name: "Coverage Agent", icon: Shield, color: "bg-green-500" },
  driver_identity: { name: "Identity Agent", icon: User, color: "bg-purple-500" },
  driver_eligibility: { name: "Eligibility Agent", icon: User, color: "bg-indigo-500" },
  telematics: { name: "Telematics Agent", icon: Cpu, color: "bg-cyan-500" },
  risk_assessment: { name: "Risk Agent", icon: Shield, color: "bg-amber-500" },
  pricing: { name: "Pricing Agent", icon: Calculator, color: "bg-emerald-500" },
  document: { name: "Document Agent", icon: FileText, color: "bg-rose-500" },
};

export const ChatBubble = ({ message, avatarUrl }) => {
  const isBot = message.role === "assistant";
  const agentKey = message.agent || "orchestrator";
  const agent = AGENT_CONFIG[agentKey] || AGENT_CONFIG.orchestrator;
  const AgentIcon = agent.icon;
  
  return (
    <div 
      className={cn(
        "flex items-end gap-3",
        !isBot && "flex-row-reverse"
      )}
      data-testid={`chat-bubble-${message.role}`}
    >
      {isBot && (
        <div className="flex flex-col items-center gap-1">
          {avatarUrl ? (
            <img 
              src={avatarUrl} 
              alt={agent.name}
              className="w-10 h-10 rounded-xl bg-white object-cover flex-shrink-0"
            />
          ) : (
            <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", agent.color)}>
              <AgentIcon className="w-5 h-5 text-white" />
            </div>
          )}
        </div>
      )}
      
      <div className="flex flex-col gap-1 max-w-[70%] md:max-w-[60%] lg:max-w-[50%]">
        {isBot && (
          <div className="flex items-center gap-2 ml-1">
            <span className={cn("w-2 h-2 rounded-full", agent.color)}></span>
            <span className="text-xs font-medium text-gray-500">{agent.name}</span>
          </div>
        )}
        <div 
          className={cn(
            "message-bubble",
            isBot ? "bot" : "user"
          )}
        >
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatBubble;
