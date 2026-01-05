import { Shield, Car, CheckCircle, User } from "lucide-react";

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

      {/* Policyholder Name */}
      {card.policyholder_name && (
        <div className="flex items-center gap-2 mb-3 text-sm text-white/90 bg-white/10 rounded-lg px-3 py-2">
          <User className="w-4 h-4" />
          <span className="text-white/70">Policyholder:</span>
          <span className="font-semibold">{card.policyholder_name}</span>
        </div>
      )}

      {card.vehicle && (
        <div className="flex items-center gap-2 mb-4 text-sm text-white/80">
          <Car className="w-4 h-4" />
          {card.vehicle}
        </div>
      )}

      <div className="quote-breakdown">
        {card.breakdown?.map((item, index) => {
          const isTotal = index === card.breakdown.length - 1;
          return (
            <div key={index} className={`quote-row ${isTotal ? 'font-bold' : ''}`}>
              <span>{item.item}</span>
              <span>{item.amount}</span>
            </div>
          );
        })}
      </div>

      <div className="text-center mt-4 pt-4 border-t border-white/20">
        <div className="text-3xl font-bold font-['Outfit']">{card.premium}</div>
        <p className="text-sm text-white/70 mt-1">Annual Premium</p>
      </div>
    </div>
  );
};

export default QuoteCard;
