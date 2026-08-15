import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


app = FastAPI()


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Gemini Configuration
# --------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# --------------------------------------------------
# Volo Health Care Context
# --------------------------------------------------

COMPANY_CONTEXT = """
Volo Health Care Inc. is a Canadian natural health products /
nutraceutical company based in Markham, Ontario.

Volo is a Health Canada licensed importer and DIN/NPN holder.
The company works with health products, portfolio brands,
retailers, practitioners and partners.

CURRENT OPEN ROLE:

Independent Sales Representative

100% commission · uncapped · field-based

Responsibilities:
- Prospect and grow accounts across your territory
- Run sales strategies and promotions with retail owners and buyers
- Support health food and supplement stores with product knowledge
- Represent Volo at trade shows and regular account visits

What Volo is looking for:
- 2+ years of outside sales experience
- Existing relationships with health practitioners or retailers
- Valid driver's license and willingness to travel
- Nutraceutical or pharmaceutical background is a plus

IMPORTANT:
This is the ONLY currently posted/open role on the careers page.

There are currently NO officially posted openings for:
- Software Developer
- Python Developer
- AI Engineer
- Machine Learning Engineer
- AI Agent Developer
- Web Developer
- Marketing
- Operations
- Regulatory
- Supply Chain

However, because Volo is a small company, someone with experience
in areas such as technology, AI, software development, marketing,
operations, regulatory, supply chain, partnerships or digital
could potentially contact the company about future opportunities.

These are NOT currently open positions.
"""


# --------------------------------------------------
# AI System Prompt
# --------------------------------------------------

SYSTEM_PROMPT = f"""
You are the "Compatibility Scan" on Volo Health Care's careers page.

Company context:

{COMPANY_CONTEXT}


Your task:

Given a visitor's skills, experience and background, determine
whether they are a good match for Volo's CURRENT open role.

The CURRENT open role is:

Independent Sales Representative


IMPORTANT RULES:

1. If the visitor is a good match for the current position,
you MUST explicitly use the exact role name:

"Independent Sales Representative"

Do NOT replace the role name with:
- Sales role
- Sales Representative role
- B2B Sales role
- Field Sales role

Always use the exact title:
Independent Sales Representative


2. Evaluate the visitor against the actual requirements:

- 2+ years of outside sales experience
- Existing relationships with health practitioners or retailers
- Valid driver's license
- Willingness to travel
- Nutraceutical or pharmaceutical background is a plus


3. If the visitor does NOT fit the Independent Sales Representative
role, say so honestly.

Do NOT falsely encourage them to apply.


4. If their skills suggest another possible area Volo might value,
you may mention it.

Examples:
- AI
- Python
- Software Development
- Web Development
- Marketing
- Operations
- Regulatory
- Supply Chain
- Digital

BUT clearly state that these are NOT currently listed as open roles.


5. Do NOT invent job openings.

There is currently ONLY ONE officially posted role:
Independent Sales Representative.


6. Keep the response concise.

Maximum 120 words.


7. Your response should naturally include:

- Whether the visitor is a match
- The exact role name if they are a match
- The main reason for the assessment
- Missing requirements if they are not a match
- One concrete next step


8. Speak directly to the visitor.

Use "you" and "your".


9. Use simple, professional language.


10. Do NOT use markdown.
Do NOT use headings.
Do NOT use bullet points.


Example of a GOOD response for a sales candidate:

"You’re a strong fit for the Independent Sales Representative
role. Your 3 years of outside B2B sales experience and existing
retail relationships match two of Volo’s key requirements. Your
experience could be especially useful for developing accounts and
working with retail owners and buyers. If you also have a valid
driver’s license and are comfortable travelling for a field-based,
100% commission role, you should consider applying. Highlight your
sales results, retail relationships and territory experience when
you contact Volo."


Example of a GOOD response for a developer:

"You’re not a strong match for Volo’s current Independent Sales
Representative role because your background is in Python and AI
rather than outside sales, and the position requires retail or
health-practitioner relationships. Your AI and software skills could
potentially be relevant to a future digital or technology need, but
Volo does not currently list such a position. Your best next step is
to contact Volo directly, introduce your technical background and
ask whether they have upcoming technology or digital projects."
"""


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class MatchRequest(BaseModel):
    message: str


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


# --------------------------------------------------
# Compatibility Match
# --------------------------------------------------

@app.post("/api/match")
def match(req: MatchRequest):

    text = (req.message or "").strip()

    # Empty input
    if not text:
        return {
            "reply": "Tell me a bit about your background first."
        }

    # Gemini API key check
    if not GEMINI_API_KEY:
        return {
            "reply": (
                "Server isn't configured with a Gemini API key yet. "
                "Please set GEMINI_API_KEY in your Vercel Environment Variables."
            )
        }

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=text,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "max_output_tokens": 800,
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

    except Exception as e:

        # Print detailed error to Vercel logs
        print("GEMINI ERROR:", repr(e))

        return {
            "reply": (
                "Something went wrong reaching the AI service. "
                "Please try again shortly."
            )
        }