import os, subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def verify_executable(path: str) -> bool:
    try:
        if not os.path.isfile(path):
            return False
        c = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
        return c.returncode == 0 and 'ChromeDriver' in (c.stdout + c.stderr)
    except Exception:
        return False

def prepare_service(chrome_path: str | None) -> Service:
    candidates = []
    if chrome_path:
        candidates += [chrome_path, chrome_path + '.exe']
        if os.path.isdir(chrome_path):
            candidates += [os.path.join(chrome_path, 'chromedriver.exe'),
                           os.path.join(chrome_path, 'chromedriver')]
        candidates.append(os.path.join(os.path.dirname(chrome_path), 'chromedriver.exe'))

    for c in candidates:
        if verify_executable(c):
            return Service(c)

    # Fallback: webdriver-manager
    from webdriver_manager.chrome import ChromeDriverManager
    driver_path = ChromeDriverManager().install()
    if verify_executable(driver_path):
        return Service(driver_path)
    raise RuntimeError("Could not prepare ChromeDriver")

def build_options(headless: bool = True, window_size: str = "1920,1080") -> Options:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={window_size}")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--log-level=2")
    return opts

def get_driver(chrome_path: str | None, headless: bool, window_size: str) -> webdriver.Chrome:
    svc = prepare_service(chrome_path)
    opts = build_options(headless=headless, window_size=window_size)
    return webdriver.Chrome(service=svc, options=opts)
