import { FileText, Download, Calendar, User, Car, Shield, AlertTriangle, Leaf } from "lucide-react";

// Standard motor insurance exclusions for Singapore
const POLICY_EXCLUSIONS = [
  "Driving under the influence of alcohol or drugs",
  "Driving without a valid license",
  "Use of vehicle for illegal purposes",
  "Mechanical or electrical breakdown, wear and tear",
  "Damage caused by war, terrorism, or nuclear risks",
  "Consequential or indirect losses",
  "Personal belongings left in the vehicle",
  "Racing, speed testing, or rallies",
  "Using vehicle for hire/reward (unless declared)",
  "Damage while vehicle is used outside Singapore/West Malaysia"
];

export const PolicyCard = ({ card, onDownload }) => {
  return (
    <div className="policy-card" data-testid="policy-card">
      <div className="policy-card-header">
        <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
          <FileText className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold font-['Outfit']">Policy Summary</h3>
          <p className="text-sm text-white/80">{card.policy_number}</p>
        </div>
      </div>

      <div className="policy-card-body">
        {/* Policy Period */}
        <div className="policy-detail-row">
          <Calendar className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-gray-500">Coverage Period: </span>
            <span className="font-medium text-gray-900">
              {card.start_date} - {card.end_date}
            </span>
          </div>
        </div>

        {/* Driver */}
        {card.driver_name && (
          <div className="policy-detail-row">
            <User className="w-4 h-4 text-[#F96302]" />
            <div>
              <span className="text-gray-500">Policyholder: </span>
              <span className="font-medium text-gray-900">{card.driver_name}</span>
            </div>
          </div>
        )}

        {/* Vehicle */}
        <div className="policy-detail-row">
          <Car className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-gray-500">Vehicle: </span>
            <span className="font-medium text-gray-900">{card.vehicle}</span>
          </div>
        </div>

        {/* Coverage */}
        <div className="policy-detail-row">
          <Shield className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-gray-500">Coverage: </span>
            <span className="font-medium text-gray-900">
              {card.coverage} - {card.plan}
            </span>
          </div>
        </div>

        {/* Premium */}
        <div className="policy-premium-box">
          <div>
            <span className="text-gray-500 text-sm">Annual Premium</span>
            {card.ncd_percentage && card.ncd_percentage !== "0%" && (
              <p className="text-xs text-gray-400 mt-1">
                NCD Applied: {card.ncd_percentage}
              </p>
            )}
            {card.green_vehicle_discount > 0 && (
              <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                <Leaf className="w-3 h-3" />
                Green Vehicle Discount: 5% (-${card.green_vehicle_discount})
              </p>
            )}
          </div>
          <span className="policy-premium-amount">
            {card.premium}
          </span>
        </div>

        {/* Exclusions Section */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <h4 className="font-semibold text-gray-900 text-sm font-['Outfit']">Policy Exclusions</h4>
          </div>
          <div className="bg-amber-50 rounded-lg p-3 border border-amber-200">
            <p className="text-xs text-amber-800 mb-2 font-medium">This policy does not cover:</p>
            <ul className="space-y-1">
              {POLICY_EXCLUSIONS.map((exclusion, index) => (
                <li key={index} className="text-xs text-amber-700 flex items-start gap-2">
                  <span className="text-amber-400 mt-0.5">•</span>
                  <span>{exclusion}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Download Button */}
        <button
          onClick={onDownload}
          className="primary-action-btn w-full justify-center mt-4"
          data-testid="download-pdf-btn"
        >
          <Download className="w-4 h-4" />
          Download Policy Summary PDF
        </button>
      </div>
    </div>
  );
};

export default PolicyCard;
