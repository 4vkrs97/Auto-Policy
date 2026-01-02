from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import asyncio
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'motor_insurance')]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ MODELS ============

class SessionCreate(BaseModel):
    user_agent: Optional[str] = None

class Session(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_agent: str = "orchestrator"
    state: Dict[str, Any] = Field(default_factory=dict)

class MessageCreate(BaseModel):
    session_id: str
    content: str
    quick_reply_value: Optional[str] = None

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # user, assistant, system
    content: str
    agent: Optional[str] = None
    quick_replies: Optional[List[Dict[str, str]]] = None
    cards: Optional[List[Dict[str, Any]]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuoteRequest(BaseModel):
    session_id: str

class Quote(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    vehicle_type: str
    vehicle_make: str
    vehicle_model: str
    engine_capacity: str
    coverage_type: str
    plan_name: str
    base_premium: float
    risk_loading: float
    ncd_discount: float
    telematics_discount: float
    final_premium: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ MOCK DATA ============

VEHICLE_MAKES = {
    "car": ["Toyota", "Honda", "BMW", "Mercedes-Benz", "Audi", "Mazda", "Hyundai", "Kia", "Nissan", "Volkswagen"],
    "motorcycle": ["Honda", "Yamaha", "Kawasaki", "Suzuki", "Ducati", "Harley-Davidson", "BMW", "KTM"]
}

VEHICLE_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Prius", "Altis"],
    "Honda": ["Civic", "Accord", "CR-V", "Jazz", "City", "CBR500R", "CB650R", "PCX"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "G 310 R", "R 1250 GS"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "A-Class"],
    "Audi": ["A4", "A6", "Q5", "Q7"],
    "Mazda": ["3", "6", "CX-5", "CX-30"],
    "Hyundai": ["Elantra", "Tucson", "Santa Fe", "Ioniq"],
    "Kia": ["Cerato", "Sportage", "Sorento", "Stinger"],
    "Nissan": ["Sylphy", "X-Trail", "Kicks", "Serena"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "Touareg"],
    "Yamaha": ["YZF-R3", "MT-07", "XMAX", "NMAX"],
    "Kawasaki": ["Ninja 400", "Z650", "Versys 650"],
    "Suzuki": ["GSX-R600", "SV650", "V-Strom 650"],
    "Ducati": ["Panigale V2", "Monster", "Multistrada"],
    "Harley-Davidson": ["Iron 883", "Street Glide", "Fat Boy"],
    "KTM": ["Duke 390", "RC 390", "Adventure 390"]
}

ENGINE_CAPACITIES = {
    "car": ["1000cc - 1600cc", "1601cc - 2000cc", "2001cc - 3000cc", "Above 3000cc"],
    "motorcycle": ["Below 200cc", "200cc - 400cc", "401cc - 650cc", "Above 650cc"]
}

# Mock LTA vehicle data
MOCK_LTA_DATA = {
    "SGX1234A": {
        "make": "Toyota",
        "model": "Camry",
        "engine_cc": "2000cc",
        "year": 2022,
        "road_tax_valid": True,
        "accident_history": []
    },
    "SBA5678B": {
        "make": "Honda",
        "model": "Civic",
        "engine_cc": "1500cc",
        "year": 2021,
        "road_tax_valid": True,
        "accident_history": [{"date": "2023-05-15", "severity": "minor"}]
    }
}

# Mock Singpass data
MOCK_SINGPASS_DATA = {
    "S1234567A": {
        "full_name": "Tan Ah Kow",
        "nric": "S1234567A",
        "dob": "1985-06-15",
        "gender": "Male",
        "marital_status": "Married",
        "phone": "+6591234567",
        "email": "tan.ahkow@email.com",
        "address": "123 Orchard Road, #08-01, Singapore 238857",
        "driving_license": {
            "class": "3",
            "issue_date": "2005-03-20",
            "expiry_date": "2030-03-19"
        }
    }
}

# ============ AGENT SYSTEM PROMPTS ============

ORCHESTRATOR_PROMPT = """You are Jiffy Jane, a friendly and efficient motor insurance assistant for Income Insurance Singapore. 
Your role is to guide users through the motor insurance quote and purchase process.

PERSONALITY:
- Warm, helpful, and professional
- Use simple, clear language
- Add occasional Singapore flavor (lah, can, shiok) sparingly
- Always be encouraging and supportive

FLOW OVERVIEW:
1. Welcome and ask about vehicle type (Car or Two-Wheeler)
2. Collect vehicle information (make, model, engine capacity, off-peak status)
3. Present coverage options (Third Party or Comprehensive)
4. Show plan comparison (Drive Premium vs Drive Classic)
5. Collect driver identity (offer Singpass option)
6. Check driver eligibility and claims history
7. Ask about additional drivers
8. Offer telematics opt-in
9. Calculate and present premium quote
10. Generate policy documents

RESPONSE FORMAT:
Always respond in JSON format with:
{{
    "message": "Your conversational message here",
    "quick_replies": [{{"label": "Button Label", "value": "button_value"}}],
    "next_agent": "agent_name",
    "data_collected": {{"key": "value"}},
    "show_cards": false
}}

Current session state: {state}
User message: {user_message}

Based on the current state and user message, provide an appropriate response. Guide the user through the process step by step.
"""

INTAKE_AGENT_PROMPT = """You are the Vehicle Intake Agent for Income Insurance. Collect vehicle primary information.

Your task:
1. Confirm or ask for vehicle type (car/motorcycle)
2. Ask for vehicle make
3. Ask for vehicle model
4. Ask for engine capacity
5. Ask about off-peak status (for cars only)

Available makes for cars: {car_makes}
Available makes for motorcycles: {motorcycle_makes}

Current session state: {state}
User message: {user_message}

Respond in JSON format:
{{
    "message": "Your message",
    "quick_replies": [{{"label": "Option", "value": "value"}}],
    "next_agent": "coverage" or "intake" (if more info needed),
    "data_collected": {{"field": "value"}}
}}
"""

COVERAGE_AGENT_PROMPT = """You are the Coverage Agent for Income Insurance. Present coverage options to the user.

Coverage Types:
1. Third Party Only - Basic coverage for third party liability
2. Comprehensive - Full coverage including own damage, theft, and third party

Plans:
1. Drive Premium Plan - Higher coverage limits, 24/7 roadside assistance, windscreen coverage
2. Drive Classic Plan - Standard coverage, essential protection

Current vehicle: {vehicle_type} - {vehicle_make} {vehicle_model}
Current session state: {state}
User message: {user_message}

Respond in JSON format with coverage comparison cards when appropriate:
{{
    "message": "Your message",
    "quick_replies": [{{"label": "Plan Option", "value": "value"}}],
    "next_agent": "driver_identity" or "coverage",
    "data_collected": {{"coverage_type": "value", "plan_name": "value"}},
    "show_cards": true,
    "cards": [
        {{
            "type": "coverage_comparison",
            "plans": [
                {{"name": "Drive Premium", "price": "$XXX/year", "features": ["Feature 1", "Feature 2"]}},
                {{"name": "Drive Classic", "price": "$XXX/year", "features": ["Feature 1", "Feature 2"]}}
            ]
        }}
    ]
}}
"""

DRIVER_IDENTITY_AGENT_PROMPT = """You are the Driver Identity Agent for Income Insurance. Collect driver information.

Options:
1. Retrieve via Singpass (quick and convenient)
2. Manual entry

If manual entry, collect:
- Full Name
- NRIC / Passport
- Date of Birth
- Gender
- Marital Status
- Phone
- Email
- Address

Current session state: {state}
User message: {user_message}

Respond in JSON format:
{{
    "message": "Your message",
    "quick_replies": [{{"label": "Option", "value": "value"}}],
    "next_agent": "driver_eligibility" or "driver_identity",
    "data_collected": {{"driver_field": "value"}},
    "singpass_retrieved": true/false
}}
"""

RISK_ASSESSMENT_PROMPT = """You are the Risk Assessment Agent for Income Insurance. Assess driver and vehicle risk.

Consider:
- Driver age and experience
- Claims history
- Vehicle type and value
- Additional drivers

Risk factors:
- No claims in 3 years: Low risk, eligible for NCD
- 1 minor claim: Medium risk
- Multiple claims or major claim: High risk, may need loading

Current session state: {state}
User message: {user_message}

Respond in JSON format:
{{
    "message": "Your message explaining risk assessment",
    "quick_replies": [{{"label": "Continue", "value": "continue"}}],
    "next_agent": "pricing",
    "data_collected": {{"risk_score": "low/medium/high", "ncd_eligible": true/false}}
}}
"""

PRICING_AGENT_PROMPT = """You are the Pricing Agent for Income Insurance. Calculate and present premium.

Base Premium Calculation:
- Car 1000-1600cc: $800-1200/year
- Car 1601-2000cc: $1000-1500/year
- Car 2001-3000cc: $1200-1800/year
- Car >3000cc: $1500-2500/year
- Motorcycle <400cc: $300-500/year
- Motorcycle 400-650cc: $500-800/year
- Motorcycle >650cc: $800-1200/year

Adjustments:
- Comprehensive vs Third Party: +40% for Comprehensive
- Premium Plan vs Classic: +20% for Premium
- NCD (No Claims Discount): -10% to -50%
- Telematics opt-in: -5%
- Risk loading: +10% to +30% for high risk

Current session state: {state}
User message: {user_message}

Calculate and respond in JSON format with quote details:
{{
    "message": "Here's your personalized quote!",
    "quick_replies": [{{"label": "Proceed to Documents", "value": "proceed"}}],
    "next_agent": "document",
    "data_collected": {{
        "base_premium": 1200,
        "coverage_loading": 480,
        "plan_loading": 240,
        "ncd_discount": -336,
        "telematics_discount": 0,
        "risk_loading": 0,
        "final_premium": 1584
    }},
    "show_cards": true,
    "cards": [
        {{
            "type": "quote_summary",
            "plan_name": "Drive Premium",
            "coverage_type": "Comprehensive",
            "premium": "$1,584/year",
            "breakdown": [
                {{"item": "Base Premium", "amount": "$1,200"}},
                {{"item": "Coverage (Comprehensive)", "amount": "+$480"}},
                {{"item": "Plan (Premium)", "amount": "+$240"}},
                {{"item": "NCD Discount (20%)", "amount": "-$336"}}
            ]
        }}
    ]
}}
"""

DOCUMENT_AGENT_PROMPT = """You are the Document Agent for Income Insurance. Generate policy documents.

Documents to generate:
1. Policy Summary
2. Coverage Details
3. Terms and Conditions
4. Premium Breakdown

Current session state: {state}
User message: {user_message}

Respond in JSON format:
{{
    "message": "Great news! Your policy documents are ready for review.",
    "quick_replies": [
        {{"label": "View Policy Summary", "value": "view_summary"}},
        {{"label": "Download PDF", "value": "download_pdf"}}
    ],
    "next_agent": "complete",
    "data_collected": {{"documents_ready": true}},
    "show_cards": true,
    "cards": [
        {{
            "type": "policy_document",
            "policy_number": "INC-2024-XXXXX",
            "vehicle": "Toyota Camry",
            "coverage": "Comprehensive",
            "plan": "Drive Premium",
            "premium": "$1,584/year",
            "start_date": "01 Jan 2025",
            "end_date": "31 Dec 2025"
        }}
    ]
}}
"""

# ============ LLM CHAT HANDLER ============

async def get_agent_response(session_id: str, user_message: str, state: dict, agent: str) -> dict:
    """Get response from the appropriate agent - using fallback for speed"""
    # Use fallback responses directly for faster and more predictable flow
    return get_fallback_response(state, agent, user_message)

def get_fallback_response(state: dict, agent: str, user_message: str) -> dict:
    """Provide fallback responses when LLM fails"""
    user_lower = user_message.lower()
    
    # Step 1: Welcome - Ask for vehicle type
    if not state.get("vehicle_type"):
        return {
            "message": "Hi there! I'm Jiffy Jane, your friendly motor insurance assistant from Income Insurance! Let me help you get a quick quote. What type of vehicle would you like to insure?",
            "quick_replies": [
                {"label": "🚗 Car", "value": "car"},
                {"label": "🏍️ Motorcycle", "value": "motorcycle"}
            ],
            "next_agent": "orchestrator",
            "data_collected": {}
        }
    
    # Step 2: Ask for vehicle make
    if state.get("vehicle_type") and not state.get("vehicle_make"):
        vtype = state.get("vehicle_type")
        makes = VEHICLE_MAKES.get(vtype, VEHICLE_MAKES["car"])
        return {
            "message": f"Great choice! Which brand is your {vtype}?",
            "quick_replies": [{"label": make, "value": make} for make in makes[:8]],
            "next_agent": "intake",
            "data_collected": {}
        }
    
    # Step 3: Ask for vehicle model
    if state.get("vehicle_make") and not state.get("vehicle_model"):
        make = state.get("vehicle_make")
        models = VEHICLE_MODELS.get(make, ["Sedan", "SUV", "Hatchback", "Other"])
        return {
            "message": f"Nice! What model is your {make}?",
            "quick_replies": [{"label": model, "value": model} for model in models[:6]],
            "next_agent": "intake",
            "data_collected": {}
        }
    
    # Step 4: Ask for engine capacity
    if state.get("vehicle_model") and not state.get("engine_capacity"):
        vtype = state.get("vehicle_type", "car")
        capacities = ENGINE_CAPACITIES.get(vtype, ENGINE_CAPACITIES["car"])
        return {
            "message": "What's the engine capacity of your vehicle?",
            "quick_replies": [{"label": cap, "value": cap} for cap in capacities],
            "next_agent": "intake",
            "data_collected": {}
        }
    
    # Step 5: Ask about off-peak (for cars only)
    if state.get("engine_capacity") and state.get("vehicle_type") == "car" and state.get("off_peak") is None:
        return {
            "message": "Is your car registered as an off-peak vehicle? (Weekend/Red plate car)",
            "quick_replies": [
                {"label": "Yes, Off-Peak", "value": "yes_offpeak"},
                {"label": "No, Regular Car", "value": "no_offpeak"}
            ],
            "next_agent": "intake",
            "data_collected": {}
        }
    
    # Step 6: Show vehicle summary and move to coverage
    if state.get("engine_capacity") and not state.get("vehicle_confirmed"):
        vtype = state.get("vehicle_type", "car")
        # Skip off-peak for motorcycles
        if vtype == "motorcycle" or state.get("off_peak") is not None:
            make = state.get("vehicle_make", "")
            model = state.get("vehicle_model", "")
            engine = state.get("engine_capacity", "")
            off_peak = "Yes" if state.get("off_peak") == "yes_offpeak" else "No"
            
            return {
                "message": f"Perfect! Here's a summary of your vehicle details:",
                "quick_replies": [
                    {"label": "✓ Confirm & Continue", "value": "confirm_vehicle"},
                    {"label": "Edit Details", "value": "edit_vehicle"}
                ],
                "next_agent": "intake",
                "data_collected": {},
                "show_cards": True,
                "cards": [{
                    "type": "vehicle_summary",
                    "data": {
                        "type": vtype.title(),
                        "make": make,
                        "model": model,
                        "engine": engine,
                        "off_peak": off_peak if vtype == "car" else "N/A"
                    }
                }]
            }
    
    # Vehicle confirmed, show coverage options
    if state.get("vehicle_confirmed") and not state.get("coverage_type"):
        return {
            "message": "Perfect! Now let's choose the right coverage for you. I recommend Comprehensive coverage for maximum protection.",
            "quick_replies": [
                {"label": "Comprehensive", "value": "comprehensive"},
                {"label": "Third Party Only", "value": "third_party"}
            ],
            "next_agent": "coverage",
            "data_collected": {},
            "show_cards": True,
            "cards": [{
                "type": "coverage_comparison",
                "plans": [
                    {"name": "Comprehensive", "price": "From $1,200/year", "features": ["Own damage coverage", "Theft protection", "Third party liability", "Personal accident cover", "Natural disaster coverage"], "recommended": True},
                    {"name": "Third Party", "price": "From $800/year", "features": ["Third party liability", "Personal accident cover", "Legal costs coverage"]}
                ]
            }]
        }
    
    # Coverage selected, show plan options
    if state.get("coverage_type") and not state.get("plan_name"):
        coverage = state.get("coverage_type", "comprehensive").replace("_", " ").title()
        return {
            "message": f"Excellent choice! For {coverage} coverage, we have two plans. Drive Premium includes extra benefits like windscreen coverage and 24/7 roadside assistance.",
            "quick_replies": [
                {"label": "Drive Premium", "value": "Drive Premium"},
                {"label": "Drive Classic", "value": "Drive Classic"}
            ],
            "next_agent": "coverage",
            "data_collected": {},
            "show_cards": True,
            "cards": [{
                "type": "plan_comparison",
                "plans": [
                    {"name": "Drive Premium", "price": "+20%", "features": ["Coverage limit: $100,000", "24/7 Roadside assistance", "Windscreen coverage: $1,000", "Personal belongings: $2,000", "NCD Protector included"], "recommended": True},
                    {"name": "Drive Classic", "price": "Base", "features": ["Coverage limit: $50,000", "Business hours support", "Windscreen coverage: $300", "Personal belongings: $500"]}
                ]
            }]
        }
    
    # Plan selected, ask about Singpass
    if state.get("plan_name") and not state.get("driver_info_method"):
        return {
            "message": "Great choice! Now I need to verify your identity and driving credentials. Would you like to retrieve your details via Singpass? It's faster and more secure!",
            "quick_replies": [
                {"label": "🔐 Use Singpass", "value": "singpass"},
                {"label": "Enter Manually", "value": "manual"}
            ],
            "next_agent": "driver_identity",
            "data_collected": {}
        }
    
    # Singpass selected, ask for consent
    if state.get("driver_info_method") == "singpass" and not state.get("singpass_consent"):
        return {
            "message": "To retrieve your details from Singpass, I need your consent. By proceeding, you agree to allow Income Insurance to access your personal data from Singpass for insurance purposes, in compliance with PDPA guidelines.",
            "quick_replies": [
                {"label": "✓ I Consent", "value": "consent_yes"},
                {"label": "No, Enter Manually", "value": "consent_no"}
            ],
            "next_agent": "driver_identity",
            "data_collected": {}
        }
    
    # Singpass consent given, retrieve and show data
    if state.get("singpass_consent") == "consent_yes" and not state.get("driver_confirmed"):
        mock_data = list(MOCK_SINGPASS_DATA.values())[0]
        return {
            "message": f"🔐 Successfully retrieved your details from Singpass!",
            "quick_replies": [
                {"label": "✓ Confirm Details", "value": "confirm_driver"},
                {"label": "Edit Details", "value": "edit_driver"}
            ],
            "next_agent": "driver_identity",
            "data_collected": {
                "driver_name": mock_data["full_name"],
                "driver_nric": mock_data["nric"],
                "driver_dob": mock_data["dob"],
                "driver_phone": mock_data["phone"],
                "driver_email": mock_data["email"],
                "driver_address": mock_data["address"],
                "license_class": mock_data["driving_license"]["class"]
            },
            "show_cards": True,
            "cards": [{
                "type": "singpass_fetch",
                "data": {
                    "name": mock_data["full_name"],
                    "nric": mock_data["nric"][:5] + "****",
                    "dob": mock_data["dob"],
                    "address": mock_data["address"][:30] + "...",
                    "license": f"Class {mock_data['driving_license']['class']}",
                    "experience": "18 years"
                }
            }]
        }
    
    # Driver confirmed, ask about claims history
    if state.get("driver_confirmed") and not state.get("claims_history"):
        return {
            "message": "Now let me assess your risk profile. Have you made any motor insurance claims in the last 3 years?",
            "quick_replies": [
                {"label": "No Claims (NCD eligible)", "value": "no_claims"},
                {"label": "1 Minor Claim", "value": "1_minor"},
                {"label": "Multiple Claims", "value": "multiple"}
            ],
            "next_agent": "driver_eligibility",
            "data_collected": {}
        }
    
    # Claims history recorded, ask about additional drivers
    if state.get("claims_history") and not state.get("additional_drivers"):
        return {
            "message": "Would you like to add any additional named drivers to your policy? Adding named drivers can affect your premium.",
            "quick_replies": [
                {"label": "No, Just Me", "value": "none"},
                {"label": "Add 1 Driver", "value": "add_one"},
                {"label": "Add 2+ Drivers", "value": "add_multiple"}
            ],
            "next_agent": "driver_eligibility",
            "data_collected": {}
        }
    
    # Additional drivers recorded, ask about telematics
    if state.get("additional_drivers") and not state.get("telematics_consent"):
        return {
            "message": "🚗 Would you like to opt-in for our Smart Driver programme? By allowing us to monitor your driving habits through our app, you can save up to 15% on your premium!",
            "quick_replies": [
                {"label": "Yes, Save 15%!", "value": "yes"},
                {"label": "No Thanks", "value": "no"}
            ],
            "next_agent": "telematics",
            "data_collected": {}
        }
    
    # Telematics recorded, calculate and show risk assessment then premium
    if state.get("telematics_consent") and not state.get("risk_assessed") and not state.get("modify_quote") and not state.get("change_coverage") and not state.get("change_plan") and not state.get("change_telematics"):
        # Determine NCD percentage
        ncd_percent = 0
        if state.get("claims_history") == "no_claims":
            ncd_percent = 30
        elif state.get("claims_history") == "1_minor":
            ncd_percent = 10
            
        risk_level = "Low" if state.get("claims_history") == "no_claims" else ("Medium" if state.get("claims_history") == "1_minor" else "High")
        
        return {
            "message": "🔍 Analyzing your risk profile...",
            "quick_replies": [
                {"label": "View My Quote", "value": "view_quote"}
            ],
            "next_agent": "risk_assessment",
            "data_collected": {
                "risk_assessed": True,
                "ncd_percent": ncd_percent,
                "risk_level": risk_level
            },
            "show_cards": True,
            "cards": [{
                "type": "risk_fetch",
                "data": {
                    "claims": "0 claims" if state.get("claims_history") == "no_claims" else ("1 minor claim" if state.get("claims_history") == "1_minor" else "Multiple claims"),
                    "driver_risk": risk_level,
                    "vehicle_risk": "Low",
                    "ncd": f"{ncd_percent}% NCD Eligible" if ncd_percent > 0 else "Not eligible",
                    "rating": risk_level
                }
            }]
        }
    
    # Handle "Keep Current Quote" - set risk_assessed to True to trigger premium recalculation
    if state.get("keep_quote"):
        state["risk_assessed"] = True
        state["keep_quote"] = False
    
    # Modify quote - let user choose what to modify (MUST come before premium calculation)
    if state.get("modify_quote"):
        return {
            "message": "No problem! What would you like to modify in your quote?",
            "quick_replies": [
                {"label": "Change Coverage Type", "value": "change_coverage"},
                {"label": "Change Plan", "value": "change_plan"},
                {"label": "Change Telematics Option", "value": "change_telematics"},
                {"label": "Keep Current Quote", "value": "keep_quote"}
            ],
            "next_agent": "pricing",
            "data_collected": {"modify_quote": False}
        }
    
    # Risk assessed, calculate and show premium
    if state.get("risk_assessed") and not state.get("final_premium"):
        # Calculate premium
        # Third Party base rates (lower than Comprehensive)
        coverage_type = state.get("coverage_type", "third_party")
        
        if coverage_type == "third_party":
            base = 800  # Base for Third Party car
            if state.get("vehicle_type") == "motorcycle":
                base = 400
        else:
            base = 1200  # Base for Comprehensive car
            if state.get("vehicle_type") == "motorcycle":
                base = 600
        
        engine = state.get("engine_capacity", "2000cc")
        if "2001" in engine or "3000" in engine:
            base *= 1.3
        elif "above" in engine.lower() or "3000" in engine:
            base *= 1.5
        
        plan_mult = 1.2 if state.get("plan_name") == "Drive Premium" else 1.0
        
        ncd_percent = state.get("ncd_percent", 0)
        telematics_percent = 15 if state.get("telematics_consent") == "yes" else 0
        
        gross = base * plan_mult
        ncd_discount = gross * (ncd_percent / 100)
        telematics_discount = gross * (telematics_percent / 100)
        final = gross - ncd_discount - telematics_discount
        
        # Calculate plan loading amount
        plan_loading = base * (plan_mult - 1) if plan_mult > 1 else 0
        
        policy_num = f"INC-2024-{str(uuid.uuid4())[:8].upper()}"
        
        # Build breakdown based on coverage type
        breakdown = [
            {"item": f"Base Premium ({coverage_type.replace('_', ' ').title()})", "amount": f"${round(base, 2)}"},
        ]
        
        if plan_mult > 1:
            breakdown.append({"item": f"Plan Upgrade ({state.get('plan_name', 'Drive Premium')})", "amount": f"+${round(plan_loading, 2)}"})
        
        if ncd_discount > 0:
            breakdown.append({"item": f"NCD Discount ({ncd_percent}%)", "amount": f"-${round(ncd_discount, 2)}"})
        
        if telematics_discount > 0:
            breakdown.append({"item": f"Smart Driver Discount ({telematics_percent}%)", "amount": f"-${round(telematics_discount, 2)}"})
        
        breakdown.append({"item": "Final Premium", "amount": f"${round(final, 2)}"})
        
        return {
            "message": f"🎉 Great news! Based on your profile, here's your personalized quote:",
            "quick_replies": [
                {"label": "✓ Proceed to Payment", "value": "proceed_to_payment"},
                {"label": "Modify Quote", "value": "modify"}
            ],
            "next_agent": "pricing",
            "data_collected": {
                "base_premium": round(base, 2),
                "gross_premium": round(gross, 2),
                "ncd_discount": round(ncd_discount, 2),
                "telematics_discount": round(telematics_discount, 2),
                "final_premium": round(final, 2)
            },
            "show_cards": True,
            "cards": [{
                "type": "quote_summary",
                "plan_name": state.get("plan_name", "Drive Classic"),
                "coverage_type": coverage_type.replace("_", " ").title(),
                "vehicle": f"{state.get('vehicle_make', 'Toyota')} {state.get('vehicle_model', 'Camry')}",
                "premium": f"${round(final, 2)}/year",
                "breakdown": breakdown
            }]
        }
    
    # Payment initiated - show payment gateway options
    if state.get("payment_initiated") and not state.get("payment_completed"):
        return {
            "message": "💳 Please complete your payment to finalize your policy. Select your preferred payment method:",
            "quick_replies": [
                {"label": "Open Payment Gateway", "value": "open_payment_gateway"}
            ],
            "next_agent": "payment",
            "data_collected": {},
            "show_cards": True,
            "cards": [{
                "type": "payment_gateway",
                "amount": f"${state.get('final_premium', 0)}",
                "currency": "SGD",
                "payment_methods": [
                    {"id": "paynow", "name": "PayNow", "icon": "paynow"},
                    {"id": "card", "name": "Credit/Debit Card", "icon": "card"},
                    {"id": "grabpay", "name": "GrabPay", "icon": "grabpay"},
                    {"id": "paylah", "name": "DBS PayLah!", "icon": "paylah"},
                    {"id": "nets", "name": "NETS", "icon": "nets"}
                ]
            }]
        }
    
    # Payment completed - generate policy
    if state.get("payment_completed") and not state.get("documents_ready"):
        # Generate policy number in format TRV-YYYY-XXXXX
        current_year = datetime.now().year
        sequence_num = str(uuid.uuid4().int)[:5]  # 5 digit sequence
        policy_num = f"TRV-{current_year}-{sequence_num}"
        
        now = datetime.now()
        start_date = now.strftime("%d %b %Y")
        end_date = (now.replace(year=now.year + 1)).strftime("%d %b %Y")
        
        return {
            "message": "🎊 Payment successful! Your policy has been generated.",
            "quick_replies": [
                {"label": "📄 Download PDF", "value": "download_pdf"},
                {"label": "Start New Quote", "value": "new_quote"}
            ],
            "next_agent": "document",
            "data_collected": {
                "documents_ready": True,
                "policy_number": policy_num
            },
            "show_cards": True,
            "cards": [{
                "type": "policy_document",
                "policy_number": policy_num,
                "vehicle": f"{state.get('vehicle_make', 'Toyota')} {state.get('vehicle_model', 'Camry')}",
                "coverage": state.get("coverage_type", "comprehensive").replace("_", " ").title(),
                "plan": state.get("plan_name", "Drive Classic"),
                "premium": f"${state.get('final_premium', 0)}/year",
                "start_date": start_date,
                "end_date": end_date,
                "driver_name": state.get("driver_name", "Tan Ah Kow"),
                "ncd_percentage": f"{state.get('ncd_percent', 0)}%",
                "payment_reference": state.get("payment_reference", "")
            }],
            "show_policy_popup": True
        }
    
    # Handle modification choices
    if state.get("change_coverage"):
        return {
            "message": "Please select your preferred coverage type:",
            "quick_replies": [
                {"label": "Comprehensive", "value": "comprehensive"},
                {"label": "Third Party Only", "value": "third_party"}
            ],
            "next_agent": "coverage",
            "data_collected": {
                "change_coverage": False,
                "coverage_type": None,
                "plan_name": None,
                "risk_assessed": None,
                "final_premium": None
            }
        }
    
    if state.get("change_plan"):
        coverage = state.get("coverage_type", "comprehensive").replace("_", " ").title()
        return {
            "message": f"Please select your preferred plan for {coverage} coverage:",
            "quick_replies": [
                {"label": "Drive Premium", "value": "Drive Premium"},
                {"label": "Drive Classic", "value": "Drive Classic"}
            ],
            "next_agent": "coverage",
            "data_collected": {
                "change_plan": False,
                "plan_name": None,
                "risk_assessed": None,
                "final_premium": None
            }
        }
    
    if state.get("change_telematics"):
        return {
            "message": "Would you like to opt-in for our Smart Driver programme? Save up to 15% on your premium!",
            "quick_replies": [
                {"label": "Yes, Save 15%!", "value": "yes"},
                {"label": "No Thanks", "value": "no"}
            ],
            "next_agent": "telematics",
            "data_collected": {
                "change_telematics": False,
                "telematics_consent": None,
                "risk_assessed": None,
                "final_premium": None
            }
        }
    
    # Default fallback
    return {
        "message": "I'm here to help! Let me know what you'd like to do.",
        "quick_replies": [
            {"label": "Start New Quote", "value": "start"},
            {"label": "Help", "value": "help"}
        ],
        "next_agent": "orchestrator",
        "data_collected": {}
    }

# ============ API ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "Jiffy Jane Motor Insurance API", "status": "running"}

@api_router.post("/sessions", response_model=Session)
async def create_session(input: SessionCreate):
    """Create a new chat session"""
    session = Session(
        state={
            "step": "welcome",
            "vehicle_type": None,
            "registration_number": None,
            "vehicle_make": None,
            "vehicle_model": None,
            "engine_capacity": None,
            "vehicle_year": None,
            "vehicle_confirmed": None,
            "coverage_type": None,
            "plan_name": None,
            "driver_info_method": None,
            "singpass_consent": None,
            "driver_confirmed": None,
            "driver_name": None,
            "driver_nric": None,
            "driver_dob": None,
            "driver_phone": None,
            "driver_email": None,
            "driver_address": None,
            "license_class": None,
            "claims_history": None,
            "additional_drivers": None,
            "telematics_consent": None,
            "risk_assessed": None,
            "ncd_percent": None,
            "risk_level": None,
            "base_premium": None,
            "final_premium": None,
            "ncd_discount": None,
            "telematics_discount": None,
            "policy_number": None,
            "payment_initiated": None,
            "payment_completed": None,
            "payment_method": None,
            "payment_reference": None,
            "documents_ready": None
        }
    )
    
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.sessions.insert_one(doc)
    return session

@api_router.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get session by ID"""
    session = await db.sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if isinstance(session['created_at'], str):
        session['created_at'] = datetime.fromisoformat(session['created_at'])
    
    return session

@api_router.post("/chat")
async def send_message(input: MessageCreate):
    """Send a message and get AI response"""
    # Get session
    session = await db.sessions.find_one({"id": input.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = session.get("state", {})
    current_agent = session.get("current_agent", "orchestrator")
    
    # Save user message
    user_msg = Message(
        session_id=input.session_id,
        role="user",
        content=input.content
    )
    user_doc = user_msg.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.messages.insert_one(user_doc)
    
    # Process quick reply value if present
    message_content = input.quick_reply_value or input.content
    
    # Update state based on user input
    updated_state = update_state_from_input(state, message_content, current_agent)
    
    # Get AI response
    response = await get_agent_response(
        input.session_id,
        message_content,
        updated_state,
        current_agent
    )
    
    # Merge collected data into state
    if response.get("data_collected"):
        updated_state.update(response["data_collected"])
    
    # Update session with new state and agent
    next_agent = response.get("next_agent", current_agent)
    await db.sessions.update_one(
        {"id": input.session_id},
        {"$set": {"state": updated_state, "current_agent": next_agent}}
    )
    
    # Save assistant message
    assistant_msg = Message(
        session_id=input.session_id,
        role="assistant",
        content=response.get("message", ""),
        agent=next_agent,
        quick_replies=response.get("quick_replies"),
        cards=response.get("cards")
    )
    assistant_doc = assistant_msg.model_dump()
    assistant_doc['created_at'] = assistant_doc['created_at'].isoformat()
    await db.messages.insert_one(assistant_doc)
    
    return {
        "message": assistant_msg.model_dump(),
        "state": updated_state,
        "current_agent": next_agent
    }

def update_state_from_input(state: dict, user_input: str, agent: str) -> dict:
    """Update session state based on user input"""
    input_lower = user_input.lower()
    input_upper = user_input.upper()
    
    # Vehicle type
    if input_lower in ["car", "motorcycle", "🚗 car", "🏍️ motorcycle"]:
        state["vehicle_type"] = "car" if "car" in input_lower else "motorcycle"
        return state
    
    # Vehicle make - check against known makes
    if state.get("vehicle_type") and not state.get("vehicle_make"):
        all_makes = VEHICLE_MAKES.get(state.get("vehicle_type"), [])
        for make in all_makes:
            if make.lower() == input_lower:
                state["vehicle_make"] = make
                return state
    
    # Vehicle model - check against known models for the selected make
    if state.get("vehicle_make") and not state.get("vehicle_model"):
        make = state.get("vehicle_make")
        models = VEHICLE_MODELS.get(make, [])
        for model in models:
            if model.lower() == input_lower:
                state["vehicle_model"] = model
                return state
        # Accept any input as model if it's not a make name
        all_makes = VEHICLE_MAKES.get("car", []) + VEHICLE_MAKES.get("motorcycle", [])
        if input_lower not in [m.lower() for m in all_makes]:
            state["vehicle_model"] = user_input
            return state
    
    # Engine capacity
    if state.get("vehicle_model") and not state.get("engine_capacity"):
        for vtype, capacities in ENGINE_CAPACITIES.items():
            for cap in capacities:
                if cap.lower() == input_lower or cap.lower() in input_lower:
                    state["engine_capacity"] = cap
                    return state
    
    # Off-peak for cars
    if state.get("engine_capacity") and state.get("vehicle_type") == "car" and state.get("off_peak") is None:
        if "yes" in input_lower or "off-peak" in input_lower or "offpeak" in input_lower:
            state["off_peak"] = "yes_offpeak"
            return state
        elif "no" in input_lower or "regular" in input_lower:
            state["off_peak"] = "no_offpeak"
            return state
    
    # Confirm vehicle
    if input_lower in ["confirm_vehicle", "✓ confirm & continue", "confirm & continue", "confirm details", "✓ confirm details"]:
        state["vehicle_confirmed"] = True
        return state
    
    # Coverage type
    if input_lower in ["third party", "third_party", "third party only", "comprehensive"]:
        state["coverage_type"] = "comprehensive" if "comprehensive" in input_lower else "third_party"
        return state
    
    # Plan name
    if "premium" in input_lower or "classic" in input_lower:
        state["plan_name"] = "Drive Premium" if "premium" in input_lower else "Drive Classic"
        return state
    
    # Driver info method
    if input_lower in ["singpass", "use singpass", "🔐 use singpass", "manual", "enter manually"]:
        state["driver_info_method"] = "singpass" if "singpass" in input_lower else "manual"
    
    # Singpass consent
    if "consent" in input_lower or input_lower in ["✓ i consent", "i consent", "consent_yes", "consent_no"]:
        state["singpass_consent"] = "consent_yes" if "yes" in input_lower or "✓" in input_lower or "i consent" in input_lower else "consent_no"
    
    # Confirm driver
    if input_lower in ["confirm_driver", "✓ confirm details", "confirm details"] and state.get("singpass_consent"):
        state["driver_confirmed"] = True
    
    # Claims history
    if "no claims" in input_lower or input_lower == "no_claims":
        state["claims_history"] = "no_claims"
    elif "1 minor" in input_lower or input_lower == "1_minor":
        state["claims_history"] = "1_minor"
    elif "multiple" in input_lower:
        state["claims_history"] = "multiple"
    
    # Additional drivers
    if input_lower in ["no, just me", "none", "add_one", "add 1 driver", "add_multiple", "add 2+ drivers"]:
        if "no" in input_lower or "none" in input_lower or "just me" in input_lower:
            state["additional_drivers"] = "none"
        else:
            state["additional_drivers"] = "add"
    
    # Telematics
    if state.get("additional_drivers") and not state.get("telematics_consent"):
        if "yes" in input_lower or "save" in input_lower:
            state["telematics_consent"] = "yes"
        elif input_lower in ["no", "no thanks"]:
            state["telematics_consent"] = "no"
    
    # View quote
    if input_lower in ["view_quote", "view my quote"]:
        state["view_quote"] = True
    
    # Accept quote
    if input_lower in ["accept_quote", "✓ accept & generate policy", "accept & generate policy", "proceed_to_payment", "✓ proceed to payment"]:
        state["quote_accepted"] = True
        state["payment_initiated"] = True
    
    # Payment completed
    if input_lower in ["payment_completed", "payment_success"]:
        state["payment_completed"] = True
    
    # Modify quote - reset pricing state to allow modification
    if input_lower in ["modify", "modify quote", "modify_quote"]:
        state["final_premium"] = None
        state["base_premium"] = None
        state["gross_premium"] = None
        state["ncd_discount"] = None
        state["telematics_discount"] = None
        state["risk_assessed"] = None
        state["modify_quote"] = True
    
    # Handle modification choices from the modify quote menu
    if input_lower in ["change_coverage", "change coverage type"]:
        state["change_coverage"] = True
        state["modify_quote"] = False  # Clear modify flag
    
    if input_lower in ["change_plan", "change plan"]:
        state["change_plan"] = True
        state["modify_quote"] = False  # Clear modify flag
    
    if input_lower in ["change_telematics", "change telematics option"]:
        state["change_telematics"] = True
        state["modify_quote"] = False  # Clear modify flag
    
    if input_lower in ["keep_quote", "keep current quote"]:
        state["keep_quote"] = True
        state["modify_quote"] = False  # Clear modify flag
    
    return state

@api_router.get("/messages/{session_id}", response_model=List[Message])
async def get_messages(session_id: str):
    """Get all messages for a session"""
    messages = await db.messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    for msg in messages:
        if isinstance(msg['created_at'], str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return messages

@api_router.post("/welcome/{session_id}")
async def get_welcome_message(session_id: str):
    """Get initial welcome message"""
    session = await db.sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    welcome_msg = Message(
        session_id=session_id,
        role="assistant",
        content="Hi there! I'm Jiffy Jane, your friendly motor insurance assistant from Income Insurance! 🚗 I'll help you get a quick quote for your vehicle. Are you looking to insure a car or a motorcycle?",
        agent="orchestrator",
        quick_replies=[
            {"label": "🚗 Car", "value": "car"},
            {"label": "🏍️ Motorcycle", "value": "motorcycle"}
        ]
    )
    
    doc = welcome_msg.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.messages.insert_one(doc)
    
    return welcome_msg

@api_router.get("/vehicle-makes/{vehicle_type}")
async def get_vehicle_makes(vehicle_type: str):
    """Get available vehicle makes"""
    makes = VEHICLE_MAKES.get(vehicle_type.lower(), [])
    return {"makes": makes}

@api_router.get("/vehicle-models/{make}")
async def get_vehicle_models(make: str):
    """Get available vehicle models for a make"""
    models = VEHICLE_MODELS.get(make, [])
    return {"models": models}

@api_router.get("/lta-lookup/{registration_number}")
async def lta_vehicle_lookup(registration_number: str):
    """Mock LTA vehicle lookup"""
    data = MOCK_LTA_DATA.get(registration_number.upper())
    if not data:
        # Generate mock data for any registration
        return {
            "found": True,
            "data": {
                "make": "Toyota",
                "model": "Camry",
                "engine_cc": "2000cc",
                "year": 2022,
                "road_tax_valid": True,
                "accident_history": []
            }
        }
    return {"found": True, "data": data}

@api_router.get("/singpass-retrieve/{nric}")
async def singpass_retrieve(nric: str):
    """Mock Singpass data retrieval"""
    data = MOCK_SINGPASS_DATA.get(nric.upper())
    if not data:
        # Return mock data for any NRIC
        return {
            "found": True,
            "data": list(MOCK_SINGPASS_DATA.values())[0]
        }
    return {"found": True, "data": data}

@api_router.post("/generate-quote/{session_id}")
async def generate_quote(session_id: str):
    """Generate a formal quote"""
    session = await db.sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = session.get("state", {})
    
    quote = Quote(
        session_id=session_id,
        vehicle_type=state.get("vehicle_type", "car"),
        vehicle_make=state.get("vehicle_make", ""),
        vehicle_model=state.get("vehicle_model", ""),
        engine_capacity=state.get("engine_capacity", ""),
        coverage_type=state.get("coverage_type", "third_party"),
        plan_name=state.get("plan_name", "Drive Classic"),
        base_premium=state.get("base_premium", 0),
        risk_loading=0,
        ncd_discount=state.get("ncd_discount", 0),
        telematics_discount=state.get("telematics_discount", 0),
        final_premium=state.get("final_premium", 0)
    )
    
    doc = quote.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.quotes.insert_one(doc)
    
    return quote

@api_router.get("/document/{session_id}/pdf")
async def generate_pdf_document(session_id: str):
    """Generate PDF policy document"""
    session = await db.sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = session.get("state", {})
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#F96302'),
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    story = []
    
    # Header
    story.append(Paragraph("Income Insurance", title_style))
    story.append(Paragraph("Motor Insurance Policy Summary", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Policy details
    policy_number = state.get("policy_number", f"INC-2024-{str(uuid.uuid4())[:8].upper()}")
    
    story.append(Paragraph("Policy Details", heading_style))
    policy_data = [
        ["Policy Number:", policy_number],
        ["Effective Date:", datetime.now().strftime("%d %B %Y")],
        ["Expiry Date:", (datetime.now().replace(year=datetime.now().year + 1)).strftime("%d %B %Y")],
    ]
    
    t = Table(policy_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Policyholder details
    story.append(Paragraph("Policyholder Information", heading_style))
    holder_data = [
        ["Name:", state.get("driver_name", "N/A")],
        ["NRIC:", state.get("driver_nric", "N/A")],
        ["Contact:", state.get("driver_phone", "N/A")],
        ["Email:", state.get("driver_email", "N/A")],
    ]
    
    t = Table(holder_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Vehicle details
    story.append(Paragraph("Vehicle Information", heading_style))
    vehicle_type = state.get("vehicle_type") or "N/A"
    vehicle_data = [
        ["Vehicle Type:", vehicle_type.title() if vehicle_type != "N/A" else "N/A"],
        ["Make:", state.get("vehicle_make") or "N/A"],
        ["Model:", state.get("vehicle_model") or "N/A"],
        ["Engine Capacity:", state.get("engine_capacity") or "N/A"],
    ]
    
    t = Table(vehicle_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Coverage details
    story.append(Paragraph("Coverage Details", heading_style))
    coverage_type = state.get("coverage_type") or "N/A"
    final_premium = state.get('final_premium') or 0
    ncd_discount = state.get('ncd_discount') or 0
    coverage_data = [
        ["Coverage Type:", coverage_type.replace("_", " ").title() if coverage_type != "N/A" else "N/A"],
        ["Plan:", state.get("plan_name") or "N/A"],
        ["Annual Premium:", f"${final_premium:.2f}"],
        ["NCD Discount:", f"${ncd_discount:.2f}"],
    ]
    
    t = Table(coverage_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Exclusions section
    story.append(Paragraph("Policy Exclusions", heading_style))
    
    exclusion_style = ParagraphStyle(
        'ExclusionStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#92400E'),
        leftIndent=15,
        spaceBefore=3,
        spaceAfter=3
    )
    
    exclusion_intro_style = ParagraphStyle(
        'ExclusionIntro',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#78350F'),
        spaceBefore=5,
        spaceAfter=10
    )
    
    story.append(Paragraph("This policy does not cover:", exclusion_intro_style))
    
    exclusions = [
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
    ]
    
    for exclusion in exclusions:
        story.append(Paragraph(f"• {exclusion}", exclusion_style))
    
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("This is a computer-generated document. No signature is required.", styles['Normal']))
    story.append(Paragraph("Income Insurance Limited. All rights reserved.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=policy_{policy_number}.pdf"}
    )

@api_router.get("/document/{session_id}/html")
async def generate_html_document(session_id: str):
    """Generate HTML policy document"""
    session = await db.sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = session.get("state", {})
    policy_number = state.get("policy_number", f"INC-2024-{str(uuid.uuid4())[:8].upper()}")
    
    return {
        "policy_number": policy_number,
        "effective_date": datetime.now().strftime("%d %B %Y"),
        "expiry_date": (datetime.now().replace(year=datetime.now().year + 1)).strftime("%d %B %Y"),
        "policyholder": {
            "name": state.get("driver_name", "N/A"),
            "nric": state.get("driver_nric", "N/A"),
            "phone": state.get("driver_phone", "N/A"),
            "email": state.get("driver_email", "N/A"),
            "address": state.get("driver_address", "N/A")
        },
        "vehicle": {
            "type": state.get("vehicle_type") or "N/A",
            "make": state.get("vehicle_make") or "N/A",
            "model": state.get("vehicle_model") or "N/A",
            "engine_capacity": state.get("engine_capacity") or "N/A"
        },
        "coverage": {
            "type": (state.get("coverage_type") or "N/A").replace("_", " ").title() if state.get("coverage_type") else "N/A",
            "plan": state.get("plan_name") or "N/A",
            "premium": state.get("final_premium", 0),
            "ncd_discount": state.get("ncd_discount", 0),
            "telematics_discount": state.get("telematics_discount", 0)
        },
        "exclusions": [
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
        ]
    }

class PaymentRequest(BaseModel):
    session_id: str
    payment_method: str
    amount: float

class PaymentResponse(BaseModel):
    success: bool
    payment_reference: str
    message: str

@api_router.post("/payment/process")
async def process_payment(payment: PaymentRequest):
    """Process demo payment for motor insurance"""
    session = await db.sessions.find_one({"id": payment.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Generate payment reference
    payment_ref = f"PAY-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Generate policy number in format TRV-YYYY-XXXXX
    current_year = datetime.now().year
    sequence_num = str(uuid.uuid4().int)[:5]
    policy_num = f"TRV-{current_year}-{sequence_num}"
    
    # Update session with payment info and policy number
    await db.sessions.update_one(
        {"id": payment.session_id},
        {"$set": {
            "state.payment_completed": True,
            "state.payment_method": payment.payment_method,
            "state.payment_reference": payment_ref,
            "state.policy_number": policy_num,
            "state.documents_ready": True
        }}
    )
    
    # Save payment record
    payment_record = {
        "id": str(uuid.uuid4()),
        "session_id": payment.session_id,
        "payment_reference": payment_ref,
        "policy_number": policy_num,
        "payment_method": payment.payment_method,
        "amount": payment.amount,
        "currency": "SGD",
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payments.insert_one(payment_record)
    
    return {
        "success": True,
        "payment_reference": payment_ref,
        "policy_number": policy_num,
        "message": "Payment processed successfully"
    }

@api_router.get("/payment/methods")
async def get_payment_methods():
    """Get available payment methods for Singapore"""
    return {
        "methods": [
            {"id": "paynow", "name": "PayNow", "description": "Pay instantly with PayNow QR"},
            {"id": "card", "name": "Credit/Debit Card", "description": "Visa, Mastercard, AMEX"},
            {"id": "grabpay", "name": "GrabPay", "description": "Pay with your GrabPay wallet"},
            {"id": "paylah", "name": "DBS PayLah!", "description": "Pay with DBS PayLah!"},
            {"id": "nets", "name": "NETS", "description": "Pay with NETS"}
        ]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
