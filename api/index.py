import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


app = FastAPI()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gemini client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


COMPANY_CONTEXT = """
Volo Health Care Inc. is a Canadian (Markham, Ontario) natural
health products / nutraceutical company - a Health Canada licensed importer
and DIN/NPN holder. It in-licenses and imports health products, working with
partners, portfolio brands, and retail/practitioner channels.

Their careers page voice is unconventional:
"we forgo blueprints and best practices in favor of insight and inspiration,"
"we go with gut feelings more than sales projections," obsessive work ethic,
reimagining talent management.

The only currently posted role is:

Independent Sales Representative - 100% commission (uncapped), field-based.

Prospects accounts, runs sales strategies/promotions with retail owners and
buyers, supports health food and supplement stores with product knowledge,
attends trade shows, visits accounts regularly.

Requirements:
2+ years outside sales experience,
existing relationships with health practitioners/retailers,
valid driver's license,
willingness to travel,
nutraceutical/pharma industry experience is an asset,
basic MS Office skills.

There are no other open roles listed.

The company is small, so likely has ongoing needs around:
regulatory/compliance for natural health products,
marketing,
operations/supply chain for importing,
partnerships,
and possibly web/digital presence.
"""


SYSTEM_PROMPT = f"""
You are the "Compatibility Scan" on Volo Health Care's careers page.

Company context:

{COMPANY_CONTEXT}

Given a visitor's described skills/background, give an honest, specific,
concise (under 120 words) assessment:

- Does it fit the one posted Sales Representative role?
- Or does it point at a role Volo doesn't currently list but might value,
  such as regulatory, marketing, operations, or digital?
- Be direct and do not falsely encourage the visitor.
- Say plainly if it is a stretch.
- End with one concrete suggested next step, such as who to email and what
  to mention.

Speak directly to the visitor.
Use second person.
Use plain language.
No headers.
No markdown.
"""


class MatchRequest(BaseModel):
    message: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/match")
def match(req: MatchRequest):

    text = (req.message or "").strip()

    if not text:
        return {
            "reply": "Tell me a bit about your background first."
        }

    if not GEMINI_API_KEY:
        return {
            "reply": (
                "Server isn't configured with a Gemini API key yet. "
                "Set GEMINI_API_KEY in your Vercel Environment Variables."
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

        return {
            "reply": reply or "Couldn't generate a response - try again."
        }

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        return {
            "reply": f"Gemini API error: {str(e)}"
        }