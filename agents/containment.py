import os, json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_containment_agent(state):
    print("\n[Agent 3] Gemini designing containment plan...")

    summary = []
    for zone, proj in state.projections.items():
        summary.append(
            f"{zone}: {proj[23]} cases (24h), {proj[47]} cases (48h), {proj[71]} cases (72h)"
        )

    prompt = f"""You are an epidemic containment architect for {state.city}, India.

Outbreak detected: {state.location}, {state.cases} confirmed {state.disease} cases.

72-hour spread projections:
{chr(10).join(summary)}

Design a containment plan. Return ONLY valid JSON, no extra text, no markdown:
{{
  "zones": [
    {{
      "name": "zone name",
      "level": "red",
      "restrictions": ["Close weekend markets", "Mandatory fogging"],
      "testing_centers": 2,
      "reason": "Highest projected cases, origin zone"
    }}
  ],
  "immediate_actions": ["Deploy rapid response team", "Alert hospitals"]
}}

Rules:
- red = highest risk zones
- orange = medium risk
- yellow = monitoring only
- Include all 8 zones"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text
    start = text.find("{")
    end = text.rfind("}") + 1
    plan = json.loads(text[start:end])

    state.containment_zones = plan["zones"]
    state.immediate_actions = plan.get("immediate_actions", [])
    print(f"[Agent 3] Done — {len(plan['zones'])} zones planned by Gemini")
    return state