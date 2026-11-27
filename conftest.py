import os
import subprocess
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
APP_DIR = ROOT / "shop_app"
TEST_DB = ROOT / "test_shop.db"
PORT = 8001
BASE = f"http://127.0.0.1:{PORT}"

# Must be set before importing the app code, and before starting the server,
# so both the tests and the server use the test database.
os.environ["SHOP_DB_PATH"] = str(TEST_DB)
sys.path.insert(0, str(APP_DIR))

from seed import seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def app_server():
    """Start the shop app once for the whole test run, stop it at the end."""
    seed()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(PORT)],
        cwd=APP_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{BASE}/api/products", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    else:
        proc.terminate()
        raise RuntimeError("Shop app did not start within 20 seconds")
    yield
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(autouse=True)
def reset_data():
    """Restore the seed data before every test so tests never affect each other."""
    seed()


@pytest.fixture
def db():
    """Direct SQL access to the test database, for DB validation."""
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()