import { cn } from "@/lib/utils";
import { Bot, Car, Shield, User, Calculator, FileText, Cpu, CheckCircle } from "lucide-react";

const AGENT_CONFIG = {
  orchestrator: { name: "Jiffy Jane", icon: Bot, color: "text-orange-500" },
  intake: { name: "Vehicle Agent", icon: Car, color: "text-blue-500" },
  coverage: { name: "Coverage Agent", icon: Shield, color: "text-green-500" },
  driver_identity: { name: "Identity Agent", icon: User, color: "text-purple-500" },
  driver_eligibility: { name: "Eligibility Agent", icon: CheckCircle, color: "text-indigo-500" },
  telematics: { name: "Telematics Agent", icon: Cpu, color: "text-cyan-500" },
  risk_assessment: { name: "Risk Agent", icon: Shield, color: "text-amber-500" },
  pricing: { name: "Pricing Agent", icon: Calculator, color: "text-emerald-500" },
  document: { name: "Document Agent", icon: FileText, color: "text-rose-500" },
};

export const ChatBubble = ({ message, avatarUrl }) => {
  const isBot = message.role === "assistant";
  const agentKey = message.agent || "orchestrator";
  const agent = AGENT_CONFIG[agentKey] || AGENT_CONFIG.orchestrator;
  
  return (
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
          <div className={cn("message-sender", agent.color)}>
            {agent.name}
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
  );
};

export default ChatBubble;
