import json
import logging
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import chromedriver_autoinstaller

load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = "screenshots"
DATA_FILE = "test_runs.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
APP_PORT = os.getenv("APP_PORT")
TEST_URL = "https://www.reddit.com"



# Create screenshot directory if it doesn't exist
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# Initialize Flask app
app = Flask(__name__, static_folder=SCREENSHOT_DIR)
CORS(app)

# In-memory cache of test runs (will be saved to file)
test_runs = []

# Load existing test runs from file if it exists
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as file:
            test_runs = json.load(file)
    except Exception as e:
        logger.error(f"Error loading test runs data: {e}")

def save_test_runs():
    """Save test runs to JSON file"""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(test_runs, file)
    except Exception as e:
        logger.error(f"Error saving test runs data: {e}")

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(service=ChromiumService())

# API Routes
@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "hi"})

@app.route("/api/test/runs", methods=["GET"])
def get_test_runs():
    return jsonify(test_runs)

# API Routes
@app.route("/api/test/run", methods=["GET"])
def run_tests():
    return run_test()

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({"status": "ok"})

@app.route("/screenshots/<path:filename>")
def get_screenshot(filename):
    return send_from_directory(SCREENSHOT_DIR, filename)

def run_test():
    run_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    screenshot_path = f"/{SCREENSHOT_DIR}/{run_id}.png"
    local_screenshot_path = f".{screenshot_path}"

    driver.get("http://reddit.com")
    driver.save_screenshot(local_screenshot_path)
    assert "Reddit" in driver.title
    return "OK"

if __name__ == "__main__":
    logger.info("Starting Selenium Monitor service")
    app.run(debug=True, host="0.0.0.0", port=APP_PORT)