import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


app = FastAPI()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)


# ============================================================
# COMPANY + ROLE DATA
# ============================================================

COMPANY_CONTEXT = """
Volo Health Care Inc. is a Canadian natural health products /
nutraceutical company based in Markham, Ontario.

The careers page currently contains one REAL company opening:

REAL OPENING
--------------------------------------------------

1. Independent Sales Representative

Employment:
100% commission · uncapped · field-based

Responsibilities:
- Prospect and grow accounts across your territory
- Run sales strategies and promotions with retail owners and buyers
- Support health food and supplement stores with product knowledge
- Represent Volo at trade shows and regular account visits

Requirements:
- 2+ years of outside sales experience
- Existing relationships with health practitioners or retailers
- Valid driver's license
- Willingness to travel
- Nutraceutical or pharmaceutical background is a plus


DEMO / TEST OPENINGS
--------------------------------------------------

The following four roles are ONLY for testing the AI
compatibility feature. They should NOT be presented as
confirmed real Volo job openings.

2. Python Developer

Employment:
Full-time · backend · hybrid

Responsibilities:
- Build and maintain Python backend applications
- Develop REST APIs using FastAPI
- Work with databases and third-party APIs
- Deploy and maintain backend services

Requirements:
- Python programming experience
- FastAPI or similar backend framework
- REST API development
- Database knowledge
- Git knowledge


3. AI/ML Engineer

Employment:
Full-time · AI · machine learning

Responsibilities:
- Build AI and machine learning applications
- Develop LLM and Generative AI solutions
- Integrate AI APIs into products
- Build AI agents and automation systems

Requirements:
- Python programming
- Machine learning fundamentals
- LLM experience
- Generative AI experience
- AI API integration
- Experience building AI applications or agents


4. Frontend Developer

Employment:
Full-time · frontend · web

Responsibilities:
- Build responsive web interfaces
- Develop reusable React components
- Integrate frontend applications with REST APIs
- Improve website performance and user experience

Requirements:
- React.js
- JavaScript
- HTML
- CSS
- REST API integration
- Responsive web development


5. Marketing Associate

Employment:
Full-time · marketing · digital

Responsibilities:
- Support digital marketing campaigns
- Create social media and marketing content
- Track campaign performance
- Support brand and promotional activities

Requirements:
- Digital marketing knowledge
- Social media experience
- Content creation
- Campaign management
- Basic analytics


IMPORTANT:

Only "Independent Sales Representative" is a real currently
posted Volo opening.

The other four roles exist only to test the compatibility
matching system.
"""


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = f"""
You are an AI Compatibility Scanner for a careers demo page.

Analyze the candidate's background against ALL of these roles:

1. Independent Sales Representative
2. Python Developer
3. AI/ML Engineer
4. Frontend Developer
5. Marketing Associate

Candidate profile:
{message}

Return a COMPLETE response using exactly this structure:

Closest match: [EXACT ROLE NAME]

Why this is the closest match:
[2-4 complete sentences explaining why the candidate matches this role.
Mention specific skills or experience from the candidate.]

Skills that match:
- [skill/experience]
- [skill/experience]
- [skill/experience]

Other possible matches:
- [ROLE NAME] — [short reason]
- [ROLE NAME] — [short reason]

Recommendation:
[1-2 complete sentences explaining what the candidate should focus on.]

Important:
- Always write complete sentences.
- Never stop in the middle of a sentence.
- Do not end with "and", "or", "your", "their", "the", etc.
- Do not invent experience that the candidate did not mention.
- The roles other than Independent Sales Representative are DEMO roles for testing this compatibility feature.
- Clearly mention that the scan is a demo when appropriate.
- Keep the response around 150-220 words.
"""


# ============================================================
# REQUEST MODEL
# ============================================================

class MatchRequest(BaseModel):
    message: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


# ============================================================
# COMPATIBILITY SCAN
# ============================================================

@app.post("/api/match")
def match(req: MatchRequest):

    text = (req.message or "").strip()

    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    if not text:
        return {
            "reply": "Tell me a bit about your background first."
        }

    # --------------------------------------------------------
    # API key check
    # --------------------------------------------------------

    if not GEMINI_API_KEY:
        return {
            "reply": (
                "Server isn't configured with a Gemini API key yet. "
                "Please set GEMINI_API_KEY in your Vercel Environment Variables."
            )
        }

    # --------------------------------------------------------
    # Gemini request
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=text,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "max_output_tokens": 800,
                "temperature": 0.3,
            },
        )

        reply = (response.text or "").strip()

        if not reply:
            return {
                "reply": "Couldn't generate a response. Please try again."
            }

        return {
            "reply": reply
        }

    # --------------------------------------------------------
    # Error handling
    # --------------------------------------------------------

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        return {
            "reply": (
                "Something went wrong reaching the AI service. "
                "Please try again shortly."
            )
        }