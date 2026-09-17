from __future__ import annotations

import json
from urllib.request import urlopen

ENDPOINTS = [
    (
        "API liveness",
        "http://localhost:8000/api/v1/health/live",
    ),
]


def main() -> None:
    for name, url in ENDPOINTS:
        with urlopen(
            url,
            timeout=5,
        ) as response:
            payload = json.loads(response.read())

            if response.status != 200:
                raise RuntimeError(f"{name} failed.")

            print(f"[ok] {name}: {payload}")


if __name__ == "__main__":
    main()
