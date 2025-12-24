import { FileText, Download, Calendar, User, Car, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

export const PolicyCard = ({ card, onDownload }) => {
  return (
    <div className="policy-card" data-testid="policy-card">
      <div className="policy-card-header">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold font-['Outfit']">Policy Summary</h3>
            <p className="text-sm text-white/80">{card.policy_number}</p>
          </div>
        </div>
      </div>

      <div className="policy-card-body space-y-4">
        {/* Dates */}
        <div className="flex items-center gap-3 text-sm">
          <Calendar className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-[#6B7280]">Coverage Period: </span>
            <span className="font-medium text-[#1F2937]">
              {card.start_date} - {card.end_date}
            </span>
          </div>
        </div>

        {/* Driver */}
        {card.driver_name && (
          <div className="flex items-center gap-3 text-sm">
            <User className="w-4 h-4 text-[#F96302]" />
            <div>
              <span className="text-[#6B7280]">Policyholder: </span>
              <span className="font-medium text-[#1F2937]">{card.driver_name}</span>
            </div>
          </div>
        )}

        {/* Vehicle */}
        <div className="flex items-center gap-3 text-sm">
          <Car className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-[#6B7280]">Vehicle: </span>
            <span className="font-medium text-[#1F2937]">{card.vehicle}</span>
          </div>
        </div>

        {/* Coverage */}
        <div className="flex items-center gap-3 text-sm">
          <Shield className="w-4 h-4 text-[#F96302]" />
          <div>
            <span className="text-[#6B7280]">Coverage: </span>
            <span className="font-medium text-[#1F2937]">
              {card.coverage} - {card.plan}
            </span>
          </div>
        </div>

        {/* Premium */}
        <div className="bg-[#FFF0E0] rounded-xl p-4 mt-4">
          <div className="flex items-center justify-between">
            <span className="text-[#6B7280]">Annual Premium</span>
            <span className="text-2xl font-bold text-[#F96302] font-['Outfit']">
              {card.premium}
            </span>
          </div>
          {card.ncd_percentage && card.ncd_percentage !== "0%" && (
            <p className="text-xs text-[#6B7280] mt-1">
              NCD Applied: {card.ncd_percentage}
            </p>
          )}
        </div>

        {/* Download Button */}
        <Button
          onClick={onDownload}
          className="w-full bg-[#F96302] hover:bg-[#D85502] text-white"
          data-testid="download-pdf-btn"
        >
          <Download className="w-4 h-4 mr-2" />
          Download PDF
        </Button>
      </div>
    </div>
  );
};

export default PolicyCard;
