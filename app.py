from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json, os, subprocess, csv
from datetime import datetime
from pipeline import run_pipeline

app = FastAPI()

os.makedirs("output", exist_ok=True)
os.makedirs("data", exist_ok=True)      # CSV files yahan
os.makedirs("opd_records", exist_ok=True)  # OPD submissions yahan

app.mount("/output", StaticFiles(directory="output"), name="output")

# ── MODELS ────────────────────────────────────────────────────────────────

class OutbreakInput(BaseModel):
    city: str = "Lucknow"
    location: str = "Hazratganj"
    cases: int = 25
    disease: str = "dengue"

class OPDBooking(BaseModel):
    name: str
    age: str
    phone: str
    area: str
    hospital: str
    symptoms: List[str]
    token: str

# ── EXISTING ROUTES ───────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse("web/index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return FileResponse("web/dashboard.html")

@app.post("/api/simulate")
async def simulate(data: OutbreakInput):
    try:
        run_pipeline(
            city=data.city,
            location=data.location,
            cases=data.cases,
            disease=data.disease
        )
        subprocess.run(
            ["python", "map_generator.py"],
            capture_output=True,
            text=True
        )
        with open("output/report.json", "r", encoding="utf-8") as f:
            report = json.load(f)
        return {
            "status": "success",
            "report": report,
            "map_url": "/output/lucknow_map.html"
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}

@app.get("/api/report")
async def get_report():
    try:
        with open("output/report.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"error": "No report yet"}

# ── NEW: GET /api/hospitals ───────────────────────────────────────────────
# lucknow_hospitals.csv se data padhta hai
# CSV format expected:
#   id, name, loc, dist, beds, avail, icu, amb, doc, load, opd, iso
# Agar CSV nahi mila → fallback default data return karta hai

@app.get("/api/hospitals")
async def get_hospitals():
    csv_path = "data/lucknow_hospitals.csv"

    # Fallback default data (index.html ke DEFAULT_HOSPITALS se match karta hai)
    default = [
        {"id":0,"name":"King George Medical University","loc":"Chowk, Lucknow · Govt. Hospital","dist":"2.4 km","beds":350,"avail":120,"icu":45,"amb":8,"doc":45,"load":"Moderate Load","opd":True,"iso":True},
        {"id":1,"name":"Ram Manohar Lohia Institute","loc":"Vibhuti Khand, Lucknow · Govt. Hospital","dist":"5.1 km","beds":250,"avail":85,"icu":30,"amb":5,"doc":32,"load":"Low Load","opd":True,"iso":False},
        {"id":2,"name":"Balrampur Hospital","loc":"Golaganj, Lucknow · Govt. Hospital","dist":"3.2 km","beds":180,"avail":60,"icu":20,"amb":4,"doc":28,"load":"Low Load","opd":True,"iso":False},
        {"id":3,"name":"Civil Hospital Lucknow","loc":"Qaiserbagh, Lucknow · Govt. Hospital","dist":"4.0 km","beds":280,"avail":95,"icu":35,"amb":6,"doc":38,"load":"Moderate Load","opd":True,"iso":True},
        {"id":4,"name":"Medanta Lucknow","loc":"Amar Shaheed Path · Private","dist":"8.7 km","beds":300,"avail":42,"icu":60,"amb":6,"doc":55,"load":"High Load","opd":True,"iso":True},
        {"id":5,"name":"District Women Hospital","loc":"Hazratganj, Lucknow · Govt. Hospital","dist":"1.8 km","beds":160,"avail":55,"icu":18,"amb":3,"doc":22,"load":"Low Load","opd":True,"iso":False},
    ]

    if not os.path.exists(csv_path):
        return default

    try:
        hospitals = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                hospitals.append({
                    "id":     int(row.get("id", 0)),
                    "name":   row.get("name", ""),
                    "loc":    row.get("loc", ""),
                    "dist":   row.get("dist", "—"),
                    "beds":   int(row.get("beds", 0)),
                    "avail":  int(row.get("avail", 0)),
                    "icu":    int(row.get("icu", 0)),
                    "amb":    int(row.get("amb", 0)),
                    "doc":    int(row.get("doc", 0)),
                    "load":   row.get("load", "Low Load"),
                    "opd":    row.get("opd", "true").lower() == "true",
                    "iso":    row.get("iso", "false").lower() == "true",
                })
        return hospitals if hospitals else default
    except Exception as e:
        print(f"CSV read error: {e}")
        return default


# ── NEW: POST /api/opd/book ───────────────────────────────────────────────
# OPD form submission store karta hai
# Data 2 jagah save hota hai:
#   1. opd_records/opd_bookings.json  → sab bookings ek file mein (hospital dashboard ke liye)
#   2. output/opd_latest.json         → last booking (ContagionGrid pipeline input ke liye)

@app.post("/api/opd/book")
async def book_opd(booking: OPDBooking):
    try:
        record = {
            "token":     booking.token,
            "name":      booking.name,
            "age":       booking.age,
            "phone":     booking.phone,
            "area":      booking.area,
            "hospital":  booking.hospital,
            "symptoms":  booking.symptoms,
            "timestamp": datetime.now().isoformat(),
            "status":    "pending"   # hospital dashboard mein seen/done ho sakta hai
        }

        # ── File 1: opd_records/opd_bookings.json (append) ──────────────
        bookings_path = "opd_records/opd_bookings.json"
        if os.path.exists(bookings_path):
            with open(bookings_path, "r", encoding="utf-8") as f:
                all_bookings = json.load(f)
        else:
            all_bookings = []

        all_bookings.append(record)

        with open(bookings_path, "w", encoding="utf-8") as f:
            json.dump(all_bookings, f, ensure_ascii=False, indent=2)

        # ── File 2: output/opd_latest.json (ContagionGrid input format) ──
        # Ye format pipeline.py ko seedha pass ho sakta hai
        latest = {
            "token":    booking.token,
            "hospital": booking.hospital,
            "area":     booking.area,
            "symptoms": booking.symptoms,
            "timestamp": record["timestamp"]
        }
        with open("output/opd_latest.json", "w", encoding="utf-8") as f:
            json.dump(latest, f, ensure_ascii=False, indent=2)

        return {
            "status":  "success",
            "token":   booking.token,
            "message": "OPD booking confirmed"
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}
# ── Ye 3 routes apne app.py mein add karo existing routes ke saath ──────

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return FileResponse("web/login.html")

@app.get("/hospital_dashboard", response_class=HTMLResponse)
async def hospital_dashboard():
    return FileResponse("web/hospital_dashboard.html")

@app.get("/cmo_dashboard", response_class=HTMLResponse)
async def cmo_dashboard():
    return FileResponse("web/cmo_dashboard.html")

@app.get("/dm_dashboard", response_class=HTMLResponse)
async def dm_dashboard():
    return FileResponse("web/dm_dashboard.html")

# ── HOSPITAL DASHBOARD ROUTES ──────────────────────────────────────────

class StatusUpdate(BaseModel):
    token: str
    status: str

@app.post("/api/opd/status")
async def update_opd_status(update: StatusUpdate):
    try:
        bookings_path = "opd_records/opd_bookings.json"
        if not os.path.exists(bookings_path):
            return {"status": "error", "message": "No bookings file found"}

        with open(bookings_path, "r", encoding="utf-8") as f:
            all_bookings = json.load(f)

        updated = False
        for booking in all_bookings:
            if booking["token"] == update.token:
                booking["status"] = update.status
                booking["updated_at"] = datetime.now().isoformat()
                updated = True
                break

        with open(bookings_path, "w", encoding="utf-8") as f:
            json.dump(all_bookings, f, ensure_ascii=False, indent=2)

        return {"status": "success", "token": update.token, "new_status": update.status}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/disease/summary")
async def disease_summary(hospital: Optional[str] = None):
    try:
        with open("opd_records/opd_bookings.json", "r", encoding="utf-8") as f:
            all_bookings = json.load(f)
        if hospital:
            all_bookings = [b for b in all_bookings if b["hospital"] == hospital]
        return {"status": "success", "bookings": all_bookings}
    except FileNotFoundError:
        return {"status": "success", "bookings": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}
@app.get("/dm_dashboard", response_class=HTMLResponse)
async def dm_dashboard():
    return FileResponse("web/dm_dashboard.html")


# ── OPTIONAL: GET /api/opd/list ───────────────────────────────────────────
# Hospital dashboard ke liye — saari bookings ek saath
# Layer 2 (hospital login) mein use hoga

@app.get("/api/opd/list")
async def list_opd(hospital: Optional[str] = None):
    """
    hospital query param se filter kar sakte ho:
    GET /api/opd/list?hospital=Balrampur+Hospital
    """
    try:
        with open("opd_records/opd_bookings.json", "r", encoding="utf-8") as f:
            all_bookings = json.load(f)
        if hospital:
            all_bookings = [b for b in all_bookings if b["hospital"] == hospital]
        return {"status": "success", "count": len(all_bookings), "bookings": all_bookings}
    except:
        return {"status": "success", "count": 0, "bookings": []}
