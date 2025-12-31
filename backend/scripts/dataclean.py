
import pandas as pd

# -----------------------
# File paths (relative to project root)
# -----------------------
file_path = "data/processed/merged_dataset_inner_matches.csv"
output_file = "data/processed/merged_dataset_inner_matches_cleaned.csv"

# -----------------------
# Load dataset
# -----------------------
df = pd.read_csv(file_path)
print("✅ File loaded successfully:", file_path)

# -----------------------
# Step 1: Remove duplicates
# -----------------------
df = df.drop_duplicates()

# -----------------------
# Step 2: Handle missing values
# -----------------------
for col in df.columns:
    if df[col].dtype in ["int64", "float64"]:
        df[col] = df[col].fillna(df[col].median())
    else:
        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")

# -----------------------
# Step 3: Clean text fields
# -----------------------
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].str.strip()

# -----------------------
# Step 4: Convert numeric columns properly
# -----------------------
numeric_cols = ["ratings", "ratings_place", "distance", "ideal_duration", "popularity"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# -----------------------
# Step 5: Automatic Outlier Fixing
# -----------------------
# Ratings → clip to [0, 5]
if "ratings" in df.columns:
    df["ratings"] = df["ratings"].clip(lower=0, upper=5)

if "ratings_place" in df.columns:
    df["ratings_place"] = df["ratings_place"].clip(lower=0, upper=5)

# Distance → replace negatives with 0
if "distance" in df.columns:
    df["distance"] = df["distance"].apply(lambda x: max(x, 0))

# Ideal duration → replace <=0 with median
if "ideal_duration" in df.columns:
    median_duration = df["ideal_duration"].median()
    df["ideal_duration"] = df["ideal_duration"].apply(lambda x: median_duration if x <= 0 else x)

# Popularity → replace negatives with 0
if "popularity" in df.columns:
    df["popularity"] = df["popularity"].apply(lambda x: max(x, 0))

print("✨ Automatic outlier fixing applied!")

# -----------------------
# Step 6: Save cleaned dataset
# -----------------------
df.to_csv(output_file, index=False)
print(f"✅ Cleaned dataset saved as {output_file}")


