def run_resource_agent(state):
    print("\n[Agent 4] Allocating resources using real hospital data...")

    hospitals = state.hospitals or {}
    plan = {}

    for zone in state.containment_zones:
        name  = zone["name"]
        level = zone["level"]

        # Real hospital capacity is zone mein
        zone_hospitals = hospitals.get(name, [])
        total_beds = sum(h["beds"] for h in zone_hospitals)
        icu_beds   = sum(h["icu_beds"] for h in zone_hospitals)

        # Level ke hisaab se deployment
        if level == "red":
            doctors      = 9
            testing_kits = 225
            ambulances   = 3
            beds_reserve = min(total_beds, int(total_beds * 0.3))
        elif level == "orange":
            doctors      = 6
            testing_kits = 150
            ambulances   = 2
            beds_reserve = min(total_beds, int(total_beds * 0.15))
        else:
            doctors      = 2
            testing_kits = 50
            ambulances   = 1
            beds_reserve = min(total_beds, int(total_beds * 0.05))

        plan[name] = {
            "doctors":         doctors,
            "testing_kits":    testing_kits,
            "ambulances":      ambulances,
            "beds_available":  total_beds,
            "icu_beds":        icu_beds,
            "beds_reserved":   beds_reserve,
            "hospitals":       [h["name"] for h in zone_hospitals],
        }

        print(f"  {name} ({level}): {doctors} doctors, "
              f"{testing_kits} kits, {beds_reserve}/{total_beds} beds reserved")

    state.resource_plan = plan
    print(f"[Agent 4] Done — Real hospital capacity integrated")
    return state