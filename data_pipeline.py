import csv
from pathlib import Path
import pandas as pd
import sys
import hashlib

BASE = Path(__file__).resolve().parent
# !!!fix COLS to reference actual columns!!!
COLS = ["time", "name", "type", "status", "location_id", "description", "geo_point", "primary_key", "description_of_behavior", "image", "ranger_id", "ranger_notes", "direction_of_travel", "description_of_area", "threat_level"]

# Define paths (use relative paths so script runs regardless of user home differences)
CSV_REL = BASE / "data"/"raw"/"raw"/"animal_sightings.csv"
OUT_REL = BASE / "data"/"clean"/"animal_sightings_clean.csv"

# Check code is formatted correctly
def new_sighting():
    f = open(OUT_REL, "x", "b", "t")
    time = time # input() if time does not work
    name = input()
    type = input()
    status = "active"
    location_id = # Hash of geoshape the geopoint falls in
    description = input()
    geo_point = # geo point input
    primary_key = 'primary_key'
    description_of_behavior = input()
    image = # image input
    ranger_id = # current_user.apply(lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest())    # How to get current user?
    ranger_notes = input()
    direction_of_travel = # Option menu
    description_of_area = # Surrounding Area Description LLM output
    threat_level = # Threat Level LLM output
    f.write[time, name, type, status, location_id, description, geo_point, primary_key, description_of_behavior, image, ranger_id, ranger_notes, direction_of_travel, description_of_area, threat_level]
    f.close()

def detect_delimiter(path: Path, sample_size: int = 8192) -> str:
    with path.open("r", encoding="utf-8", newline="") as f:
        sample = f.read(sample_size)
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter
    except Exception:
        return ","

def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")

    sep = detect_delimiter(path)
    df = pd.read_csv(
        path,
        sep=sep,
        encoding="utf-8",
        skipinitialspace=True,
        parse_dates=["time"] if "time" in pd.read_csv(path, nrows=0).columns else [],
        infer_datetime_format=True,
        low_memory=False,
    )
    # Drop columns with names like 'Unnamed: 0'
    df =df.loc[:, ~df.columns.str.match(r'^Unnamed')]

    # ensure numeric coordinates (only convert if column exists)
    if "longitude" in df.columns:
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    if "latitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    if "elevation_in_meters" in df.columns:
        df["elevation_in_meters"] = pd.to_numeric(df["elevation_in_meters"], errors="coerce")
    else:
        df["elevation_in_meters"] = pd.Series([pd.NA] * len(df), dtype="Float64")
    return df

def write_clean_data(df: pd.DataFrame, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Wrote cleaned CSV to {out_path} (rows={len(df)})")

def main(input_path: Path = CSV_REL, output_path: Path = OUT_REL):
    try:
        df = load_data(input_path)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("Error reading CSV:", e, file=sys.stderr)
        sys.exit(2)

    # Concatenate latitude and longitude and create a geo point
    df['geo_point'] = df['longitude'].fillna('').astype(str).str.cat(
                     df['latitude'].fillna('').astype(str),
                     sep=',', na_rep=''
    )
    # Drop columns
    cols_to_drop = ["elevation_in_meters", "sym", "latitude", "longitude"] #adjust as needed
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")

    # Create primary key
    df['primary_key'] = df['time'].astype(str) + df['geo_point'].astype(str)
    df['primary_key'] = df['primary_key'].apply(lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest())
    
    # Add columns
    df["description_of_behavior"].astype(str)
    df["image"].astype(str)
    df["ranger_id"].astype(str)
    df["ranger_notes"].astype(str)
    df["direction_of_travel"].astype(str)

    # LLM for searching area around sighting geo_point for surrounding area description
    # input code here

    # Add colunmn for area description summary
    df["area_description"] = # Surrounding area LLM output

    # LLM for threat level analysis
    # input code here

    # Add threat_level column
    df["threat_level"] = # Threat level LLM output



    # Done: write result
    write_clean_data(df, output_path)

if __name__ == "__main__":
    main()