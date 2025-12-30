import { FileText, Download, Calendar, User, Car, Shield, Clock, AlertCircle } from "lucide-react";

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
        {/* Claim Dates Section */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
          <h4 className="text-sm font-semibold text-amber-800 mb-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Claim Information
          </h4>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-amber-700 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" />
                Claim Intimation Date
              </span>
              <span className="font-medium text-amber-900">{card.claim_intimation_date}</span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-amber-700 flex items-center gap-2">
                <AlertCircle className="w-3.5 h-3.5" />
                Incident Date & Time
              </span>
              <span className="font-medium text-amber-900">{card.incident_date_time}</span>
            </div>
          </div>
        </div>

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
