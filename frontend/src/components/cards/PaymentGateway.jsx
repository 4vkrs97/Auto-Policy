import { useState } from "react";
import { X, CreditCard, Smartphone, QrCode, Check, Loader2 } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Singapore payment method icons/logos
const PAYMENT_METHODS = [
  {
    id: "paynow",
    name: "PayNow",
    description: "Pay instantly with PayNow QR",
    icon: "🔵",
    color: "bg-purple-100 border-purple-300 hover:border-purple-500"
  },
  {
    id: "card",
    name: "Credit/Debit Card",
    description: "Visa, Mastercard, AMEX",
    icon: "💳",
    color: "bg-blue-100 border-blue-300 hover:border-blue-500"
  },
  {
    id: "grabpay",
    name: "GrabPay",
    description: "Pay with your GrabPay wallet",
    icon: "🟢",
    color: "bg-green-100 border-green-300 hover:border-green-500"
  },
  {
    id: "paylah",
    name: "DBS PayLah!",
    description: "Pay with DBS PayLah!",
    icon: "🔴",
    color: "bg-red-100 border-red-300 hover:border-red-500"
  },
  {
    id: "nets",
    name: "NETS",
    description: "Pay with NETS",
    icon: "🔷",
    color: "bg-cyan-100 border-cyan-300 hover:border-cyan-500"
  }
];

const PaymentGateway = ({ sessionId, amount, onClose, onPaymentComplete }) => {
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState("select"); // select, confirm, processing, success

  const handleMethodSelect = (methodId) => {
    setSelectedMethod(methodId);
  };

  const handleProceedToPayment = () => {
    if (selectedMethod) {
      setStep("confirm");
    }
  };

  const handleConfirmPayment = async () => {
    setStep("processing");
    setIsProcessing(true);

    try {
      // Call the payment API
      const response = await fetch(`${API}/payment/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          payment_method: selectedMethod,
          amount: amount
        })
      });

      if (!response.ok) {
        throw new Error("Payment failed");
      }

      const data = await response.json();

      // Simulate payment processing delay for demo
      await new Promise(resolve => setTimeout(resolve, 2000));

      setStep("success");

      // Wait a moment then call the completion handler
      setTimeout(() => {
        onPaymentComplete(selectedMethod, data.payment_reference, data.policy_number);
      }, 1500);

    } catch (error) {
      console.error("Payment error:", error);
      setStep("select");
      setIsProcessing(false);
    }
  };

  const selectedMethodData = PAYMENT_METHODS.find(m => m.id === selectedMethod);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-scale-in max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-white" />
            <h2 className="text-lg font-bold text-white font-['Outfit']">Payment Gateway</h2>
          </div>
          {step === "select" && (
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          {step === "select" && (
            <>
              {/* Amount */}
              <div className="text-center mb-4">
                <p className="text-gray-500 text-xs">Amount to Pay</p>
                <p className="text-2xl font-bold text-gray-900 font-['Outfit']">
                  S${amount.toFixed(2)}
                </p>
                <p className="text-gray-400 text-xs">Annual Premium (incl. GST)</p>
              </div>

              {/* Payment Methods */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-700 mb-2">Select Payment Method</p>
                {PAYMENT_METHODS.map((method) => (
                  <button
                    key={method.id}
                    onClick={() => handleMethodSelect(method.id)}
                    className={`w-full p-3 rounded-lg border-2 transition-all flex items-center gap-3 ${
                      selectedMethod === method.id
                        ? "border-orange-500 bg-orange-50 ring-1 ring-orange-200"
                        : method.color
                    }`}
                  >
                    <span className="text-xl">{method.icon}</span>
                    <div className="text-left flex-1">
                      <p className="font-semibold text-gray-900 text-sm">{method.name}</p>
                      <p className="text-xs text-gray-500">{method.description}</p>
                    </div>
                    {selectedMethod === method.id && (
                      <Check className="w-4 h-4 text-orange-500" />
                    )}
                  </button>
                ))}
              </div>

              {/* Proceed Button */}
              <button
                onClick={handleProceedToPayment}
                disabled={!selectedMethod}
                className={`w-full mt-4 py-3 rounded-lg font-semibold transition-all ${
                  selectedMethod
                    ? "bg-orange-500 text-white hover:bg-orange-600"
                    : "bg-gray-200 text-gray-400 cursor-not-allowed"
                }`}
              >
                Proceed to Pay
              </button>

              <p className="text-center text-xs text-gray-400 mt-3">
                🔒 Secure payment powered by Income Insurance
              </p>
            </>
          )}

          {step === "confirm" && (
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-3xl">{selectedMethodData?.icon}</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Confirm Payment</h3>
              <p className="text-gray-500 text-sm mb-4">
                You are about to pay <span className="font-bold text-gray-900">S${amount.toFixed(2)}</span> via{" "}
                <span className="font-bold text-gray-900">{selectedMethodData?.name}</span>
              </p>
              
              <div className="bg-gray-50 rounded-lg p-3 mb-4 text-left">
                <p className="text-xs text-gray-500 mb-1">DEMO MODE</p>
                <p className="text-xs text-gray-600">
                  This is a demo payment. No actual charges will be made. 
                  Click "Confirm Payment" to simulate a successful payment.
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setStep("select")}
                  className="flex-1 py-2.5 rounded-lg border-2 border-gray-200 text-gray-600 font-semibold text-sm hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleConfirmPayment}
                  className="flex-1 py-3 rounded-xl bg-orange-500 text-white font-semibold hover:bg-orange-600 transition-colors"
                >
                  Confirm Payment
                </button>
              </div>
            </div>
          )}

          {step === "processing" && (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Processing Payment</h3>
              <p className="text-gray-500">Please wait while we process your payment...</p>
              <div className="flex justify-center gap-1 mt-6">
                <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
              </div>
            </div>
          )}

          {step === "success" && (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 animate-bounce-once">
                <Check className="w-10 h-10 text-green-500" />
              </div>
              <h3 className="text-2xl font-bold text-green-600 mb-2">Payment Successful!</h3>
              <p className="text-gray-500">Your policy is being generated...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentGateway;
