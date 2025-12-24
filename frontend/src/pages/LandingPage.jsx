import { useNavigate } from "react-router-dom";
import { Car, Shield, FileText, Clock, ChevronRight, Zap } from "lucide-react";

const INCOME_LOGO = "https://customer-assets.emergentagent.com/job_563e7fa0-9b63-4fef-a677-9b1ace8339d0/artifacts/ywmks2cv_image.png";
const JIFFY_JANE = "https://customer-assets.emergentagent.com/job_563e7fa0-9b63-4fef-a677-9b1ace8339d0/artifacts/1czfonbv_image.png";

const features = [
  {
    icon: Clock,
    title: "Quick Quote",
    description: "Get your insurance quote in under 5 minutes"
  },
  {
    icon: Shield,
    title: "Comprehensive Coverage",
    description: "Choose from Third Party or Full Coverage options"
  },
  {
    icon: Car,
    title: "Car & Motorcycle",
    description: "Coverage for all types of motor vehicles"
  },
  {
    icon: FileText,
    title: "Instant Documents",
    description: "Download your policy documents immediately"
  }
];

export const LandingPage = () => {
  const navigate = useNavigate();

  const handleStartChat = async () => {
    try {
      const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
      const response = await fetch(`${API}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_agent: navigator.userAgent })
      });
      
      if (!response.ok) throw new Error("Failed to create session");
      
      const session = await response.json();
      navigate(`/chat/${session.id}`);
    } catch (error) {
      console.error("Error starting chat:", error);
      navigate("/chat");
    }
  };

  return (
    <div className="landing-hero" data-testid="landing-page">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 md:px-8">
        <img 
          src={INCOME_LOGO} 
          alt="Income Insurance" 
          className="h-10 object-contain"
          data-testid="income-logo"
        />
        <button
          onClick={handleStartChat}
          className="flex items-center gap-2 text-[#F96302] hover:bg-orange-50 px-4 py-2 rounded-full transition-colors font-medium"
          data-testid="header-get-quote-btn"
        >
          Get Quote
          <ChevronRight className="w-4 h-4" />
        </button>
      </header>

      {/* Hero Section */}
      <main className="px-6 md:px-8 pt-12 md:pt-20 pb-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Jiffy Jane Avatar */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <img 
                src={JIFFY_JANE} 
                alt="Jiffy Jane" 
                className="jiffy-avatar-large"
                data-testid="jiffy-jane-avatar"
              />
              <div className="absolute -bottom-2 -right-2 bg-[#F96302] text-white text-xs font-semibold px-3 py-1 rounded-full shadow-lg flex items-center gap-1">
                <Zap className="w-3 h-3" />
                Online
              </div>
            </div>
          </div>

          {/* Hero Text */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#1F2937] mb-4 tracking-tight font-['Outfit']">
            Hi, I'm <span className="text-[#F96302]">Jiffy Jane!</span>
          </h1>
          <p className="text-lg md:text-xl text-[#6B7280] mb-10 max-w-2xl mx-auto leading-relaxed">
            Your friendly motor insurance assistant. Let me help you find the perfect coverage for your car or motorcycle in Singapore.
          </p>

          {/* CTA Button */}
          <button
            onClick={handleStartChat}
            className="start-button mb-16"
            data-testid="start-chat-btn"
          >
            Chat with Jiffy Jane
          </button>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((feature, index) => (
              <div 
                key={index} 
                className="feature-card text-left"
                data-testid={`feature-card-${index}`}
              >
                <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-[#F96302]" />
                </div>
                <h3 className="font-semibold text-[#1F2937] mb-2 font-['Outfit']">
                  {feature.title}
                </h3>
                <p className="text-sm text-[#6B7280]">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="max-w-3xl mx-auto mt-16 text-center">
          <p className="text-sm text-[#9CA3AF] mb-4">Trusted by thousands of Singaporeans</p>
          <div className="flex items-center justify-center gap-10 flex-wrap">
            <div className="text-center">
              <div className="text-2xl font-bold text-[#F96302] font-['Outfit']">50,000+</div>
              <div className="text-xs text-[#6B7280]">Policies Issued</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-[#F96302] font-['Outfit']">4.8/5</div>
              <div className="text-xs text-[#6B7280]">Customer Rating</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-[#F96302] font-['Outfit']">24/7</div>
              <div className="text-xs text-[#6B7280]">Support Available</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-6 text-center border-t border-gray-200 bg-white/50">
        <p className="text-xs text-[#9CA3AF]">
          © 2024 Income Insurance Limited. All rights reserved.
        </p>
        <p className="text-xs text-[#9CA3AF] mt-1">
          Regulated by the Monetary Authority of Singapore
        </p>
      </footer>

      {/* Made with Emergent badge */}
      <div className="emergent-badge">
        <div className="w-5 h-5 rounded-full bg-[#F96302] flex items-center justify-center">
          <span className="text-white text-xs font-bold">E</span>
        </div>
        Made with Emergent
      </div>
    </div>
  );
};

export default LandingPage;
