import duckdb
from pathlib import Path

from config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "warehouse.duckdb")


def get_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(DB_PATH)

    # httpfs Extension laden (ermöglicht S3-kompatiblen Zugriff)
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")

    # MinIO Zugangsdaten setzen (S3-kompatibel)
    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    con.execute(f"SET s3_endpoint='{endpoint}';")
    con.execute(f"SET s3_access_key_id='{MINIO_ACCESS_KEY}';")
    con.execute(f"SET s3_secret_access_key='{MINIO_SECRET_KEY}';")
    con.execute("SET s3_use_ssl=false;")       # MinIO läuft lokal ohne SSL
    con.execute("SET s3_url_style='path';")    # wichtig für MinIO (nicht virtual-hosted-style)

    return con


def create_raw_table(con: duckdb.DuckDBPyConnection):
    # Alle JSON-Snapshots aus MinIO in eine raw-Tabelle einlesen
    s3_path = f"s3://{MINIO_BUCKET}/raw/opensky/*/*.json"

    con.execute(f"""
        CREATE OR REPLACE TABLE raw_opensky AS
        SELECT *, filename AS source_file
        FROM read_json_auto('{s3_path}', filename=true, union_by_name=true)
    """)

    count = con.execute("SELECT COUNT(*) FROM raw_opensky").fetchone()[0]
    print(f"[duckdb] raw_opensky Tabelle erstellt mit {count} Snapshot-Zeilen")


if __name__ == "__main__":
    con = get_connection()
    create_raw_table(con)

    # Kurzer Check
    print(con.execute("SELECT time, source_file FROM raw_opensky").fetchdf())
    con.close()