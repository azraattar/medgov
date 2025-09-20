import pandas as pd
import os

def load_and_clean_data(filepath):
    """
    Loads and cleans the health data from the CSV file.
    This function ensures data types are correct for calculations.
    """
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        
        # Convert necessary columns to numeric, handling potential errors
        for col in ['Year', 'No of cases', 'No of deaths']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows where conversion failed
        df.dropna(subset=['Year', 'No of cases', 'No of deaths'], inplace=True)
        
        # Convert to integers for clean output
        for col in ['Year', 'No of cases', 'No of deaths']:
            df[col] = df[col].astype(int)
            
        # Clean string columns
        df['Disease'] = df['Disease'].str.strip()
        df['Area'] = df['Area'].str.strip()
        
        return df
    except FileNotFoundError:
        print(f"Error: The file was not found at {filepath}")
        return None

def generate_text_insights(df):
    """
    Generates a list of plain-text sentences from the DataFrame.
    Each sentence is a self-contained piece of knowledge.
    """
    if df is None:
        return []

    insights = []

    # Insight Type 1: Yearly Trends for Each Disease
    for (disease, year), group in df.groupby(['Disease', 'Year']):
        total_cases = group['No of cases'].sum()
        total_deaths = group['No of deaths'].sum()
        text = f"For the year {year}, the disease {disease} had {total_cases} reported cases and {total_deaths} deaths in Maharashtra."
        insights.append(text)

    # Insight Type 2: District Health Profiles for Each Year
    for (area, year), group in df.groupby(['Area', 'Year']):
        # Find the top 3 most common diseases for that district and year
        top_diseases = group.groupby('Disease')['No of cases'].sum().nlargest(3)
        if not top_diseases.empty:
            disease_list = ", ".join([f"{name} ({count} cases)" for name, count in top_diseases.items()])
            text = f"In the district of {area} during the year {year}, the most common diseases included: {disease_list}."
            insights.append(text)

    # Insight Type 3: Overall Fatality Rates for Each Disease
    for disease, group in df.groupby('Disease'):
        total_cases = group['No of cases'].sum()
        total_deaths = group['No of deaths'].sum()
        if total_cases > 0 and total_deaths > 0:
            fatality_rate = (total_deaths / total_cases) * 100
            text = f"The overall case fatality rate for {disease} is {fatality_rate:.2f}%, based on {total_cases} cases and {total_deaths} deaths."
            insights.append(text)
            
    return insights

def save_insights_to_file(insights, output_filepath):
    """
    Saves the list of insights to a text file, with each insight on a new line.
    """
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            for insight in insights:
                f.write(insight + '\n')
        print(f"✅ Successfully saved {len(insights)} insights to {output_filepath}")
    except IOError as e:
        print(f"Error: Could not write to file {output_filepath}. Reason: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # Define file paths relative to the current script
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    csv_input_path = os.path.join(APP_ROOT, 'static', 'data', 'govdata.csv')
    text_output_path = os.path.join(APP_ROOT, 'knowledge_base.txt')

    # 1. Load the data
    health_df = load_and_clean_data(csv_input_path)

    # 2. Generate the text insights
    if health_df is not None:
        text_insights = generate_text_insights(health_df)

        # 3. Save the insights to a file
        save_insights_to_file(text_insights, text_output_path)

