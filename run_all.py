from pathlib import Path
import subprocess
import sys
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

def run(cmd):
    log.info(f"Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, shell=False)
    if r.returncode != 0:
        log.error(f"Command failed: {' '.join(cmd)}")
        log.error(f"Exit code: {r.returncode}")
        sys.exit(r.returncode)
    log.info("Completed successfully")

log.info("Starting pipeline")

log.info("Step 1/3: Downloading data")
run([sys.executable, "scripts/download_data.py"])

log.info("Step 2/3: Building dataset")
run([sys.executable, "scripts/build_dataset.py"])

log.info("Step 3/3: Launching Streamlit app")
if os.environ.get("DOCKER_CONTAINER") == "true":
    log.info("Running in Docker mode")
    run([
        "streamlit", "run", "app/streamlit_app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501",
        "--server.headless=true",
    ])
else:
    log.info("Running in local mode")
    run(["streamlit", "run", "app/streamlit_app.py"])