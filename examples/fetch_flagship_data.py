"""Download the public ADaM parquet files used by TRACE flagship examples."""

from pathlib import Path
from urllib.request import urlretrieve

BASE_URL = "https://raw.githubusercontent.com/elong0527/demo-py-esub/main/data"
DATA_DIR = Path("data")
DATASETS = ("adsl.parquet", "adae.parquet", "adtte.parquet")

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
