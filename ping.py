#!/usr/bin/env python3
"""
https://stackoverflow.com/questions/75741942/prevent-render-com-server-from-sleeping
- render server will sleep after 15 minutes of inactivity
- render has a 750-hour limit per month, which is about 31 days
"""
import sys
import time

import requests
import schedule


def ping_endpoint(url: str, timeout: int = 10):
    try:
        response = requests.get(url, timeout=timeout)
        print(f"{url} - Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"✗ {url} - Error: {e}")


def main() -> int:
    url = "https://bncapi.onrender.com/api/ping"
    ping_endpoint(url)


if __name__ == "__main__":
    sys.exit(main())
