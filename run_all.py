from pathlib import Path
import subprocess, sys

def run(cmd):
    print("Running:", cmd)
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


run("python scripts/download_data.py")
run("python scripts/build_dataset.py")
run("streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=8501")