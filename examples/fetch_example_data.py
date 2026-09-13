"""Download the public CDISC Pilot Study ADaM datasets used by TRACE examples."""

from pathlib import Path
from urllib.request import urlretrieve

BASE_URL = (
    "https://raw.githubusercontent.com/cdisc-org/sdtm-adam-pilot-project/master/"
    "updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/"
    "analysis/adam/datasets"
)
DATA_DIR = Path("data")
DATASETS = ("adsl.xpt", "adae.xpt", "adtte.xpt")

DATA_DIR.mkdir(exist_ok=True)

for dataset in DATASETS:
    destination = DATA_DIR / dataset
    if destination.exists():
        print(f"exists: {destination}")
        continue

    source = f"{BASE_URL}/{dataset}"
    print(f"downloading: {source}")
    urlretrieve(source, destination)
    print(f"saved: {destination}")
