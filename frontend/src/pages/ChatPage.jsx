import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Send, ArrowLeft, Download, FileText, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import ChatBubble from "@/components/chat/ChatBubble";
import QuickReplies from "@/components/chat/QuickReplies";
import TypingIndicator from "@/components/chat/TypingIndicator";
import CoverageCard from "@/components/cards/CoverageCard";
import QuoteCard from "@/components/cards/QuoteCard";
import PolicyCard from "@/components/cards/PolicyCard";
import DataFetchCard from "@/components/cards/DataFetchCard";

const INCOME_LOGO = "https://customer-assets.emergentagent.com/job_563e7fa0-9b63-4fef-a677-9b1ace8339d0/artifacts/ywmks2cv_image.png";
const JIFFY_JANE = "https://customer-assets.emergentagent.com/job_563e7fa0-9b63-4fef-a677-9b1ace8339d0/artifacts/1czfonbv_image.png";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ChatPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        if (sessionId) {
          // Get existing session
          const sessionRes = await fetch(`${API}/sessions/${sessionId}`);
          if (!sessionRes.ok) {
            throw new Error("Session not found");
          }
          const sessionData = await sessionRes.json();
          setSession(sessionData);

          // Get existing messages
          const messagesRes = await fetch(`${API}/messages/${sessionId}`);
          if (messagesRes.ok) {
            const messagesData = await messagesRes.json();
            setMessages(messagesData);
            
            // If no messages, get welcome message
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
          // Create new session
          const response = await fetch(`${API}/sessions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_agent: navigator.userAgent })
          });
          
          if (!response.ok) throw new Error("Failed to create session");
          
          const newSession = await response.json();
          setSession(newSession);
          navigate(`/chat/${newSession.id}`, { replace: true });

          // Get welcome message
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

  // Scroll to bottom when messages change
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
      
      // Small delay to show typing indicator
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setIsTyping(false);
      setMessages(prev => [...prev, data.message]);
      setSession(prev => ({ ...prev, state: data.state, current_agent: data.current_agent }));
    } catch (error) {
      console.error("Error sending message:", error);
      setIsTyping(false);
      toast.error("Failed to send message. Please try again.");
    }
  };

  const handleQuickReply = (value, label) => {
    sendMessage(label, value);
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
        default:
          return null;
      }
    });
  };

  const lastAssistantMessage = messages.filter(m => m.role === "assistant").pop();

  return (
    <div className="chat-container" data-testid="chat-page">
      {/* Header */}
      <header className="flex items-center gap-4 px-6 py-4 bg-[#F96302] text-white sticky top-0 z-50">
        <Button
          variant="ghost"
          size="icon"
          className="text-white hover:bg-white/20 -ml-2"
          onClick={() => navigate("/")}
          data-testid="back-button"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        
        <img 
          src={INCOME_LOGO} 
          alt="Income" 
          className="h-8"
        />
        
        <div className="flex-1 text-center">
          <h1 className="font-semibold text-lg font-['Outfit']">Motor Insurance</h1>
          <p className="text-sm text-white/80">Powered by AI Agents</p>
        </div>

        <img 
          src={JIFFY_JANE} 
          alt="Jiffy Jane" 
          className="w-12 h-12 rounded-xl bg-white object-cover"
          data-testid="chat-jiffy-avatar"
        />
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 md:px-[10%] lg:px-[20%]" data-testid="messages-container">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <div 
              key={message.id || index} 
              className="animate-slide-in"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <ChatBubble 
                message={message} 
                avatarUrl={message.role === "assistant" ? JIFFY_JANE : null}
              />
              
              {/* Render cards after assistant messages */}
              {message.role === "assistant" && message.cards && (
                <div className="mt-3 ml-14">
                  {renderCards(message.cards)}
                </div>
              )}
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="animate-slide-in">
              <div className="flex items-end gap-2">
                <img 
                  src={JIFFY_JANE} 
                  alt="Jiffy Jane" 
                  className="w-10 h-10 rounded-xl bg-white object-cover"
                />
                <TypingIndicator />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Replies */}
      {lastAssistantMessage?.quick_replies && !isTyping && (
        <div className="px-6 md:px-[10%] lg:px-[20%]">
          <div className="max-w-4xl mx-auto">
            <QuickReplies 
              replies={lastAssistantMessage.quick_replies}
              onSelect={handleQuickReply}
            />
          </div>
        </div>
      )}

      {/* Input Area */}
      <form 
        onSubmit={handleSubmit}
        className="chat-input-area flex items-center gap-3"
        data-testid="chat-input-form"
      >
        <div className="flex-1 max-w-4xl mx-auto flex items-center gap-3 w-full">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="chat-input flex-1"
            disabled={isLoading || isTyping}
            data-testid="chat-input"
          />
          <button
            type="submit"
            className="send-button"
            disabled={!inputValue.trim() || isLoading || isTyping}
            data-testid="send-button"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPage;
