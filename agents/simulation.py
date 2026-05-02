import numpy as np

DISEASE_PARAMS = {
    "dengue": {"R0": 2.0, "sigma": 1/5, "gamma": 1/6},
    "covid":  {"R0": 2.5, "sigma": 1/5, "gamma": 1/10},
    "flu":    {"R0": 1.3, "sigma": 1/2, "gamma": 1/5},
}

def seir_simulate(population, initial_cases, R0, sigma, gamma, hours=72):
    S = population - initial_cases
    E = initial_cases
    I = 0
    R = 0
    beta = R0 * gamma
    results = []
    for _ in range(hours):
        dt = 1.0
        new_exposed    = beta * S * I / max(population, 1) * dt
        new_infectious = sigma * E * dt
        new_recovered  = gamma * I * dt
        S -= new_exposed
        E += new_exposed - new_infectious
        I += new_infectious - new_recovered
        R += new_recovered
        results.append(int(I + E))
    return results

def run_simulation_agent(state):
    print("\n[Agent 2] Running SEIR simulation (72 hours)...")
    params = DISEASE_PARAMS.get(state.disease, DISEASE_PARAMS["dengue"])
    G = state.contact_graph
    projections = {}
    for zone in G.nodes:
        pop = G.nodes[zone]["pop"]
        if zone == state.location:
            init = state.cases
        elif G.has_edge(state.location, zone):
            w = G[state.location][zone]["weight"]
            init = max(1, int(state.cases * w * 0.15))
        else:
            init = 0
        projections[zone] = seir_simulate(pop, init, **params)
    peak = max(projections, key=lambda z: projections[z][-1])
    state.projections = projections
    state.peak_zone = peak
    print(f"[Agent 2] Done — Peak zone: {peak}")
    return state