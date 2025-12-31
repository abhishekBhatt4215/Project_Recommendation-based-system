import pandas as pd

# Load your cleaned CSV file
csv_file = "merged_dataset_inner_matches_cleaned.csv"

# Output JSON file name
json_file = "merged_dataset_inner_matches_cleaned.json"

# Read CSV
df = pd.read_csv(csv_file)

# Convert to JSON (records format is BEST for backend + RAG)
df.to_json(json_file, orient="records", indent=4)

print("✅ CSV successfully converted to JSON!")
print("📁 Saved as:", json_file)
print("📊 Total records:", len(df))
