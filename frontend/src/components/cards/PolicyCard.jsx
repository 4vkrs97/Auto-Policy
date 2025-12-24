import { FileText, Download, Calendar, User, Car, Shield } from "lucide-react";

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
        {/* Dates */}
        <div className="policy-detail-row">
          <Calendar className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-gray-500">Coverage: </span>
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
          </div>
          <span className="policy-premium-amount">
            {card.premium}
          </span>
        </div>

        {/* Download Button */}
        <button
          onClick={onDownload}
          className="primary-action-btn w-full justify-center mt-4"
          data-testid="download-pdf-btn"
        >
          <Download className="w-4 h-4" />
          Download Policy PDF
        </button>
      </div>
    </div>
  );
};

export default PolicyCard;
