import { Check, Star } from "lucide-react";
import { cn } from "@/lib/utils";

export const CoverageCard = ({ card, onSelect }) => {
  const plans = card.plans || [];

  return (
    <div className="space-y-3" data-testid="coverage-card">
      {plans.map((plan, index) => (
        <div
          key={index}
          className={cn(
            "coverage-card cursor-pointer",
            plan.recommended && "recommended"
          )}
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
            <div>
              <h3 className="font-semibold text-[#1F2937] font-['Outfit']">
                {plan.name}
              </h3>
              <p className="text-[#F96302] font-semibold">{plan.price}</p>
            </div>
          </div>
          
          <ul className="space-y-2">
            {plan.features.map((feature, fIndex) => (
              <li key={fIndex} className="flex items-start gap-2 text-sm text-[#6B7280]">
                <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                {feature}
              </li>
            ))}
          </ul>
          
          <div className="mt-4 pt-3 border-t border-[#E5E5EA]">
            <span className="text-sm text-[#F96302] font-medium">
              Select this plan →
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CoverageCard;
