import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def get_test_file(download_file, destination_dir="."):
    """
    Download one or more test files from GitHib resources.

    Parameters
    ----------
    download_file : str or list[str]
        One or more test file names to download from GitHib resources.
    destination_dir : path-like, optional
        Location to save downloaded files.

    """
    os.makedirs(destination_dir, exist_ok=True)
    resource_urls = [
        "https://media.githubusercontent.com/media/wsp-sag/client_sandag_rsm_resources/main/",
        "https://raw.githubusercontent.com/wsp-sag/client_sandag_rsm_resources/main/",
        "https://media.githubusercontent.com/media/camsys/client_sandag_rsm_resources/main/",
        "https://raw.githubusercontent.com/camsys/client_sandag_rsm_resources/main/",
    ]
    if isinstance(download_file, (str, Path)):
        if os.path.exists(os.path.join(destination_dir, download_file)):
            logger.warning(f"file {download_file!r} already exists")
            return
        for resource_url in resource_urls:
            r = requests.get((resource_url + download_file), allow_redirects=True)
            if r.ok:
                open(os.path.join(destination_dir, download_file), "wb").write(
                    r.content
                )
                break
        else:
            raise FileNotFoundError(download_file)
    else:
        for f in download_file:
            get_test_file(f, destination_dir)
