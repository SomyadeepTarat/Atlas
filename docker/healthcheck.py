from __future__ import annotations

import json
import sys
from urllib.error import URLError
from urllib.request import urlopen

URL = "http://127.0.0.1:8000/api/v1/health/live"


def main() -> int:
    try:
        with urlopen(
            URL,
            timeout=2,
        ) as response:
            if response.status != 200:
                return 1

            payload = json.loads(response.read())

    except (
        URLError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return 1

    if payload.get("status") != "ok":
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
