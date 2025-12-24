export const TypingIndicator = () => {
  return (
    <div 
      className="message-bubble bot inline-flex items-center gap-1"
      data-testid="typing-indicator"
    >
      <div className="typing-dot bg-gray-400"></div>
      <div className="typing-dot bg-gray-400"></div>
      <div className="typing-dot bg-gray-400"></div>
    </div>
  );
};

export default TypingIndicator;
