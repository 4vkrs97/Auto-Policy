import { cn } from "@/lib/utils";

export const ChatBubble = ({ message, avatarUrl }) => {
  const isBot = message.role === "assistant";
  
  return (
    <div 
      className={cn(
        "flex items-end gap-2",
        !isBot && "flex-row-reverse"
      )}
      data-testid={`chat-bubble-${message.role}`}
    >
      {isBot && avatarUrl && (
        <img 
          src={avatarUrl} 
          alt="Jiffy Jane" 
          className="w-8 h-8 rounded-xl bg-white object-cover flex-shrink-0"
        />
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
  );
};

export default ChatBubble;
