import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Send, ArrowLeft, Download, FileText, Check, X, LogOut, RefreshCw, Car, Shield, User, Briefcase, Calendar, Clock, AlertTriangle, Bot, Calculator, Cpu, CheckCircle, CreditCard, Wallet } from "lucide-react";
import { toast } from "sonner";
import ChatBubble from "@/components/chat/ChatBubble";
import TypingIndicator from "@/components/chat/TypingIndicator";
import CoverageCard from "@/components/cards/CoverageCard";
import QuoteCard from "@/components/cards/QuoteCard";
import PolicyCard from "@/components/cards/PolicyCard";
import DataFetchCard from "@/components/cards/DataFetchCard";
import VehicleSummaryCard from "@/components/cards/VehicleSummaryCard";
import PaymentGateway from "@/components/cards/PaymentGateway";
import PolicyPopup from "@/components/cards/PolicyPopup";
import AddonsCard from "@/components/cards/AddonsCard";

const INCOME_LOGO = "https://customer-assets.emergentagent.com/job_563e7fa0-9b63-4fef-a677-9b1ace8339d0/artifacts/d6i0a1n5_image.png";
const JIFFY_JANE = "https://customer-assets.emergentagent.com/job_563e7fa0-9b63-4fef-a677-9b1ace8339d0/artifacts/1czfonbv_image.png";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Agent configuration for the status panel
const AGENTS = [
  { key: "orchestrator", name: "Orchestrator", icon: Bot, color: "bg-orange-500" },
  { key: "intake", name: "Vehicle Agent", icon: Car, color: "bg-blue-500" },
  { key: "coverage", name: "Coverage Agent", icon: Shield, color: "bg-green-500" },
  { key: "driver_identity", name: "Identity Agent", icon: User, color: "bg-purple-500" },
  { key: "driver_eligibility", name: "Eligibility Agent", icon: CheckCircle, color: "bg-indigo-500" },
  { key: "telematics", name: "Telematics Agent", icon: Cpu, color: "bg-cyan-500" },
  { key: "risk_assessment", name: "Risk Agent", icon: Shield, color: "bg-amber-500" },
  { key: "pricing", name: "Pricing Agent", icon: Calculator, color: "bg-emerald-500" },
  { key: "payment", name: "Payment Agent", icon: CreditCard, color: "bg-violet-500" },
  { key: "document", name: "Document Agent", icon: FileText, color: "bg-rose-500" },
];

export const ChatPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [policyNumber, setPolicyNumber] = useState(null);
  const [currentAgent, setCurrentAgent] = useState("orchestrator");
  const [completedAgents, setCompletedAgents] = useState([]);
  const [showPaymentGateway, setShowPaymentGateway] = useState(false);
  const [showPolicyPopup, setShowPolicyPopup] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState(0);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    // Only scroll within the messages container, not the main page
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, []);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        if (sessionId) {
          const sessionRes = await fetch(`${API}/sessions/${sessionId}`);
          if (!sessionRes.ok) {
            throw new Error("Session not found");
          }
          const sessionData = await sessionRes.json();
          setSession(sessionData);
          setCurrentAgent(sessionData.current_agent || "orchestrator");
          if (sessionData.state?.policy_number) {
            setPolicyNumber(sessionData.state.policy_number);
          }

          const messagesRes = await fetch(`${API}/messages/${sessionId}`);
          if (messagesRes.ok) {
            const messagesData = await messagesRes.json();
            setMessages(messagesData);
            
            // Track completed agents from message history
            const agents = messagesData
              .filter(m => m.role === "assistant" && m.agent)
              .map(m => m.agent);
            setCompletedAgents([...new Set(agents)]);
            
            if (messagesData.length === 0) {
              const welcomeRes = await fetch(`${API}/welcome/${sessionId}`, {
                method: "POST"
              });
              if (welcomeRes.ok) {
                const welcomeMsg = await welcomeRes.json();
                setMessages([welcomeMsg]);
              }
            }
          }
        } else {
          const response = await fetch(`${API}/sessions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_agent: navigator.userAgent })
          });
          
          if (!response.ok) throw new Error("Failed to create session");
          
          const newSession = await response.json();
          setSession(newSession);
          navigate(`/chat/${newSession.id}`, { replace: true });

          const welcomeRes = await fetch(`${API}/welcome/${newSession.id}`, {
            method: "POST"
          });
          if (welcomeRes.ok) {
            const welcomeMsg = await welcomeRes.json();
            setMessages([welcomeMsg]);
          }
        }
      } catch (error) {
        console.error("Error initializing session:", error);
        toast.error("Failed to start chat session");
        navigate("/");
      }
    };

    initSession();
  }, [sessionId, navigate]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = async (content, quickReplyValue = null) => {
    if (!session || (!content.trim() && !quickReplyValue)) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: content.trim() || quickReplyValue,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const response = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: session.id,
          content: content.trim() || quickReplyValue,
          quick_reply_value: quickReplyValue
        })
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setIsTyping(false);
      setMessages(prev => [...prev, data.message]);
      setSession(prev => ({ ...prev, state: data.state, current_agent: data.current_agent }));
      setCurrentAgent(data.current_agent);
      
      // Track completed agents - only add valid agents from AGENTS list
      const validAgentKeys = AGENTS.map(a => a.key);
      if (data.current_agent && validAgentKeys.includes(data.current_agent) && !completedAgents.includes(data.current_agent)) {
        setCompletedAgents(prev => {
          const newAgents = [...prev, data.current_agent];
          // Filter to only include valid agents and remove duplicates
          return [...new Set(newAgents.filter(a => validAgentKeys.includes(a)))];
        });
      }
      
      if (data.state?.policy_number) {
        setPolicyNumber(data.state.policy_number);
      }
      
      // Check if we should show policy popup
      if (data.message?.show_policy_popup) {
        setShowPolicyPopup(true);
        setPolicyNumber(data.state?.policy_number);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setIsTyping(false);
      toast.error("Failed to send message. Please try again.");
    }
  };

  const handleQuickReply = (value, label) => {
    // Check if this is a payment gateway trigger
    if (value === "proceed_to_payment" || value === "open_payment_gateway") {
      setPaymentAmount(session?.state?.final_premium || 0);
      setShowPaymentGateway(true);
      return;
    }
    sendMessage(label, value);
  };

  const handlePaymentComplete = async (paymentMethod, paymentRef, policyNum) => {
    setShowPaymentGateway(false);
    setPolicyNumber(policyNum);
    setShowPolicyPopup(true);
    
    // Update local state
    setSession(prev => ({
      ...prev,
      state: {
        ...prev?.state,
        payment_completed: true,
        payment_method: paymentMethod,
        payment_reference: paymentRef,
        policy_number: policyNum,
        documents_ready: true
      }
    }));
    
    // Update current agent to document
    setCurrentAgent("document");
    const validAgentKeys = AGENTS.map(a => a.key);
    setCompletedAgents(prev => {
      const newAgents = [...prev];
      if (!newAgents.includes("payment")) newAgents.push("payment");
      if (!newAgents.includes("document")) newAgents.push("document");
      // Filter to only include valid agents and cap at AGENTS.length
      return [...new Set(newAgents.filter(a => validAgentKeys.includes(a)))].slice(0, AGENTS.length);
    });
    
    // Send a message to update the chat
    sendMessage("Payment completed", "payment_completed");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      sendMessage(inputValue);
    }
  };

  const handleDownloadPdf = async () => {
    if (!session) return;
    
    try {
      setIsLoading(true);
      const response = await fetch(`${API}/document/${session.id}/pdf`);
      if (!response.ok) throw new Error("Failed to generate PDF");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `policy_${session.state?.policy_number || "document"}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success("PDF downloaded successfully!");
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast.error("Failed to download PDF");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewQuote = () => {
    navigate("/");
  };

  const renderCards = (cards) => {
    if (!cards || cards.length === 0) return null;

    return cards.map((card, index) => {
      switch (card.type) {
        case "coverage_comparison":
        case "plan_comparison":
          return <CoverageCard key={index} card={card} onSelect={handleQuickReply} />;
        case "quote_summary":
          return <QuoteCard key={index} card={card} />;
        case "policy_document":
          return <PolicyCard key={index} card={card} onDownload={handleDownloadPdf} />;
        case "vehicle_fetch":
          return <DataFetchCard key={index} type="vehicle" data={card.data} />;
        case "vin_fetch":
          return <DataFetchCard key={index} type="vin" data={card.data} />;
        case "vehicle_summary":
          return <VehicleSummaryCard key={index} data={card.data} />;
        case "singpass_fetch":
          return <DataFetchCard key={index} type="singpass" data={card.data} />;
        case "risk_fetch":
          return <DataFetchCard key={index} type="risk" data={card.data} />;
        case "coverage_addons":
          return <AddonsCard key={index} card={card} sessionId={session?.id} onAddonsUpdated={() => {}} />;
        default:
          return null;
      }
    });
  };

  const lastAssistantMessage = messages.filter(m => m.role === "assistant").pop();

  // Get previous agent for each message
  const getPreviousAgent = (index) => {
    for (let i = index - 1; i >= 0; i--) {
      if (messages[i].role === "assistant" && messages[i].agent) {
        return messages[i].agent;
      }
    }
    return null;
  };

  return (
    <div className="chat-page" data-testid="chat-page">
      {/* Orange Header */}
      <header className="chat-header">
        <div className="chat-header-left">
          <img 
            src={INCOME_LOGO} 
            alt="Income" 
            className="income-logo"
          />
        </div>
        
        <div className="chat-header-center">
          <img 
            src={JIFFY_JANE} 
            alt="Jiffy Jane" 
            className="header-avatar"
            data-testid="chat-jiffy-avatar"
          />
          <span className="font-semibold text-white font-['Outfit']">Jiffy Jane</span>
        </div>

        <div className="chat-header-right">
          {policyNumber && (
            <div className="text-right text-sm">
              <div className="font-medium">Policy Holder</div>
              <div className="text-white/80 text-xs">{policyNumber}</div>
            </div>
          )}
          <button 
            onClick={handleNewQuote}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
            data-testid="new-quote-btn"
          >
            <LogOut className="w-5 h-5 text-white" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="chat-main">
        <div className="flex gap-6 w-full max-w-[1200px]">
          {/* Agent Status Panel */}
          <div className="hidden lg:block w-64 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-lg p-4 sticky top-6">
              <h3 className="font-semibold text-gray-900 font-['Outfit'] mb-4 flex items-center gap-2">
                <Bot className="w-5 h-5 text-orange-500" />
                Agent Pipeline
              </h3>
              <div className="space-y-2">
                {AGENTS.map((agent, index) => {
                  const Icon = agent.icon;
                  const isActive = currentAgent === agent.key;
                  const isCompleted = completedAgents.includes(agent.key);
                  
                  return (
                    <div 
                      key={agent.key}
                      className={`flex items-center gap-3 p-2.5 rounded-xl transition-all ${
                        isActive 
                          ? 'bg-orange-50 border-2 border-orange-300' 
                          : isCompleted 
                            ? 'bg-green-50 border border-green-200' 
                            : 'bg-gray-50 border border-gray-100'
                      }`}
                      data-testid={`agent-status-${agent.key}`}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        isActive ? agent.color : isCompleted ? 'bg-green-500' : 'bg-gray-300'
                      }`}>
                        {isCompleted && !isActive ? (
                          <Check className="w-4 h-4 text-white" />
                        ) : (
                          <Icon className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium truncate ${
                          isActive ? 'text-orange-700' : isCompleted ? 'text-green-700' : 'text-gray-500'
                        }`}>
                          {agent.name}
                        </div>
                        <div className="text-xs text-gray-400">
                          {isActive ? 'Active' : isCompleted ? 'Completed' : 'Pending'}
                        </div>
                      </div>
                      {isActive && (
                        <span className="flex h-2.5 w-2.5">
                          <span className="animate-ping absolute inline-flex h-2.5 w-2.5 rounded-full bg-orange-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-orange-500"></span>
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
              
              {/* Progress */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex justify-between text-xs text-gray-500 mb-2">
                  <span>Progress</span>
                  <span>{Math.min(100, Math.round((completedAgents.length / AGENTS.length) * 100))}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-orange-400 to-orange-600 transition-all duration-500"
                    style={{ width: `${Math.min(100, (completedAgents.length / AGENTS.length) * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Chat Card */}
          <div className="chat-card flex-1">
            {/* Policy Info Header */}
            <div className="card-header">
              <div className="policy-info">
                <span className="policy-type">
                  Type: Income Motor Insurance - {session?.state?.plan_name || 'Quote in Progress'}
                </span>
                <span className={`policy-status ${session?.state?.documents_ready ? 'active' : ''}`}>
                  Status: {session?.state?.documents_ready ? 'ACTIVE' : 'IN PROGRESS'}
                </span>
              </div>
              
              <button 
                className="primary-action-btn"
                onClick={handleNewQuote}
                data-testid="new-quote-header-btn"
              >
                <RefreshCw className="w-4 h-4" />
                Start New Quote
              </button>
            </div>

            {/* Messages Area */}
            <div className="messages-area" data-testid="messages-container">
              {messages.map((message, index) => (
                <div 
                  key={message.id || index} 
                  className="animate-slide-in"
                  style={{ animationDelay: `${Math.min(index * 0.05, 0.3)}s` }}
                >
                  <ChatBubble 
                    message={message} 
                    avatarUrl={message.role === "assistant" ? JIFFY_JANE : null}
                    previousAgent={getPreviousAgent(index)}
                  />
                  
                  {/* Render cards after assistant messages */}
                  {message.role === "assistant" && message.cards && (
                    <div className="ml-[52px] mt-2">
                      {renderCards(message.cards)}
                    </div>
                  )}
                  
                  {/* Render quick action buttons for last assistant message */}
                  {message.role === "assistant" && 
                   message === lastAssistantMessage && 
                   message.quick_replies && 
                   message.quick_replies.length > 0 &&
                   !isTyping && (
                    <div className="ml-[52px] mt-3">
                      <div className={message.show_brand_logos ? "brand-buttons-grid" : "action-buttons-grid"}>
                        {message.quick_replies.map((reply, idx) => {
                          const IconComponent = getIconForReply(reply.value);
                          const hasLogo = reply.logo && message.show_brand_logos;
                          
                          return (
                            <button
                              key={idx}
                              onClick={() => handleQuickReply(reply.value, reply.label)}
                              className={hasLogo ? "brand-button" : "action-button"}
                              data-testid={`quick-reply-${idx}`}
                            >
                              {hasLogo ? (
                                <>
                                  <div className="brand-logo-container">
                                    <img 
                                      src={reply.logo} 
                                      alt={reply.label} 
                                      className="brand-logo"
                                      onError={(e) => {
                                        e.target.style.display = 'none';
                                        e.target.nextSibling.style.display = 'flex';
                                      }}
                                    />
                                    <div className="brand-logo-fallback" style={{display: 'none'}}>
                                      {reply.label.charAt(0)}
                                    </div>
                                  </div>
                                  <span className="brand-name">{reply.label}</span>
                                </>
                              ) : (
                                <>
                                  <IconComponent className="w-4 h-4" />
                                  {reply.label}
                                </>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="animate-slide-in">
                  <div className="message-row">
                    <img 
                      src={JIFFY_JANE} 
                      alt="Jiffy Jane" 
                      className="message-avatar"
                    />
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form 
              onSubmit={handleSubmit}
              className="chat-input-container"
              data-testid="chat-input-form"
            >
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                className="chat-input-field"
                disabled={isLoading || isTyping}
                data-testid="chat-input"
              />
              <button
                type="submit"
                className="send-btn"
                disabled={!inputValue.trim() || isLoading || isTyping}
                data-testid="send-button"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </main>

      {/* Made with Emergent badge */}
      <div className="emergent-badge">
        <div className="w-5 h-5 rounded-full bg-[#F96302] flex items-center justify-center">
          <span className="text-white text-xs font-bold">E</span>
        </div>
        Made with Emergent
      </div>

      {/* Payment Gateway Modal */}
      {showPaymentGateway && (
        <PaymentGateway
          sessionId={session?.id}
          amount={paymentAmount}
          onClose={() => setShowPaymentGateway(false)}
          onPaymentComplete={handlePaymentComplete}
        />
      )}

      {/* Policy Generated Popup */}
      {showPolicyPopup && (
        <PolicyPopup
          policyNumber={policyNumber}
          onClose={() => setShowPolicyPopup(false)}
        />
      )}
    </div>
  );
};

// Helper function to get icon for quick reply
function getIconForReply(value) {
  const valueLower = value?.toLowerCase() || '';
  
  if (valueLower.includes('car')) return Car;
  if (valueLower.includes('motorcycle')) return Car;
  if (valueLower.includes('comprehensive') || valueLower.includes('third')) return Shield;
  if (valueLower.includes('singpass') || valueLower.includes('manual') || valueLower.includes('consent')) return User;
  if (valueLower.includes('premium') || valueLower.includes('classic')) return Briefcase;
  if (valueLower.includes('claim') || valueLower.includes('no_claims')) return AlertTriangle;
  if (valueLower.includes('driver') || valueLower.includes('none') || valueLower.includes('add')) return User;
  if (valueLower.includes('telematics') || valueLower.includes('save')) return Clock;
  if (valueLower.includes('confirm') || valueLower.includes('accept')) return Check;
  if (valueLower.includes('download') || valueLower.includes('pdf')) return Download;
  if (valueLower.includes('view') || valueLower.includes('quote')) return FileText;
  if (valueLower.includes('payment') || valueLower.includes('proceed')) return CreditCard;
  
  return Calendar;
}

export default ChatPage;
