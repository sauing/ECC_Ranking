import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
from .config import CHROME_PATH, HEADLESS

def verify_executable(path: str) -> bool:
    try:
        if not os.path.isfile(path):
            return False
        completed = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
        return completed.returncode == 0 and 'ChromeDriver' in (completed.stdout + completed.stderr)
    except Exception:
        return False

def prepare_service():
    candidates = [CHROME_PATH, CHROME_PATH + '.exe']
    if os.path.isdir(CHROME_PATH):
        candidates.append(os.path.join(CHROME_PATH, 'chromedriver.exe'))
        candidates.append(os.path.join(CHROME_PATH, 'chromedriver'))
    downloads_variant = os.path.join(os.path.dirname(CHROME_PATH), 'chromedriver.exe')
    candidates.append(downloads_variant)
    for c in candidates:
        if verify_executable(c):
            return Service(c)
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        if verify_executable(driver_path):
            return Service(driver_path)
    except Exception:
        pass
    raise RuntimeError(
        "Could not find a valid chromedriver executable.\n"
        "Make sure CHROME_PATH points to chromedriver.exe, or install webdriver-manager (pip install webdriver-manager).\n"
        "You can manually download the correct chromedriver for your Chrome version: https://chromedriver.chromium.org/downloads"
    )

def get_driver():
    options = Options()
    if HEADLESS:
        options.add_argument('--headless')
    service = prepare_service()
    try:
        return webdriver.Chrome(service=service, options=options)
    except OSError as e:
        if getattr(e, 'winerror', None) == 193:
            raise RuntimeError(
                f"WinError 193: The file at {service.path} is not a valid Win32 executable.\n"
                "Verify the chromedriver is a Windows .exe built for your architecture."
            ) from e
        raise

