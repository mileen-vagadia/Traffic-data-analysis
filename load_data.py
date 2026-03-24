import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "traffic_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
CSV_PATH = "data/raw/traffic_data.csv"

# mapping csv columns to postgres column names
COLUMN_MAP = {
    "timestamp"            : "timestamp",
    "location_id"          : "intersection_id",
    "traffic_volume"       : "traffic_volume",
    "avg_vehicle_speed"    : "avg_speed",
    "vehicle_count_cars"   : "count_cars",
    "vehicle_count_trucks" : "count_trucks",
    "vehicle_count_bikes"  : "count_bikes",
    "weather_condition"    : "weather_condition",
    "temperature"          : "temperature",
    "humidity"             : "humidity",
    "accident_reported"    : "accident_reported",
    "signal_status"        : "signal_phase",
}


def load_csv(path):
    print(f"reading {path}...")
    df = pd.read_csv(path)
    print(f"shape: {df.shape}")
    return df


def clean(df):
    df = df.rename(columns=COLUMN_MAP)

    cols = [c for c in COLUMN_MAP.values() if c in df.columns]
    df = df[cols]

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["timestamp", "traffic_volume"])
    dropped = before - len(df)
    if dropped:
        print(f"dropped {dropped} rows with nulls")

    for col in ["weather_condition", "signal_phase"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower()

    print(f"clean rows: {len(df)}")
    return df


def insert(df, engine):
    print("inserting into postgres...")
    df.to_sql(
        "traffic_observations",
        engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )
    print(f"done — {len(df)} rows inserted")


def main():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("connected to postgres")

    df = load_csv(CSV_PATH)
    df = clean(df)
    insert(df, engine)


if __name__ == "__main__":
    main()
