import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types


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

CURRENT REAL OPENING
====================

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


DEMO / TEST ROLES
=================

IMPORTANT:
The following four roles are DEMO roles created ONLY to test
the AI Compatibility Scan. They must NOT be described as
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
"""


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = f"""
You are Volo Health Care's AI Compatibility Scanner.

AVAILABLE ROLES:

1. Independent Sales Representative
- 2+ years outside sales
- Retail/health practitioner relationships
- Sales and account management
- Willingness to travel
- Nutraceutical/pharmaceutical experience is a plus
- REAL currently posted role

2. Python Developer — DEMO ROLE
- Python
- FastAPI/backend development
- REST APIs
- SQL/databases
- Git

3. AI/ML Engineer — DEMO ROLE
- Python
- Machine Learning
- Generative AI / LLMs
- AI APIs
- AI agents / automation

4. Frontend Developer — DEMO ROLE
- React.js
- JavaScript
- HTML/CSS
- REST APIs
- Responsive web development

5. Marketing Associate — DEMO ROLE
- Digital marketing
- Social media
- Content creation
- Campaign management
- Analytics


CANDIDATE:
{message}


YOUR TASK:

Compare the candidate ONLY against the skills and requirements listed above.

If the candidate clearly matches one role, respond in ONLY 2-3 short sentences:

"Closest match: [EXACT ROLE NAME]

Your [specific skills/experience] match this role because [short explanation]."

If the candidate matches more than one role, choose the SINGLE strongest match.

If the candidate does NOT meaningfully match any role, respond:

"No strong match found among the current roles.

Your background in [their actual skills] does not closely match the requirements of the listed roles. You may want to look for roles focused on [relevant area]."

IMPORTANT RULES:
- Maximum 3 sentences.
- Keep the response simple and conversational.
- Always mention the EXACT role name.
- Explain briefly WHY the candidate matches or does not match.
- Use only skills the candidate actually provided.
- Never invent experience.
- Do not list multiple roles.
- Do not use headings such as "Skills that match", "Recommendation", etc.
- Do not provide long explanations.
- Do not mention demo roles unless necessary.
- "Independent Sales Representative" is the only REAL currently posted role.
- Python Developer, AI/ML Engineer, Frontend Developer and Marketing Associate are DEMO roles used only for testing the compatibility scanner.
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
    # EMPTY INPUT
    # --------------------------------------------------------

    if not text:

        return {
            "reply": "Tell me a bit about your background first."
        }


    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not GEMINI_API_KEY or client is None:

        return {
            "reply": (
                "The Gemini API is not configured. "
                "Please check the GEMINI_API_KEY environment variable."
            )
        }


    # --------------------------------------------------------
    # BUILD CANDIDATE PROMPT
    # --------------------------------------------------------

    candidate_prompt = f"""
{COMPANY_CONTEXT}

============================================================
CANDIDATE PROFILE
============================================================

{text}

============================================================
TASK
============================================================

Analyze this candidate against ALL five roles.

Choose the single closest role.

Return the complete compatibility analysis using the
required structure from the system instructions.

Make sure the response is complete and does not end
mid-sentence.
"""


    # --------------------------------------------------------
    # GEMINI REQUEST
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=candidate_prompt,

            config=types.GenerateContentConfig(

                system_instruction=SYSTEM_PROMPT,

                max_output_tokens=800,

                temperature=0.3,

            ),
        )


        # ----------------------------------------------------
        # GET RESPONSE
        # ----------------------------------------------------

        reply = (response.text or "").strip()


        if not reply:

            return {
                "reply": (
                    "The AI did not return a response. "
                    "Please try the scan again."
                )
            }


        # ----------------------------------------------------
        # RETURN TO FRONTEND
        # ----------------------------------------------------

        return {
            "reply": reply
        }


    # --------------------------------------------------------
    # GEMINI ERROR
    # --------------------------------------------------------

    except Exception as e:

        print("========================================")
        print("GEMINI ERROR")
        print(repr(e))
        print("========================================")


        return {
            "reply": f"Gemini error: {type(e).__name__}: {str(e)}"
        }