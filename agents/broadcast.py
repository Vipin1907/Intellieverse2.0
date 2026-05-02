import json, os

def run_broadcast_agent(state):
    print("\n[Agent 5] Broadcasting alerts...")
    os.makedirs("output", exist_ok=True)
    alerts = []

    # Hindi public alert
    red_zones = [z["name"] for z in state.containment_zones if z["level"] == "red"]
    if red_zones:
        msg = f"सावधान: {', '.join(red_zones)} में {state.disease} के मामले मिले हैं। घर में पानी जमा न होने दें। नजदीकी टेस्टिंग सेंटर जाएं।"
        alerts.append({"type": "public_sms", "message": msg})
        print(f"[Agent 5] Hindi SMS ready: {msg[:60]}...")

    # Full report save karo
    report = {
        "city": state.city,
        "disease": state.disease,
        "outbreak_location": state.location,
        "initial_cases": state.cases,
        "peak_zone": state.peak_zone,
        "immediate_actions": state.immediate_actions,
        "containment_zones": state.containment_zones,
        "resource_plan": state.resource_plan,
        "alerts": alerts,
    }

    with open("output/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    alerts.append({"type": "report", "path": "output/report.json"})
    state.alerts_sent = alerts
    print(f"[Agent 5] Done — Report saved to output/report.json")
    return state