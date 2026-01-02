import { useEffect, useState } from "react";
import { Check, X, FileText, Download, PartyPopper } from "lucide-react";

const PolicyPopup = ({ policyNumber, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation after mount
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  return (
    <div 
      className={`fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 transition-opacity duration-300 ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
      onClick={handleClose}
    >
      <div 
        className={`bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden transform transition-all duration-500 ${
          isVisible ? "scale-100 translate-y-0" : "scale-75 translate-y-10"
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Confetti Animation Background */}
        <div className="relative bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 px-4 py-5 overflow-hidden">
          {/* Animated Confetti Particles */}
          <div className="absolute inset-0 overflow-hidden">
            {[...Array(15)].map((_, i) => (
              <div
                key={i}
                className="absolute animate-confetti"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `-10%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${2 + Math.random() * 2}s`
                }}
              >
                <div 
                  className={`w-2 h-2 ${
                    ['bg-yellow-300', 'bg-green-300', 'bg-blue-300', 'bg-pink-300', 'bg-purple-300'][i % 5]
                  } rounded-sm transform rotate-45`}
                />
              </div>
            ))}
          </div>

          {/* Close Button */}
          <button
            onClick={handleClose}
            className="absolute top-3 right-3 text-white/80 hover:text-white transition-colors z-10"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Success Icon */}
          <div className="relative flex justify-center mb-3">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg animate-bounce-once">
              <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center">
                <Check className="w-8 h-8 text-green-500" strokeWidth={3} />
              </div>
            </div>
          </div>

          {/* Title */}
          <div className="relative text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <PartyPopper className="w-5 h-5 text-yellow-200 animate-wiggle" />
              <h2 className="text-xl font-bold text-white font-['Outfit']">
                Congratulations!
              </h2>
              <PartyPopper className="w-5 h-5 text-yellow-200 animate-wiggle" style={{ transform: 'scaleX(-1)' }} />
            </div>
            <p className="text-white/90 text-sm">Your Policy Has Been Generated</p>
          </div>
        </div>

        {/* Policy Details */}
        <div className="p-4">
          {/* Policy Number Card */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200 mb-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-9 h-9 bg-orange-100 rounded-lg flex items-center justify-center">
                <FileText className="w-4 h-4 text-orange-500" />
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Policy Number</p>
                <p className="text-xl font-bold text-gray-900 font-['Outfit'] tracking-wide">
                  {policyNumber}
                </p>
              </div>
            </div>
            <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent my-2" />
            <p className="text-xs text-gray-500 text-center">
              Your policy is now active and coverage begins immediately
            </p>
          </div>

          {/* Info Message */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 bg-green-100 rounded flex items-center justify-center flex-shrink-0 mt-0.5">
                <Check className="w-3 h-3 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-green-800 font-medium">Policy documents sent!</p>
                <p className="text-xs text-green-600 mt-0.5">
                  A confirmation email has been sent to your registered email address.
                </p>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={handleClose}
            className="w-full py-3 bg-orange-500 text-white rounded-lg font-semibold hover:bg-orange-600 transition-colors shadow-md shadow-orange-200"
          >
            Continue
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(400px) rotate(720deg);
            opacity: 0;
          }
        }
        .animate-confetti {
          animation: confetti linear infinite;
        }
        @keyframes wiggle {
          0%, 100% { transform: rotate(-10deg); }
          50% { transform: rotate(10deg); }
        }
        .animate-wiggle {
          animation: wiggle 0.5s ease-in-out infinite;
        }
        @keyframes bounce-once {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-bounce-once {
          animation: bounce-once 0.6s ease-out;
        }
      `}</style>
    </div>
  );
};

export default PolicyPopup;
