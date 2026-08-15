import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

app = FastAPI()

# Allow the frontend to call this API. Tighten allow_origins to your real
# domain once it's live (e.g. ["https://your-project.vercel.app"]).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

COMPANY_CONTEXT = """Volo Health Care Inc. is a Canadian (Markham, Ontario) natural
health products / nutraceutical company - a Health Canada licensed importer and
DIN/NPN holder. It in-licenses and imports health products, working with
partners, portfolio brands, and retail/practitioner channels. Their careers
page voice is unconventional: "we forgo blueprints and best practices in
favor of insight and inspiration," "we go with gut feelings more than sales
projections," obsessive work ethic, reimagining talent management.

The only currently posted role is:
Independent Sales Representative - 100% commission (uncapped), field-based.
Prospects accounts, runs sales strategies/promotions with retail owners and
buyers, supports health food and supplement stores with product knowledge,
attends trade shows, visits accounts regularly. Requirements: 2+ years
outside sales experience, existing relationships with health practitioners/
retailers, valid driver's license, willingness to travel, nutraceutical/
pharma industry experience is an asset, basic MS Office skills.

There are no other open roles listed. The company is small, so likely has
ongoing needs around: regulatory/compliance for natural health products,
marketing, operations/supply chain for importing, partnerships, and possibly
web/digital presence (their current careers page has visibly broken HTML/
shortcodes, suggesting no dedicated web/dev support)."""

SYSTEM_PROMPT = f"""You are the "Compatibility Scan" on Volo Health Care's
careers page. Company context:

{COMPANY_CONTEXT}

Given a visitor's described skills/background, give an honest, specific,
concise (under 120 words) assessment: does it fit the one posted Sales
Representative role, or does it point at a role Volo doesn't currently list
but might value (e.g. regulatory, marketing, ops, digital)? Be direct and
not falsely encouraging - say plainly if it's a stretch. End with one
concrete suggested next step (e.g. who to email and what to mention). Speak
directly to the visitor, second person, plain language, no headers or
markdown."""


class MatchRequest(BaseModel):
    message: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/match")
def match(req: MatchRequest):
    text = (req.message or "").strip()
    if not text:
        return {"reply": "Tell me a bit about your background first."}

    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {
            "reply": "Server isn't configured with an API key yet "
            "(set ANTHROPIC_API_KEY in your Vercel project's Environment "
            "Variables)."
        }

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )

        reply = "".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        ).strip()

        return {"reply": reply or "Couldn't generate a response - try again."}

    except Exception as e:
        print("ANTHROPIC ERROR:", repr(e))
        return {
            "reply": f"Anthropic API error: {str(e)}"
        }