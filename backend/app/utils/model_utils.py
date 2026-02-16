import requests
from pathlib import Path

def download_file(url: str, dest: str):
    dest_p = Path(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_p, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return str(dest_p)
