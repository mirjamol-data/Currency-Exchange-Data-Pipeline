# pipeline/scheduler.py
import schedule
import time
import logging
from extract import run_extraction
from transform_silver import process_bronze_to_silver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def daily_job():
    logging.info("--- Starting Daily Data Pipeline Run ---")
    try:
        run_extraction("latest")
        process_bronze_to_silver()
        logging.info("--- Daily Data Pipeline Run Completed Successfully ---")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    # Schedule to run daily at 8:00 AM UTC+5 (which is 03:00 UTC)
    # Note: If your local machine is on a different timezone, 
    # adjust the time string below so it corresponds to 8:00 AM UTC+5 for you.
    schedule_time = "03:00" 
    
    schedule.every().day.at(schedule_time).do(daily_job)
    
    logging.info(f"Scheduler started. Pipeline will run daily at {schedule_time} UTC.")
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Wait one minute before checking the schedule again