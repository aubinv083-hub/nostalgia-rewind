from pathlib import Path
import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

def run(cmd):
    log.info(f"Running: {cmd}")
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        log.error(f"Command failed: {cmd}")
        log.error(f"Exit code: {r.returncode}")
        sys.exit(r.returncode)
    log.info("Completed successfully")

log.info("Starting pipeline")

log.info("Step 1/3: Downloading data")
run("python scripts/download_data.py")

log.info("Step 2/3: Building dataset")
run("python scripts/build_dataset.py")

log.info("Step 3/3: Launching Streamlit app")
run("streamlit run app/streamlit_app.py")
