import os
from pathlib import Path

import requests


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
    resource_urls = [
        "https://media.githubusercontent.com/media/wsp-sag/client_sandag_rsm_resources/main/",
        "https://raw.githubusercontent.com/wsp-sag/client_sandag_rsm_resources/main/",
        "https://media.githubusercontent.com/media/camsys/client_sandag_rsm_resources/main/",
        "https://raw.githubusercontent.com/camsys/client_sandag_rsm_resources/main/",
    ]
    if isinstance(download_file, (str, Path)):
        while True:
            for resource_url in resource_urls:
                r = requests.get((resource_url + download_file), allow_redirects=True)
                open(os.path.join(destination_dir + download_file), "wb").write(
                    r.content
                )
    else:
        for f in download_file:
            get_test_file(f, destination_dir)
