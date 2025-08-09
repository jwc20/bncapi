#!/usr/bin/env python3
"""
https://stackoverflow.com/questions/75741942/prevent-render-com-server-from-sleeping
"""
import os
import sys
import time

import requests
import schedule
from dotenv import load_dotenv


def ping_endpoint(url: str, timeout: int = 10):
    try:
        response = requests.get(url, timeout=timeout)
        print(f"{url} - Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"✗ {url} - Error: {e}")


def main() -> int:
    load_dotenv()
    url = os.getenv("PING_ENDPOINT")
    ping_endpoint(url)


if __name__ == "__main__":
    sys.exit(main())
