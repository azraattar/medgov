# app.py
from flask import Flask, jsonify, render_template, request
import pandas as pd
import json
import os
import re
from dotenv import load_dotenv
import google.genai as genai
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
client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Gemini client initialized ✅")
print("Supabase client initialized ✅")

# --------------------- DATA LOADING ---------------------
HEALTH_DATA_CACHE = pd.DataFrame()
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
            HEALTH_DATA_CACHE = pd.DataFrame(all_data)
            print(f"✅ Complete Supabase data loaded: {len(HEALTH_DATA_CACHE)} rows")
            print(f"📋 DataFrame columns: {list(HEALTH_DATA_CACHE.columns)}")
            
            # Convert date strings back to proper format if needed
            date_columns = ['Date of start', 'Date of reporting']
            for col in date_columns:
                if col in HEALTH_DATA_CACHE.columns:
                    HEALTH_DATA_CACHE[col] = pd.to_datetime(HEALTH_DATA_CACHE[col], errors='coerce')
            
        else:
            print("❌ No data found in Supabase")
            
    except Exception as e:
        print(f"❌ Failed to load data from Supabase: {e}")
        # Fallback to CSV if Supabase fails
        try:
            csv_path = os.path.join(APP_ROOT, "static", "data", "govdata.csv")
            HEALTH_DATA_CACHE = pd.read_csv(csv_path).fillna(0)
            print(f"Fallback: CSV loaded with {len(HEALTH_DATA_CACHE)} rows")
        except FileNotFoundError:
            print("❌ CRITICAL: Both Supabase and CSV failed!")

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

# --------------------- DATA FILTERING (Fixed for actual Supabase column names) ---------------------
def filter_data(intent):
    if HEALTH_DATA_CACHE.empty:
        return pd.DataFrame()

    df = HEALTH_DATA_CACHE.copy()

    # Use actual Supabase column names (with capitals and spaces)
    if intent["year"]:
        df = df[df["Year"] == intent["year"]]  # ✅ Updated
    if intent["diseases"]:
        df = df[df["Disease"].str.lower().str.contains("|".join(intent["diseases"]), na=False)]  # ✅ Updated
    if intent["areas"]:
        df = df[df["Area"].str.lower().str.contains("|".join(intent["areas"]), na=False)]  # ✅ Updated

    # Convert to numeric using actual column names
    df["deaths_numeric"] = pd.to_numeric(df["No of deaths"], errors="coerce").fillna(0)  # ✅ Updated
    df["cases_numeric"] = pd.to_numeric(df["No of cases"], errors="coerce").fillna(0)   # ✅ Updated

    return df

def summarize_data(df, intent):
    if df.empty:
        return ["No matching data found."]

    total_deaths = int(df["deaths_numeric"].sum())
    total_cases = int(df["cases_numeric"].sum())

    result = []
    year_txt = f" in {intent['year']}" if intent['year'] else ""

    if intent["metric"] == "deaths":
        result.append(f"Total deaths{year_txt}: {total_deaths}")
    elif intent["metric"] == "cases":
        result.append(f"Total cases{year_txt}: {total_cases}")
    else:
        result.append(f"Summary{year_txt}: {total_cases} cases and {total_deaths} deaths")

    # Breakdown by disease using actual column name
    disease_summary = (
        df.groupby("Disease")[["cases_numeric", "deaths_numeric"]]  # ✅ Updated
        .sum()
        .sort_values("cases_numeric", ascending=False)
        .head(5)
    )

    for disease, row in disease_summary.iterrows():
        result.append(
            f"{disease}: {int(row['cases_numeric'])} cases, {int(row['deaths_numeric'])} deaths"
        )

    return result

# --------------------- ROUTES ---------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_health_data():
    """Return data for frontend - now from Supabase"""
    if not HEALTH_DATA_CACHE.empty:
        return jsonify(HEALTH_DATA_CACHE.to_dict(orient="records"))
    else:
        # Try to reload from Supabase
        load_health_data()
        return jsonify(HEALTH_DATA_CACHE.to_dict(orient="records") if not HEALTH_DATA_CACHE.empty else [])

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
        # DEBUG: Print the original query
        print(f"\n🔍 USER QUERY: {user_message}")
        
        # Parse intent
        intent = parse_intent(user_message)
        print(f"🎯 INTENT: {intent}")

        # Filter data
        filtered_df = filter_data(intent)
        print(f"📊 FILTERED DATA: {len(filtered_df)} rows")
        
        if not filtered_df.empty:
            # DEBUG: Show actual totals
            total_cases = int(filtered_df["cases_numeric"].sum())
            total_deaths = int(filtered_df["deaths_numeric"].sum())
            print(f"💯 ACTUAL TOTALS: {total_cases} cases, {total_deaths} deaths")
            
            # Show sample data
            print(f"📝 SAMPLE ROWS:")
            for _, row in filtered_df.head(3).iterrows():
                print(f"   {row['Year']} | {row['Area']} | {row['Disease']} | {row['cases_numeric']} cases | {row['deaths_numeric']} deaths")
        
        # Get structured summary
        structured_summary = summarize_data(filtered_df, intent)
        print(f"📋 SUMMARY: {structured_summary}")

        if structured_summary and "No matching data" not in structured_summary[0]:
            context_text = "\n".join(structured_summary)
            
            prompt = f"""Based on this Maharashtra health data, answer the user's question:

DATA:
{context_text}

USER QUESTION: {user_message}

Provide a clear, factual answer using only the data above:"""

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
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
    if GEO_DATA_CACHE is None or HEALTH_DATA_CACHE.empty:
        return jsonify({"error": "Data not available"}), 500

    # Use actual Supabase column names
    df_year = HEALTH_DATA_CACHE[HEALTH_DATA_CACHE["Year"] == year].copy()  # ✅ Updated
    df_year["No of cases"] = pd.to_numeric(df_year["No of cases"], errors="coerce").fillna(0)
    case_counts = df_year.groupby("Area")["No of cases"].sum().astype(int).to_dict()  # ✅ Updated

    map_data_copy = json.loads(json.dumps(GEO_DATA_CACHE))
    for feature in map_data_copy.get("features", []):
        props = feature.get("properties", {})
        district_name = str(props.get("DTNAME", "")).strip().lower()
        
        # Check for matches (case insensitive)
        cases = 0
        for area_csv, count in case_counts.items():
            if str(area_csv).strip().lower() == district_name:
                cases = count
                break
        
        props["cases"] = cases
        props["district_display"] = district_name.title()

    return jsonify(map_data_copy)

@app.route('/debug-supabase')
def debug_supabase():
    """Debug Supabase connection and table access"""
    try:
        # Test connection first
        response = supabase.table('govdata').select("count", count="exact").execute()
        print(f"Table count response: {response}")
        
        # Try to get first few rows
        response2 = supabase.table('govdata').select("*").limit(3).execute()
        print(f"Sample data response: {response2}")
            
        return jsonify({
            "connection": "success",
            "count_response": response.data if response else None,  
            "sample_data": response2.data if response2 else None,
            "error": None
        })
        
    except Exception as e:
        print(f"Supabase debug error: {e}")
        return jsonify({
            "connection": "failed", 
            "error": str(e),
            "url": SUPABASE_URL,
            "key_prefix": SUPABASE_KEY[:20] + "..." if SUPABASE_KEY else None
        })

@app.route('/debug-data-validation')
def debug_data_validation():
    """Validate loaded data structure and content"""
    if HEALTH_DATA_CACHE.empty:
        return jsonify({"error": "No data loaded"})
    
    # Check data structure
    validation = {
        "total_rows": len(HEALTH_DATA_CACHE),
        "columns": list(HEALTH_DATA_CACHE.columns),
        "dtypes": HEALTH_DATA_CACHE.dtypes.to_dict(),
        "sample_row": HEALTH_DATA_CACHE.iloc[0].to_dict(),
        "year_range": {
            "min": int(HEALTH_DATA_CACHE['Year'].min()) if 'Year' in HEALTH_DATA_CACHE.columns else None,
            "max": int(HEALTH_DATA_CACHE['Year'].max()) if 'Year' in HEALTH_DATA_CACHE.columns else None,
            "unique_years": sorted(HEALTH_DATA_CACHE['Year'].unique().tolist()) if 'Year' in HEALTH_DATA_CACHE.columns else []
        },
        "case_death_summary": {
            "total_cases": int(pd.to_numeric(HEALTH_DATA_CACHE['No of cases'], errors='coerce').sum()) if 'No of cases' in HEALTH_DATA_CACHE.columns else None,
            "total_deaths": int(pd.to_numeric(HEALTH_DATA_CACHE['No of deaths'], errors='coerce').sum()) if 'No of deaths' in HEALTH_DATA_CACHE.columns else None,
            "max_cases": int(pd.to_numeric(HEALTH_DATA_CACHE['No of cases'], errors='coerce').max()) if 'No of cases' in HEALTH_DATA_CACHE.columns else None,
            "max_deaths": int(pd.to_numeric(HEALTH_DATA_CACHE['No of deaths'], errors='coerce').max()) if 'No of deaths' in HEALTH_DATA_CACHE.columns else None
        }
    }
    
    return jsonify(validation)

@app.route('/debug-tables')
def debug_tables():
    """Check what tables exist in Supabase"""
    try:
        # Alternative method - try some common table names
        common_names = ['govdata', 'health_data', 'csv_import', 'data']
        existing_tables = []
        
        for name in common_names:
            try:
                test_response = supabase.table(name).select("*", count="exact").limit(1).execute()
                existing_tables.append({
                    "table": name,
                    "count": test_response.count,
                    "exists": True
                })
            except:
                existing_tables.append({
                    "table": name, 
                    "exists": False
                })
        
        return jsonify({
            "tables": existing_tables,
            "error": None
        })
        
    except Exception as e:
        return jsonify({
            "tables": [],
            "error": str(e)
        })

@app.route('/debug-map-matching/<int:year>')
def debug_map_matching(year):
    """Debug district name matching for map"""
    if HEALTH_DATA_CACHE.empty:
        return jsonify({"error": "No data"})
    
    # Get health data areas for the year
    year_data = HEALTH_DATA_CACHE[HEALTH_DATA_CACHE["Year"] == year]
    health_areas = year_data["Area"].unique().tolist()
    
    # Get GeoJSON district names
    geojson_districts = []
    if GEO_DATA_CACHE:
        for feature in GEO_DATA_CACHE.get('features', []):
            district_name = feature.get('properties', {}).get('DTNAME', '')
            if district_name:
                geojson_districts.append(district_name)
    
    return jsonify({
        "year": year,
        "health_data_areas": health_areas,
        "geojson_districts": geojson_districts[:10],  # First 10
        "matches_found": len([a for a in health_areas if a.lower() in [d.lower() for d in geojson_districts]]),
        "total_health_areas": len(health_areas),
        "total_geojson_districts": len(geojson_districts)
    })

@app.route('/approve-doctors')
def approve_doctors():
    return render_template('approve_doctors.html')

# --------------------- RUN ---------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
