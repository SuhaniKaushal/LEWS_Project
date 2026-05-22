import os
import sys
import urllib.request
import zipfile
import subprocess
import time

# Configuration
PG_VERSION = "16.2-1"
URL = f"https://get.enterprisedb.com/postgresql/postgresql-{PG_VERSION}-windows-x64-binaries.zip"
BASE_DIR = r"d:\PROJECTS\LEWS_Project-master"
TEMP_DIR = os.path.join(BASE_DIR, "temp_pg")
ZIP_PATH = os.path.join(TEMP_DIR, "pg.zip")
PGSQL_DIR = os.path.join(TEMP_DIR, "pgsql")
DATA_DIR = os.path.join(TEMP_DIR, "data")
SQL_FILE = os.path.join(BASE_DIR, "LEWS_Project-master", "01022021_website", "user_entry", "backup_10012026.sql")

def log(msg):
    print(f"[*] {msg}", flush=True)

def main():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        log(f"Created temp directory: {TEMP_DIR}")

    # Step 1: Download PostgreSQL Zip
    if not os.path.exists(ZIP_PATH) and not os.path.exists(PGSQL_DIR):
        log(f"Downloading PostgreSQL {PG_VERSION}...")
        try:
            urllib.request.urlretrieve(URL, ZIP_PATH)
            log("Download completed successfully!")
        except Exception as e:
            log(f"Failed to download PostgreSQL zip: {e}")
            sys.exit(1)

    # Step 2: Unzip
    if not os.path.exists(PGSQL_DIR):
        log("Extracting PostgreSQL binaries...")
        try:
            with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)
            log("Extraction completed!")
            # Clean up zip
            try:
                os.remove(ZIP_PATH)
            except Exception:
                pass
        except Exception as e:
            log(f"Failed to extract zip: {e}")
            sys.exit(1)

    # Step 3: Initialize Database Cluster
    bin_dir = os.path.join(PGSQL_DIR, "bin")
    initdb_path = os.path.join(bin_dir, "initdb.exe")
    pg_ctl_path = os.path.join(bin_dir, "pg_ctl.exe")
    createdb_path = os.path.join(bin_dir, "createdb.exe")
    psql_path = os.path.join(bin_dir, "psql.exe")

    if not os.path.exists(DATA_DIR):
        log("Initializing database cluster...")
        # run initdb
        cmd = [initdb_path, "-D", DATA_DIR, "-U", "postgres", "--auth=trust"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            log(f"Failed to initdb: {res.stderr}")
            sys.exit(1)
        log("Database initialized successfully!")

    # Step 4: Start PostgreSQL Server
    log("Starting PostgreSQL server on port 5432...")
    # Check if port 5432 is already in use
    # We use pg_ctl to start
    cmd = [pg_ctl_path, "-D", DATA_DIR, "-l", os.path.join(TEMP_DIR, "pg.log"), "start"]
    # Run in background
    subprocess.Popen(cmd)
    
    # Wait for startup
    time.sleep(5)
    log("Server started!")

    # Step 5: Create Database
    log("Creating netala_database...")
    cmd = [createdb_path, "-U", "postgres", "-h", "127.0.0.1", "-p", "5432", "netala_database"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        log("netala_database created successfully!")
    else:
        log(f"createdb info (might already exist): {res.stderr.strip()}")

    # Step 6: Restore SQL Dump
    if os.path.exists(SQL_FILE):
        log(f"Restoring database from {SQL_FILE}...")
        # run psql
        cmd = [psql_path, "-U", "postgres", "-h", "127.0.0.1", "-p", "5432", "-d", "netala_database", "-f", SQL_FILE]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            log("Database restored successfully!")
        else:
            log(f"Warning/Info during restore: {res.stderr.strip()[:500]}")
    else:
        log(f"SQL file not found at {SQL_FILE}!")

    # Step 7: Insert custom mock nodes n9, n0 for Kerala (to display them on selection UI)
    log("Inserting custom nodes n0 and n9...")
    insert_queries = [
        "INSERT INTO node (name, location, node_id, remark, tenant_id) VALUES ('n9', 'kerela', 'kerela_n9', 'This is kerela site 9', 2) ON CONFLICT (node_id) DO NOTHING;",
        "INSERT INTO node (name, location, node_id, remark, tenant_id) VALUES ('n0', 'kerela', 'kerela_n0', 'This is kerela site 0', 2) ON CONFLICT (node_id) DO NOTHING;",
        "INSERT INTO sensor_info (sensor_id, sensor_type, node_id, depth, remark, tenant_id) VALUES ('kerela_n9_ms1', 'moisture', 'kerela_n9', 0.5, 'BH9_Moisture', 2) ON CONFLICT (sensor_id) DO NOTHING;",
        "INSERT INTO sensor_info (sensor_id, sensor_type, node_id, depth, remark, tenant_id) VALUES ('kerela_n0_ms1', 'moisture', 'kerela_n0', 0.5, 'BH0_Moisture', 2) ON CONFLICT (sensor_id) DO NOTHING;"
    ]
    for q in insert_queries:
        cmd = [psql_path, "-U", "postgres", "-h", "127.0.0.1", "-p", "5432", "-d", "netala_database", "-c", q]
        subprocess.run(cmd, capture_output=True)
    log("Completed! Database setup and initialization successful.")

if __name__ == "__main__":
    main()
