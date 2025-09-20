# app.py
from flask import Flask, jsonify, render_template, request
import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# --------------------- CONFIG ---------------------
load_dotenv()  # Load .env file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# Auto-reload templates in dev
app.config['TEMPLATES_AUTO_RELOAD'] = True

# API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("ERROR: GEMINI_API_KEY not found. Add it to .env")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("ERROR: SUPABASE_URL or SUPABASE_KEY not found. Add them to .env")

# Initialize clients
genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Gemini client initialized ✅")
print("Supabase client initialized ✅")

# --------------------- DATA LOADING ---------------------
HEALTH_DATA_CACHE = []
GEO_DATA_CACHE = None

def load_health_data():
    """Load ALL data from Supabase with pagination"""
    global HEALTH_DATA_CACHE
    try:
        print("🔍 Attempting to load ALL data from Supabase...")
        
        # Get all data with pagination (Supabase default limit is 1000)
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = supabase.table('govdata').select("*").range(offset, offset + page_size - 1).execute()
            
            if not response.data:
                break
                
            all_data.extend(response.data)
            print(f"📊 Loaded {len(response.data)} rows (total so far: {len(all_data)})")
            
            # If we got less than page_size, we're done
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        print(f"📊 Total rows loaded from Supabase: {len(all_data)}")
        
        if all_data:
            HEALTH_DATA_CACHE = all_data
            print(f"✅ Complete Supabase data loaded: {len(HEALTH_DATA_CACHE)} rows")
        else:
            print("❌ No data found in Supabase")
            
    except Exception as e:
        print(f"❌ Failed to load data from Supabase: {e}")
        HEALTH_DATA_CACHE = []

# Load data on startup
load_health_data()

# Load GeoJSON (unchanged)
try:
    geojson_path = os.path.join(APP_ROOT, "static", "data", "maharashtradist.geojson")
    with open(geojson_path, "r") as f:
        GEO_DATA_CACHE = json.load(f)
    print("GeoJSON loaded ✅")
except:
    print("WARNING: GeoJSON not found")

# --------------------- INTENT PARSER ---------------------
def parse_intent(query: str):
    """Extract year, metric, diseases, and areas from the query"""
    query_lower = query.lower()

    year_match = re.search(r"(20\d{2})", query)
    diseases = ['malaria', 'dengue', 'chikungunya', 'fever', 'diarrheal', 'poisoning']
    areas = ['mumbai', 'pune', 'nagpur', 'nashik', 'aurangabad']

    intent = {
        "year": int(year_match.group(1)) if year_match else None,
        "metric": "both",  # default to both
        "diseases": [d for d in diseases if d in query_lower],
        "areas": [a for a in areas if a in query_lower]
    }

    if any(word in query_lower for word in ["death", "fatalities", "mortality"]):
        intent["metric"] = "deaths"
    elif any(word in query_lower for word in ["case", "outbreak", "incident"]):
        intent["metric"] = "cases"

    return intent

# --------------------- DATA FILTERING (Native Python) ---------------------
def filter_data(intent):
    if not HEALTH_DATA_CACHE:
        return []

    filtered_data = []
    
    for row in HEALTH_DATA_CACHE:
        # Filter by year
        if intent["year"] and int(row.get("Year", 0)) != intent["year"]:
            continue
            
        # Filter by diseases
        if intent["diseases"]:
            disease = str(row.get("Disease", "")).lower()
            if not any(d in disease for d in intent["diseases"]):
                continue
                
        # Filter by areas
        if intent["areas"]:
            area = str(row.get("Area", "")).lower()
            if not any(a in area for a in intent["areas"]):
                continue
        
        # Convert numeric fields
        row_copy = row.copy()
        row_copy["deaths_numeric"] = int(row.get("No of deaths", 0) or 0)
        row_copy["cases_numeric"] = int(row.get("No of cases", 0) or 0)
        
        filtered_data.append(row_copy)

    return filtered_data

def summarize_data(filtered_data, intent):
    if not filtered_data:
        return ["No matching data found."]

    total_deaths = sum(row["deaths_numeric"] for row in filtered_data)
    total_cases = sum(row["cases_numeric"] for row in filtered_data)

    result = []
    year_txt = f" in {intent['year']}" if intent['year'] else ""

    if intent["metric"] == "deaths":
        result.append(f"Total deaths{year_txt}: {total_deaths}")
    elif intent["metric"] == "cases":
        result.append(f"Total cases{year_txt}: {total_cases}")
    else:
        result.append(f"Summary{year_txt}: {total_cases} cases and {total_deaths} deaths")

    # Group by disease
    disease_summary = {}
    for row in filtered_data:
        disease = row.get("Disease", "Unknown")
        if disease not in disease_summary:
            disease_summary[disease] = {"cases": 0, "deaths": 0}
        disease_summary[disease]["cases"] += row["cases_numeric"]
        disease_summary[disease]["deaths"] += row["deaths_numeric"]

    # Sort by cases and take top 5
    sorted_diseases = sorted(disease_summary.items(), 
                           key=lambda x: x[1]["cases"], 
                           reverse=True)[:5]

    for disease, data in sorted_diseases:
        result.append(f"{disease}: {data['cases']} cases, {data['deaths']} deaths")

    return result

# --------------------- ROUTES ---------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_health_data():
    """Return data for frontend"""
    return jsonify(HEALTH_DATA_CACHE)

@app.route('/refresh-data')
def refresh_data():
    """Manually refresh data from Supabase"""
    load_health_data()
    return jsonify({"status": "success", "rows": len(HEALTH_DATA_CACHE)})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please enter a question."})

    try:
        print(f"\n🔍 USER QUERY: {user_message}")
        
        # Parse intent
        intent = parse_intent(user_message)
        print(f"🎯 INTENT: {intent}")

        # Filter data
        filtered_data = filter_data(intent)
        print(f"📊 FILTERED DATA: {len(filtered_data)} rows")
        
        if filtered_data:
            total_cases = sum(row["cases_numeric"] for row in filtered_data)
            total_deaths = sum(row["deaths_numeric"] for row in filtered_data)
            print(f"💯 ACTUAL TOTALS: {total_cases} cases, {total_deaths} deaths")
        
        # Get structured summary
        structured_summary = summarize_data(filtered_data, intent)
        print(f"📋 SUMMARY: {structured_summary}")

        if structured_summary and "No matching data" not in structured_summary[0]:
            context_text = "\n".join(structured_summary)
            
            prompt = f"""Based on this Maharashtra health data, answer the user's question:

DATA:
{context_text}

USER QUESTION: {user_message}

Provide a clear, factual answer using only the data above:"""

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            bot_reply = response.text if response and response.text else structured_summary[0]
            print(f"🤖 FINAL REPLY: {bot_reply}")
        else:
            bot_reply = structured_summary[0]
            print(f"🤖 FALLBACK REPLY: {bot_reply}")

        return jsonify({"response": bot_reply})

    except Exception as e:
        print("❌ CHAT ERROR:", str(e))
        return jsonify({"response": f"Error: {str(e)}"})

@app.route("/map_data/<int:year>")
def get_map_data(year):
    if GEO_DATA_CACHE is None or not HEALTH_DATA_CACHE:
        return jsonify({"error": "Data not available"}), 500

    # Filter data for the year
    year_data = [row for row in HEALTH_DATA_CACHE if int(row.get("Year", 0)) == year]
    
    # Group by area and sum cases
    case_counts = {}
    for row in year_data:
        area = row.get("Area", "")
        cases = int(row.get("No of cases", 0) or 0)
        if area:
            case_counts[area] = case_counts.get(area, 0) + cases

    map_data_copy = json.loads(json.dumps(GEO_DATA_CACHE))
    for feature in map_data_copy.get("features", []):
        props = feature.get("properties", {})
        district_name = str(props.get("DTNAME", "")).strip().lower()
        
        # Check for matches (case insensitive)
        cases = 0
        for area_name, count in case_counts.items():
            if str(area_name).strip().lower() == district_name:
                cases = count
                break
        
        props["cases"] = cases
        props["district_display"] = district_name.title()

    return jsonify(map_data_copy)

@app.route('/approve-doctors')
def approve_doctors():
    return render_template('approve_doctors.html')

@app.route('/debug-supabase')
def debug_supabase():
    """Debug Supabase connection and table access"""
    try:
        response = supabase.table('govdata').select("count", count="exact").execute()
        response2 = supabase.table('govdata').select("*").limit(3).execute()
            
        return jsonify({
            "connection": "success",
            "count_response": response.data if response else None,  
            "sample_data": response2.data if response2 else None,
            "error": None
        })
        
    except Exception as e:
        return jsonify({
            "connection": "failed", 
            "error": str(e),
            "url": SUPABASE_URL,
            "key_prefix": SUPABASE_KEY[:20] + "..." if SUPABASE_KEY else None
        })

# --------------------- RUN ---------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)