import { useState, useEffect } from "react";
import { Shield, Wrench, FileText, Car, Check, Plus, X } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ADDON_ICONS = {
  engine_protection: Wrench,
  total_loss: FileText,
  roadside: Car
};

const AddonsCard = ({ card, sessionId, onAddonsUpdated }) => {
  const [selectedAddons, setSelectedAddons] = useState({});
  const [isUpdating, setIsUpdating] = useState(false);
  const [totalAddons, setTotalAddons] = useState(0);

  useEffect(() => {
    // Initialize selected state from card data
    const initial = {};
    card.addons?.forEach(addon => {
      initial[addon.id] = addon.selected || false;
    });
    setSelectedAddons(initial);
  }, [card.addons]);

  useEffect(() => {
    // Calculate total add-ons price
    let total = 0;
    card.addons?.forEach(addon => {
      if (selectedAddons[addon.id]) {
        total += addon.price;
      }
    });
    setTotalAddons(total);
  }, [selectedAddons, card.addons]);

  const toggleAddon = async (addonId) => {
    const newSelected = {
      ...selectedAddons,
      [addonId]: !selectedAddons[addonId]
    };
    setSelectedAddons(newSelected);

    // Update backend state
    setIsUpdating(true);
    try {
      const addonKey = `addon_${addonId === 'engine_protection' ? 'engine_protection' : addonId === 'total_loss' ? 'total_loss' : 'roadside'}`;
      
      await fetch(`${API}/sessions/${sessionId}/state`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          [addonKey]: newSelected[addonId]
        })
      });
      
      if (onAddonsUpdated) {
        onAddonsUpdated(newSelected);
      }
    } catch (error) {
      console.error('Failed to update addon:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const basePremium = card.current_premium || 0;
  const newPremium = basePremium + totalAddons;

  return (
    <div className="addons-card" data-testid="addons-card">
      <div className="addons-card-header">
        <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold font-['Outfit']">Coverage Add-ons</h3>
          <p className="text-sm text-white/80">Boost your protection</p>
        </div>
      </div>

      <div className="addons-card-body">
        {/* Add-on Options */}
        <div className="space-y-3">
          {card.addons?.map((addon) => {
            const Icon = ADDON_ICONS[addon.id] || Shield;
            const isSelected = selectedAddons[addon.id];
            
            return (
              <div
                key={addon.id}
                onClick={() => toggleAddon(addon.id)}
                className={`addon-item ${isSelected ? 'selected' : ''}`}
              >
                <div className="addon-checkbox">
                  {isSelected ? (
                    <Check className="w-4 h-4 text-white" />
                  ) : (
                    <Plus className="w-4 h-4 text-gray-400" />
                  )}
                </div>
                
                <div className="addon-content">
                  <div className="addon-icon">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="addon-details">
                    <h4 className="addon-title">{addon.title}</h4>
                    <p className="addon-description">{addon.description}</p>
                  </div>
                </div>
                
                <div className="addon-price">
                  <span className="text-sm text-gray-500">+</span>
                  <span className="text-lg font-bold text-orange-500">${addon.price}</span>
                  <span className="text-xs text-gray-400">/yr</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Premium Summary */}
        <div className="addons-summary">
          <div className="summary-row">
            <span className="text-gray-600">Base Premium</span>
            <span className="font-medium">${basePremium.toFixed(2)}</span>
          </div>
          {totalAddons > 0 && (
            <div className="summary-row text-orange-500">
              <span>Add-ons Total</span>
              <span className="font-medium">+${totalAddons.toFixed(2)}</span>
            </div>
          )}
          <div className="summary-divider"></div>
          <div className="summary-row total">
            <span className="text-gray-900 font-semibold">New Premium</span>
            <span className="text-xl font-bold text-orange-500">${newPremium.toFixed(2)}/yr</span>
          </div>
        </div>

        {/* Info Note */}
        <div className="addons-note">
          <p className="text-xs text-gray-500">
            💡 Click on any add-on to select/deselect. Prices are annual and will be added to your premium.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AddonsCard;
