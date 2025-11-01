import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_news_agent():
    """Run the news agent"""
    logging.info("Starting scheduled news agent run...")
    try:
        result = subprocess.run(
            ['python', 'main.py'],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        if result.returncode == 0:
            logging.info("News agent completed successfully!")
        else:
            logging.error(f"News agent failed with error: {result.stderr}")
    except Exception as e:
        logging.error(f"Error running news agent: {e}")

# Schedule the job
schedule.every().day.at("08:00").do(run_news_agent)  # Run at 8 AM daily
# schedule.every(6).hours.do(run_news_agent)  # Alternative: every 6 hours

logging.info("Scheduler started! Agent will run daily at 8:00 AM")
logging.info("Press Ctrl+C to stop the scheduler")

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute