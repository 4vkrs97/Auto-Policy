import { useState, useEffect } from "react";
import { Car, User, Shield, CheckCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const FETCH_ITEMS = {
  vehicle: {
    icon: Car,
    title: "Fetching Vehicle Details",
    items: [
      { label: "Registration Number", key: "registration" },
      { label: "Make", key: "make" },
      { label: "Model", key: "model" },
      { label: "Engine Capacity", key: "engine_cc" },
      { label: "Year of Registration", key: "year" },
      { label: "Road Tax Status", key: "road_tax" },
    ]
  },
  singpass: {
    icon: User,
    title: "Retrieving from Singpass",
    items: [
      { label: "Full Name", key: "name" },
      { label: "NRIC", key: "nric" },
      { label: "Date of Birth", key: "dob" },
      { label: "Address", key: "address" },
      { label: "License Class", key: "license" },
      { label: "Driving Experience", key: "experience" },
    ]
  },
  risk: {
    icon: Shield,
    title: "Assessing Risk Profile",
    items: [
      { label: "Claims History", key: "claims" },
      { label: "Driver Risk Score", key: "driver_risk" },
      { label: "Vehicle Risk Score", key: "vehicle_risk" },
      { label: "NCD Eligibility", key: "ncd" },
      { label: "Overall Risk Rating", key: "rating" },
    ]
  }
};

export const DataFetchCard = ({ type, data, onComplete }) => {
  const [completedItems, setCompletedItems] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const config = FETCH_ITEMS[type];
  const Icon = config?.icon || Car;

  useEffect(() => {
    if (!config) return;
    
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < config.items.length) {
        setCompletedItems(prev => [...prev, config.items[currentIndex].key]);
        currentIndex++;
      } else {
        clearInterval(interval);
        setIsComplete(true);
        if (onComplete) {
          setTimeout(onComplete, 500);
        }
      }
    }, 400);

    return () => clearInterval(interval);
  }, [config, onComplete]);

  if (!config) return null;

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden max-w-md" data-testid={`fetch-card-${type}`}>
      <div className="bg-gradient-to-r from-[#F96302] to-[#FF8534] px-4 py-3 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-white font-['Outfit']">{config.title}</h3>
          <p className="text-xs text-white/80">
            {isComplete ? "Complete" : "Connecting to secure API..."}
          </p>
        </div>
      </div>
      
      <div className="p-4 space-y-2">
        {config.items.map((item, index) => {
          const isLoaded = completedItems.includes(item.key);
          const value = data?.[item.key] || "—";
          
          return (
            <div 
              key={item.key}
              className={cn(
                "flex items-center justify-between py-2 px-3 rounded-lg transition-all duration-300",
                isLoaded ? "bg-green-50" : "bg-gray-50"
              )}
            >
              <span className="text-sm text-gray-600">{item.label}</span>
              <div className="flex items-center gap-2">
                {isLoaded ? (
                  <>
                    <span className="text-sm font-medium text-gray-900">{value}</span>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </>
                ) : (
                  <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
                )}
              </div>
            </div>
          );
        })}
      </div>
      
      {isComplete && (
        <div className="px-4 pb-4">
          <div className="bg-green-100 text-green-700 text-sm py-2 px-3 rounded-lg flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>All data retrieved successfully</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataFetchCard;
