import { Shield, Car } from "lucide-react";

export const QuoteCard = ({ card }) => {
  return (
    <div className="quote-card" data-testid="quote-card">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-lg font-['Outfit']">{card.plan_name}</h3>
          <p className="text-sm text-white/80">{card.coverage_type}</p>
        </div>
      </div>

      {card.vehicle && (
        <div className="flex items-center gap-2 mb-4 text-sm text-white/80">
          <Car className="w-4 h-4" />
          {card.vehicle}
        </div>
      )}

      <div className="bg-white/10 rounded-xl p-4 mb-4">
        {card.breakdown?.map((item, index) => (
          <div 
            key={index} 
            className={`breakdown-item ${index === card.breakdown.length - 1 ? 'pt-3 border-t border-white/20 mt-2' : ''}`}
          >
            <span className={index === card.breakdown.length - 1 ? 'text-lg' : 'text-sm text-white/80'}>
              {item.item}
            </span>
            <span className={index === card.breakdown.length - 1 ? 'text-lg font-bold' : 'text-sm'}>
              {item.amount}
            </span>
          </div>
        ))}
      </div>

      <div className="text-center">
        <div className="text-3xl font-bold font-['Outfit']">{card.premium}</div>
        <p className="text-sm text-white/60">Annual Premium</p>
      </div>
    </div>
  );
};

export default QuoteCard;
