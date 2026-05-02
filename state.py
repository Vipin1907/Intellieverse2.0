from dataclasses import dataclass, field

@dataclass
class CityState:
    # --- User Input ---
    city: str = "Lucknow"
    location: str = "Hazratganj"
    cases: int = 25
    disease: str = "dengue"

    # --- Agent 1 output ---
    contact_graph: object = None
    zone_risks: dict = field(default_factory=dict)
    hospitals:dict=field(default_factory=dict)

    # --- Agent 2 output ---
    projections: dict = field(default_factory=dict)
    peak_zone: str = ""

    # --- Agent 3 output ---
    containment_zones: list = field(default_factory=list)
    immediate_actions: list = field(default_factory=list)

    # --- Agent 4 output ---
    resource_plan: dict = field(default_factory=dict)

    # --- Agent 5 output ---
    alerts_sent: list = field(default_factory=list)