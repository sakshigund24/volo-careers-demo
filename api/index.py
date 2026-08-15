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

SYSTEM_PROMPT = """
You are an AI Compatibility Scanner for a careers demo page.

Your job is to compare a candidate's actual skills and experience
against the five roles provided in the company context.

IMPORTANT RULES:

1. Analyze ALL five roles before choosing the closest match.

2. The "Closest match" must be EXACTLY one of these role names:

   Independent Sales Representative
   Python Developer
   AI/ML Engineer
   Frontend Developer
   Marketing Associate

3. Do NOT invent skills, education, experience, years of experience,
   certifications, or achievements that the candidate did not mention.

4. Base the answer only on the candidate's provided information.

5. Independent Sales Representative is the ONLY real currently
   posted Volo opening.

6. Python Developer, AI/ML Engineer, Frontend Developer and
   Marketing Associate are DEMO / TEST roles only.

7. If the closest match is a demo role, clearly say that it is
   a demo role and NOT a confirmed Volo opening.

8. If the candidate is not a strong match for the real sales role,
   do not force them into it. Choose the role that actually matches
   their skills best.

9. Write complete sentences.

10. Never stop in the middle of a sentence.

11. Do not end the response with incomplete phrases such as:
    "and", "or", "your", "their", "the", "with", "which", etc.

12. Keep the response concise but complete.

13. Target approximately 150-220 words.

14. Do not include unnecessary disclaimers.

Use this exact structure:

Closest match: [EXACT ROLE NAME]

Why this is the closest match:
[2-4 complete sentences explaining why this role matches the
candidate. Mention specific candidate skills.]

Skills that match:
- [specific matching skill]
- [specific matching skill]
- [specific matching skill]

Other possible matches:
- [ROLE NAME] — [short explanation]
- [ROLE NAME] — [short explanation]

Recommendation:
[1-2 complete sentences explaining what the candidate should
highlight or improve.]

Demo status:
[Clearly state whether the recommended role is a demo/test role
or the real currently posted opening.]
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

            model="gemini-2.5-flash",

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
            "reply": (
                "Something went wrong while running the "
                "compatibility scan. Please try again shortly."
            )
        }