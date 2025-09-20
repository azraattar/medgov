import json
import os

# This builds the path exactly like your app.py does.
# It assumes this script is in the same folder as app.py.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.join(APP_ROOT, 'static', 'data', 'maharashtradist.geojson')

print("--- GeoJSON File Diagnostic ---")
print(f"Attempting to access file at this exact path: \n{geojson_path}\n")

# Step 1: Check if the file exists at the path.
if not os.path.exists(geojson_path):
    print("❌ DIAGNOSIS: File Not Found")
    print("Python cannot find the file at the path above. Please check for typos in the path, filename, or extension. Ensure there are no hidden spaces.")
else:
    print("✅ DIAGNOSIS: File was found at the path.")
    
    # Step 2: Try to open and read the file's content.
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            # First, check if the file is empty.
            if os.path.getsize(geojson_path) == 0:
                print("❌ DIAGNOSIS: The file is empty and contains no data.")
            else:
                # If not empty, try to decode it.
                json.load(f)
                print("✅ SUCCESS: The file is valid GeoJSON and can be loaded successfully!")

    except json.JSONDecodeError as e:
        print("❌ DIAGNOSIS: The file is invalid and cannot be decoded.")
        print(f"   Error Details: {e}")
        print("   This is a syntax error inside the file. Please validate its content at a site like jsonlint.com.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

print("\n--- End of Diagnostic ---")
