import { Car, CheckCircle } from "lucide-react";

export const VehicleSummaryCard = ({ data }) => {
  const items = [
    { label: "Vehicle Type", value: data?.type || "—" },
    { label: "Make", value: data?.make || "—" },
    { label: "Model", value: data?.model || "—" },
    { label: "Engine Capacity", value: data?.engine || "—" },
  ];

  // Add off-peak only for cars
  if (data?.type?.toLowerCase() === "car") {
    items.push({ label: "Off-Peak Vehicle", value: data?.off_peak || "No" });
  }

  return (
    <div className="fetch-card" data-testid="vehicle-summary-card">
      <div className="fetch-card-header">
        <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
          <Car className="w-4 h-4 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-sm font-['Outfit']">Vehicle Details Summary</h3>
          <p className="text-xs text-white/70">Please confirm your vehicle information</p>
        </div>
      </div>
      
      <div className="fetch-card-body">
        {items.map((item) => (
          <div 
            key={item.label}
            className="fetch-row complete"
          >
            <span className="text-gray-600">{item.label}</span>
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">{item.value}</span>
              <CheckCircle className="w-4 h-4 text-green-500" />
            </div>
          </div>
        ))}
        
        <div className="fetch-success-msg mt-3">
          <CheckCircle className="w-4 h-4" />
          <span>Vehicle information collected</span>
        </div>
      </div>
    </div>
  );
};

export default VehicleSummaryCard;
