"""Download the public CDISC Pilot Study ADaM datasets used by TRACE examples."""

import shutil
from http.client import IncompleteRead
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE_URL = (
    "https://raw.githubusercontent.com/cdisc-org/sdtm-adam-pilot-project/master/"
    "updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/"
    "analysis/adam/datasets"
)
DATA_DIR = Path("data")
DATASETS = ("adsl.xpt", "adae.xpt")
DOWNLOAD_TIMEOUT_SECONDS = 30
DOWNLOAD_ATTEMPTS = 3

DATA_DIR.mkdir(exist_ok=True)


def download(source: str, destination: Path) -> None:
    request = Request(source, headers={"User-Agent": "trace-tlf-example-fetcher"})

    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        temporary_path: Path | None = None
        try:
            with urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                with NamedTemporaryFile(
                    dir=destination.parent,
                    prefix=f".{destination.name}.",
                    delete=False,
                ) as temporary_file:
                    temporary_path = Path(temporary_file.name)
                    shutil.copyfileobj(response, temporary_file)
            temporary_path.replace(destination)
            return
        except (IncompleteRead, OSError, URLError) as error:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            if attempt == DOWNLOAD_ATTEMPTS:
                raise RuntimeError(
                    f"could not download {source} after {DOWNLOAD_ATTEMPTS} attempts"
                ) from error
            delay = 2 ** (attempt - 1)
            print(f"download failed ({error}); retrying in {delay}s")
            sleep(delay)


for dataset in DATASETS:
    destination = DATA_DIR / dataset
    if destination.exists():
        print(f"exists: {destination}")
        continue

    source = f"{BASE_URL}/{dataset}"
    print(f"downloading: {source}")
    download(source, destination)
    print(f"saved: {destination}")
