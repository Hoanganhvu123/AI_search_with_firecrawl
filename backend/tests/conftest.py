"""
conftest.py — Shared test configuration.

Tất cả test files nên import BASE_URL từ đây thay vì hardcode.
"""

import os

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:5000")
