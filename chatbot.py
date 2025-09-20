import pandas as pd
import os

def load_and_preprocess_data(filepath):
    """
    Loads and robustly cleans the dataset for chatbot use.
    - Handles file not found errors.
    - Cleans and converts data types for numeric calculations.
    - Creates derived columns like 'Month' and 'Response time'.
    """
    if not os.path.exists(filepath):
        return f"Error: Data file not found at {filepath}"

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return f"Error loading CSV file: {e}"

    # Strip whitespace from column headers
    df.columns = df.columns.str.strip()

    # Convert 'No of cases' and 'No of deaths' to numeric, forcing errors to NaN
    df['No of cases'] = pd.to_numeric(df['No of cases'], errors='coerce')
    df['No of deaths'] = pd.to_numeric(df['No of deaths'], errors='coerce')

    # Drop rows where conversion resulted in NaN for these critical columns
    df.dropna(subset=['No of cases', 'No of deaths'], inplace=True)

    # Convert counts to integers
    df['No of cases'] = df['No of cases'].astype(int)
    df['No of deaths'] = df['No of deaths'].astype(int)

    # Clean and convert date columns
    df['Date of start'] = pd.to_datetime(df['Date of start'], format='%d-%m-%Y', errors='coerce')
    df['Date of reporting'] = pd.to_datetime(df['Date of reporting'], format='%d-%m-%Y', errors='coerce')
    df.dropna(subset=['Date of start', 'Date of reporting'], inplace=True)

    # Create 'Month' and 'Response time' columns
    df['Month'] = df['Date of start'].dt.month_name()
    df['Response time'] = (df['Date of reporting'] - df['Date of start']).dt.days

    # Clean the 'Disease' and 'Area' columns
    df['Disease'] = df['Disease'].str.strip()
    df['Area'] = df['Area'].str.strip()
    
    return df

# --- 1. Disease-Specific Analysis Functions ---

def get_disease_seasonality(df, disease_name):
    """
    Finds the peak season for a given disease by total cases per month.
    """
    disease_df = df[df['Disease'].str.lower() == disease_name.lower()]
    # Define order for months for correct sorting
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    seasonality = disease_df.groupby('Month')['No of cases'].sum().reindex(month_order).fillna(0)
    return seasonality

def get_geographic_hotspots(df, disease_name):
    """
    Identifies the top 5 districts most affected by a disease.
    """
    disease_df = df[df['Disease'].str.lower() == disease_name.lower()]
    hotspots = disease_df.groupby('Area')['No of cases'].sum().sort_values(ascending=False).head(5)
    return hotspots

def get_fatality_rate(df, disease_name):
    """
    Calculates the Case Fatality Rate for a specified disease.
    """
    disease_df = df[df['Disease'].str.lower() == disease_name.lower()]
    total_cases = disease_df['No of cases'].sum()
    total_deaths = disease_df['No of deaths'].sum()
    
    if total_cases == 0:
        return "No cases reported for this disease."
        
    fatality_rate = (total_deaths / total_cases) * 100
    return f"{fatality_rate:.2f}%"

def get_yearly_trends(df, disease_name):
    """
    Shows the year-over-year trend of cases and deaths for a disease.
    """
    disease_df = df[df['Disease'].str.lower() == disease_name.lower()]
    trends = disease_df.groupby('Year').agg(
        total_cases=('No of cases', 'sum'),
        total_deaths=('No of deaths', 'sum')
    ).sort_index()
    return trends

# --- 2. Location-Based Analysis Functions ---

def get_district_profile(df, district_name):
    """
    Provides a health profile for a specific district, showing the top 5 most common diseases.
    """
    district_df = df[df['Area'].str.lower() == district_name.lower()]
    profile = district_df.groupby('Disease')['No of cases'].sum().sort_values(ascending=False).head(5)
    return profile

def get_monthly_risk_for_district(df, district_name, month_name):
    """
    Shows the disease risks (cases and deaths) for a specific district in a given month.
    """
    risk_df = df[(df['Area'].str.lower() == district_name.lower()) & (df['Month'].str.lower() == month_name.lower())]
    risk_summary = risk_df.groupby('Disease').agg(
        total_cases=('No of cases', 'sum'),
        total_deaths=('No of deaths', 'sum')
    ).sort_values(by='total_cases', ascending=False)
    return risk_summary

def compare_districts(df, disease_name, district1, district2):
    """
    Compares the total cases of a disease between two districts.
    """
    comparison_df = df[(df['Disease'].str.lower() == disease_name.lower()) &
                       (df['Area'].str.lower().isin([district1.lower(), district2.lower()]))]
    result = comparison_df.groupby('Area')['No of cases'].sum()
    return result

# --- 3. Time-Based and Trend Analysis Functions ---

def get_recent_outbreaks(df, days=30):
    """
    Summarizes major outbreaks reported in the last N days.
    """
    if 'Date of reporting' not in df.columns:
        return "Date of reporting column not found."
    
    # Use the latest date in the dataset as the reference for 'today'
    latest_date = df['Date of reporting'].max()
    start_date = latest_date - pd.Timedelta(days=days)
    
    recent_df = df[df['Date of reporting'] >= start_date]
    outbreaks = recent_df[['Date of reporting', 'Area', 'Disease', 'No of cases', 'No of deaths']]
    return outbreaks.sort_values(by='Date of reporting', ascending=False)

def get_average_response_time(df, by='disease'):
    """
    Calculates the average time between outbreak start and reporting.
    Can be grouped by 'disease' or 'area'.
    """
    if by.lower() == 'disease':
        return df.groupby('Disease')['Response time'].mean().sort_values(ascending=False)
    elif by.lower() == 'area':
        return df.groupby('Area')['Response time'].mean().sort_values(ascending=False)
    else:
        # Return overall average if no specific grouping is requested
        return df['Response time'].mean()

# --- Main execution block ---
if __name__ == "__main__":
    # Path to the data file within your project structure
    data_path = 'static/data/govdata.csv'
    
    # Load and preprocess the data
    df = load_and_preprocess_data(data_path)

    # Check if the dataframe was loaded correctly before proceeding
    if isinstance(df, pd.DataFrame):
        print("--- Chatbot Insights Engine Ready ---")
        print("Data loaded and preprocessed successfully.\n")

        # --- Example Usage ---
        print("--- Example Insights ---")

        # 1. Disease-Specific
        print("\n[Insight 1: Yearly Trends for Malaria]")
        print(get_yearly_trends(df, "Malaria"))

        print("\n[Insight 2: Seasonality for Dengue (Cases per Month)]")
        print(get_disease_seasonality(df, "Dengue"))

        print("\n[Insight 3: Geographic Hotspots for Cholera]")
        print(get_geographic_hotspots(df, "Cholera"))

        print(f"\n[Insight 4: Fatality Rate for Leptospirosis]")
        print(get_fatality_rate(df, "Leptospirosis"))

        # 2. Location-Based
        print("\n[Insight 5: Health Profile for Pune District]")
        print(get_district_profile(df, "Pune"))
        
        print("\n[Insight 6: Disease Risk in Kolhapur during August]")
        print(get_monthly_risk_for_district(df, "Kolhapur", "August"))

        print("\n[Insight 7: Comparing Dengue cases in Nagpur vs. Pune]")
        print(compare_districts(df, "Dengue", "Nagpur", "Pune"))
        
        # 3. Time-Based
        print("\n[Insight 8: Average Response Time by Disease (Top 5 Slowest)]")
        print(get_average_response_time(df, by='disease').head())

        print("\n[Insight 9: Recent Outbreaks (in the last 30 days of data)]")
        print(get_recent_outbreaks(df, days=30))

    else:
        # Print the error message if data loading failed
        print(df)
