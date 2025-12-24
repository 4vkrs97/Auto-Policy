export const QuickReplies = ({ replies, onSelect }) => {
  if (!replies || replies.length === 0) return null;

  return (
    <div 
      className="px-4 py-3 bg-white/50 backdrop-blur-sm border-t border-[#E5E5EA]"
      data-testid="quick-replies-container"
    >
      <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-1">
        {replies.map((reply, index) => (
          <button
            key={index}
            onClick={() => onSelect(reply.value, reply.label)}
            className="quick-reply-btn"
            data-testid={`quick-reply-${index}`}
          >
            {reply.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickReplies;
