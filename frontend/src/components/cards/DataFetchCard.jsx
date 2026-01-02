import { useState, useEffect, useRef } from "react";
import { Car, User, Shield, CheckCircle, Loader2, Hash } from "lucide-react";

const FETCH_ITEMS = {
  vehicle: {
    icon: Car,
    title: "Fetching Vehicle Details from LTA",
    items: [
      { label: "Registration Number", key: "registration" },
      { label: "Make", key: "make" },
      { label: "Model", key: "model" },
      { label: "Engine Capacity", key: "engine_cc" },
      { label: "Year of Registration", key: "year" },
      { label: "Road Tax Status", key: "road_tax" },
    ]
  },
  vin: {
    icon: Hash,
    title: "Fetching Vehicle Details from VIN",
    items: [
      { label: "VIN Number", key: "vin" },
      { label: "Make", key: "make" },
      { label: "Model", key: "model" },
      { label: "Year", key: "year" },
      { label: "Engine Capacity", key: "engine" },
      { label: "Fuel Type", key: "fuel_type" },
      { label: "Body Class", key: "body_class" },
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

export const DataFetchCard = ({ type, data }) => {
  const [completedItems, setCompletedItems] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const indexRef = useRef(0);
  
  const config = FETCH_ITEMS[type];
  
  useEffect(() => {
    if (!config) return;
    
    setCompletedItems([]);
    setIsComplete(false);
    indexRef.current = 0;
    
    const interval = setInterval(() => {
      if (indexRef.current < config.items.length) {
        const currentKey = config.items[indexRef.current].key;
        setCompletedItems(prev => [...prev, currentKey]);
        indexRef.current += 1;
      } else {
        clearInterval(interval);
        setIsComplete(true);
      }
    }, 300);

    return () => clearInterval(interval);
  }, [type]);

  if (!config) return null;
  
  const Icon = config.icon;

  return (
    <div className="fetch-card" data-testid={`fetch-card-${type}`}>
      <div className="fetch-card-header">
        <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
          <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-sm font-['Outfit']">{config.title}</h3>
          <p className="text-xs text-white/70">
            {isComplete ? "Complete" : "Connecting to secure API..."}
          </p>
        </div>
      </div>
      
      <div className="fetch-card-body">
        {config.items.map((item) => {
          const isLoaded = completedItems.includes(item.key);
          const value = data?.[item.key] || "—";
          
          return (
            <div 
              key={item.key}
              className={`fetch-row ${isLoaded ? 'complete' : 'loading'}`}
            >
              <span className="text-gray-600">{item.label}</span>
              <div className="flex items-center gap-2">
                {isLoaded ? (
                  <>
                    <span className="font-medium text-gray-900">{value}</span>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </>
                ) : (
                  <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
                )}
              </div>
            </div>
          );
        })}
        
        {isComplete && (
          <div className="fetch-success-msg">
            <CheckCircle className="w-4 h-4" />
            <span>All data retrieved successfully</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataFetchCard;
