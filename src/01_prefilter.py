"""
Passes a list of MeSH terms to the EDirect bash script.
"""

import subprocess
import sys
from pathlib import Path

# Path to your bash script
SCRIPT_PATH = Path(__file__).parent / "01_query.sh"

def fetch_pubmed_mesh(terms):
    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Bash script not found: {SCRIPT_PATH}")

    if not isinstance(terms, (list, tuple)):
        raise ValueError("`terms` must be a list or tuple of MeSH terms")

    cmd = [str(SCRIPT_PATH)] + terms
    print(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing fetch script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    
    with open("mesh_terms.txt") as f:
        mesh_terms = [line.strip() for line in f if line.strip()]

    fetch_pubmed_mesh(mesh_terms)

