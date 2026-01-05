import { Check, Star, Shield, Award } from "lucide-react";

export const CoverageCard = ({ card, onSelect }) => {
  const plans = card.plans || [];

  return (
    <div className="coverage-cards-grid" data-testid="coverage-card">
      {plans.map((plan, index) => (
        <div
          key={index}
          className={`coverage-card ${plan.recommended ? 'recommended' : ''}`}
          onClick={() => onSelect(plan.name, plan.name)}
          data-testid={`coverage-plan-${index}`}
        >
          {plan.recommended && (
            <div className="flex items-center gap-1 text-[#F96302] text-xs font-semibold mb-2">
              <Star className="w-3 h-3 fill-current" />
              RECOMMENDED
            </div>
          )}
          
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${plan.recommended ? 'bg-orange-100' : 'bg-gray-100'}`}>
                {plan.recommended ? (
                  <Award className="w-5 h-5 text-[#F96302]" />
                ) : (
                  <Shield className="w-5 h-5 text-gray-500" />
                )}
              </div>
              <div>
                <h3 className="font-semibold text-[#1F2937] font-['Outfit']">
                  {plan.name}
                </h3>
                <p className="text-[#F96302] font-semibold text-sm">{plan.price}</p>
              </div>
            </div>
          </div>
          
          <ul className="space-y-2 flex-1">
            {plan.features.map((feature, fIndex) => (
              <li key={fIndex} className="flex items-start gap-2 text-sm text-[#6B7280]">
                <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                {feature}
              </li>
            ))}
          </ul>
          
          <div className="mt-4 pt-3 border-t border-gray-100">
            <button className="coverage-select-btn">
              Select this plan →
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CoverageCard;
