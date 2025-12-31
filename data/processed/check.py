import pandas as pd

# Load your specific CSV file
df = pd.read_csv("merged_dataset_inner_matches_cleaned.csv")

# 1. Check missing values
print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

# 2. Check duplicate rows
print("\n--- DUPLICATE ROWS ---")
print("Duplicate rows:", df.duplicated().sum())

# 3. Check column data types
print("\n--- DATA TYPES ---")
print(df.dtypes)

# 4. Check ratings range
if "ratings" in df.columns:
    print("\n--- RATINGS SUMMARY ---")
    print(df["ratings"].describe())

if "ratings_place" in df.columns:
    print("\n--- RATINGS PLACE SUMMARY ---")
    print(df["ratings_place"].describe())
