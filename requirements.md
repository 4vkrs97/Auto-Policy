# Motor Insurance - Jiffy Jane App

## Original Problem Statement
Build an agentic, conversational Motor Insurance application for Singapore with:
- Motor Car Insurance (Private Car)
- Motor Policies (including Two-Wheelers)
- New policy purchase and quote generation
- Multi-agent architecture: Orchestrator, Intake, Coverage, Driver Identity, Risk Assessment, Pricing, Document agents
- WhatsApp-style conversational UI with button-driven interactions
- Singapore regulatory compliance (PDPA)
- Income Insurance branding (orange theme)
- Jiffy Jane mascot as chatbot avatar

## User Choices
1. AI Integration: Emergent LLM key with OpenAI GPT-4o
2. Singpass: Mock verification flow
3. LTA Lookup: Mock vehicle registration
4. Documents: Both PDF and HTML generation
5. Auth: Anonymous quote journey (no login required)

## Architecture Completed

### Backend (FastAPI)
- **Models**: Session, Message, Quote, Policy
- **Agents**: 
  - Orchestrator Agent - Controls overall flow
  - Intake Agent - Collects vehicle information
  - Coverage Agent - Presents coverage options
  - Driver Identity Agent - Handles Singpass/manual identity
  - Risk Assessment Agent - Evaluates driver/vehicle risk
  - Pricing Agent - Calculates premium
  - Document Agent - Generates policy documents

### API Endpoints
- `POST /api/sessions` - Create chat session
- `GET /api/sessions/{id}` - Get session data
- `POST /api/welcome/{session_id}` - Get welcome message
- `POST /api/chat` - Send message and get AI response
- `GET /api/messages/{session_id}` - Get message history
- `GET /api/vehicle-makes/{type}` - Get vehicle makes
- `GET /api/vehicle-models/{make}` - Get vehicle models
- `GET /api/singpass-retrieve/{nric}` - Mock Singpass data
- `GET /api/lta-lookup/{registration}` - Mock LTA lookup
- `POST /api/generate-quote/{session_id}` - Generate quote
- `GET /api/document/{session_id}/pdf` - Generate PDF
- `GET /api/document/{session_id}/html` - Get HTML document data

### Frontend (React)
- **Pages**: LandingPage, ChatPage
- **Components**: 
  - ChatBubble - Message display
  - QuickReplies - Button-driven interactions
  - TypingIndicator - Loading state
  - CoverageCard - Coverage comparison
  - QuoteCard - Premium summary
  - PolicyCard - Policy document display

### Database (MongoDB)
- Collections: sessions, messages, quotes

## Features Implemented
✅ WhatsApp-style conversational UI
✅ Income Insurance branding (orange theme)
✅ Jiffy Jane mascot avatar
✅ Vehicle type selection (Car/Motorcycle)
✅ Make and model selection
✅ Engine capacity selection
✅ Coverage type selection (Third Party/Comprehensive)
✅ Plan selection (Drive Premium/Drive Classic)
✅ Mock Singpass identity verification
✅ Claims history tracking
✅ Additional drivers support
✅ Telematics opt-in
✅ Premium calculation with NCD
✅ Quote generation
✅ PDF document generation
✅ HTML document preview

## Mocked Services
- **Singpass**: Returns mock user data (Tan Ah Kow)
- **LTA Vehicle Lookup**: Returns mock vehicle data

## Next Action Items
1. Add payment integration (before completion - currently stops at document generation)
2. Implement real Singpass integration for production
3. Implement real LTA API integration for production
4. Add policy renewal flow
5. Add claims journey
6. Add user accounts for returning customers
7. Add email/SMS notifications
8. Add multi-language support (Chinese, Malay, Tamil)

## Tech Stack
- Backend: FastAPI + Python
- Frontend: React + Tailwind CSS + Shadcn/UI
- Database: MongoDB
- AI: OpenAI GPT-4o via Emergent LLM key
- PDF Generation: ReportLab
