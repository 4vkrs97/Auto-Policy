import { Car, CheckCircle, Briefcase, Calendar, MapPin, Clock, Route } from "lucide-react";

export const VehicleSummaryCard = ({ data }) => {
  const items = [
    { label: "Vehicle Type", value: data?.type || "—" },
    { label: "Make", value: data?.make || "—" },
    { label: "Model", value: data?.model || "—" },
    { label: "Engine Capacity", value: data?.engine || "—" },
  ];

  // Add usage details for cars
  const usageItems = [];
  if (data?.type?.toLowerCase() === "car" && data?.usage) {
    usageItems.push(
      { label: "Primary Purpose", value: data.usage.purpose || "—", icon: Briefcase },
      { label: "Usage Frequency", value: data.usage.frequency || "—", icon: Calendar },
      { label: "Monthly Distance", value: data.usage.distance || "—", icon: Route },
      { label: "Usual Driving Time", value: data.usage.driving_time || "—", icon: Clock },
      { label: "Driving Environment", value: data.usage.environment || "—", icon: MapPin }
    );
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
        
        {/* Usage Details Section for Cars */}
        {usageItems.length > 0 && (
          <>
            <div className="border-t border-gray-200 my-3"></div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Usage Profile</p>
            {usageItems.map((item) => {
              const Icon = item.icon;
              return (
                <div 
                  key={item.label}
                  className="fetch-row complete"
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-3 h-3 text-gray-400" />
                    <span className="text-gray-600">{item.label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{item.value}</span>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                </div>
              );
            })}
          </>
        )}
        
        <div className="fetch-success-msg mt-3">
          <CheckCircle className="w-4 h-4" />
          <span>Vehicle information collected</span>
        </div>
      </div>
    </div>
  );
};

export default VehicleSummaryCard;
