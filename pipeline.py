from langgraph.graph import StateGraph, END
from state import CityState
from agents.mobility    import run_mobility_agent
from agents.simulation  import run_simulation_agent
from agents.containment import run_containment_agent
from agents.resources   import run_resource_agent
from agents.broadcast   import run_broadcast_agent
import time

# ── Node functions ──────────────────────────────
def mobility_node(state: dict) -> dict:
    cs = CityState(**state)
    cs = run_mobility_agent(cs)
    return cs.__dict__

def simulation_node(state: dict) -> dict:
    cs = CityState(**state)
    cs = run_simulation_agent(cs)
    return cs.__dict__

def containment_node(state: dict) -> dict:
    cs = CityState(**state)
    cs = run_containment_agent(cs)
    return cs.__dict__

def resources_node(state: dict) -> dict:
    cs = CityState(**state)
    cs = run_resource_agent(cs)
    return cs.__dict__

def broadcast_node(state: dict) -> dict:
    cs = CityState(**state)
    cs = run_broadcast_agent(cs)
    return cs.__dict__

# ── Build Graph ─────────────────────────────────
def build_graph():
    graph = StateGraph(dict)

    # 5 nodes add karo
    graph.add_node("mobility",    mobility_node)
    graph.add_node("simulation",  simulation_node)
    graph.add_node("containment", containment_node)
    graph.add_node("resources",   resources_node)
    graph.add_node("broadcast",   broadcast_node)

    # Flow define karo
    graph.set_entry_point("mobility")
    graph.add_edge("mobility",    "simulation")
    graph.add_edge("simulation",  "containment")
    graph.add_edge("containment", "resources")
    graph.add_edge("resources",   "broadcast")
    graph.add_edge("broadcast",   END)

    return graph.compile()

# ── Run ─────────────────────────────────────────
def run_pipeline(city="Lucknow", location="Hazratganj",
                 cases=25, disease="dengue"):

    print(f"\n{'='*52}")
    print(f"  ContagionGrid — LangGraph Pipeline")
    print(f"  City: {city} | Zone: {location}")
    print(f"  Cases: {cases} | Disease: {disease.upper()}")
    print(f"{'='*52}\n")

    start = time.time()
    app   = build_graph()

    initial = {
        "city": city, "location": location,
        "cases": cases, "disease": disease,
        "contact_graph": None,
        "zone_risks": {}, "projections": {},
        "peak_zone": "", "containment_zones": [],
        "immediate_actions": [], "resource_plan": {},
        "alerts_sent": [],
    }

    final = app.invoke(initial)
    elapsed = time.time() - start

    print(f"\n{'='*52}")
    print(f"  ✅ Pipeline complete in {elapsed:.1f}s")
    print(f"  Zones: {len(final.get('containment_zones',[]))}")
    print(f"  Peak:  {final.get('peak_zone','-')}")
    print(f"  Report: output/report.json")
    print(f"{'='*52}\n")
    return final

if __name__ == "__main__":
    run_pipeline()