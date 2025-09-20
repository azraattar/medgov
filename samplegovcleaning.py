import pandas as pd

# Load file
df = pd.read_csv("finalgov.csv")

# Drop completely empty columns (all NaN)
df = df.dropna(axis=1, how="all")

# Drop useless "Unnamed" columns (they’re usually index leftovers)
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

df["No of cases"] = pd.to_numeric(df["No of cases"], errors="coerce").astype("Int64")
df["No of deaths"] = pd.to_numeric(df["No of deaths"], errors="coerce").astype("Int64")

# Convert dates
df["Date of start"] = pd.to_datetime(df["Date of start"], errors="coerce")
df["Date of reporting"] = pd.to_datetime(df["Date of reporting"], errors="coerce")


print("Cleaned columns:", df.columns.tolist())
# Datatypes
print("\nData Types:")
print(df.dtypes)

# Nulls
print("\nMissing Values per Column:")
print(df.isnull().sum())

# Duplicates
print("\nDuplicate Rows Count:", df.duplicated().sum())

# Numeric summary
print("\nSummary Statistics:")
print(df.describe())

# Categorical unique counts
print("\nUnique Values per Column:")
for col in df.select_dtypes(include=["object"]).columns:
    print(f"{col}: {df[col].nunique()} unique values")

# Replace null values with defaults
df["State"] = df["State"].fillna("Maharashtra")
df["Area"] = df["Area"].fillna("Mumbai")
df["Disease"] = df["Disease"].fillna("Food Poisoning")

# Quick check if nulls remain in those columns
print(df[["State", "Area", "Disease"]].isnull().sum())

# Convert "No of cases" to numeric (if not already)
df["No of cases"] = pd.to_numeric(df["No of cases"], errors="coerce")

# Calculate absolute averages


# Fill nulls with averages


# Convert to numeric just in case

# Calculate averages and round
avg_cases = round(abs(df["No of cases"].mean()))
avg_deaths = round(abs(df["No of deaths"].mean()))

# Fill missing values
df["No of cases"] = df["No of cases"].fillna(avg_cases).astype("Int64")
df["No of deaths"] = df["No of deaths"].fillna(avg_deaths).astype("Int64")

# Quick check
print(df[["No of cases", "No of deaths"]].isnull().sum())
print(df[["No of cases", "No of deaths"]].head())
print("\nMissing Values per Column:")
print(df.isnull().sum())
# Rows where Date of start is null
null_start_rows = df[df["Date of start"].isnull()].index.tolist()
print("Rows with null Date of start:", null_start_rows)

# Rows where Date of reporting is null
null_reporting_rows = df[df["Date of reporting"].isnull()].index.tolist()
print("Rows with null Date of reporting:", null_reporting_rows)

# Rows where BOTH are null
null_both_rows = df[df["Date of start"].isnull() & df["Date of reporting"].isnull()].index.tolist()
print("Rows with BOTH null:", null_both_rows)

# Save changes back to the original CSV
df.to_csv("finalgov1.csv", index=False)
print("✅ Changes saved to your_file.csv")
