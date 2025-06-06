import csv
import logging
import time
from google_play_scraper import Sort, reviews
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Bank apps with their package IDs
BANK_APPS = {
    'Commercial Bank of Ethiopia': 'com.combanketh.mobilebanking',
    'Dashen Bank': 'com.dashen.dashensuperapp',
    'Bank of Abyssinia': 'com.dashen.dashensuperapp',

     
}

# Constants
REVIEWS_PER_BANK = 500
MAX_PER_REQUEST = 100  # Google's max per call
SLEEP_TIME = 3  # Seconds between requests

def scrape_bank_reviews(bank_name, app_id):
    """Scrape reviews for a single bank app"""
    reviews_data = []
    token = None
    attempt = 0
    
    while len(reviews_data) < REVIEWS_PER_BANK and attempt < 5:
        try:
            # Fetch reviews batch
            batch, token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=MAX_PER_REQUEST,
                continuation_token=token
            )
            
            if not batch:
                logging.warning(f"No reviews returned for {bank_name}")
                break
                
            # Process reviews
            for review in batch:
                reviews_data.append({
                    'review_text': review['content'],
                    'rating': review['score'],
                    'date': review['at'].strftime('%Y-%m-%d'),
                    'bank_name': bank_name,
                    'source': 'Google Play'
                })
            
            logging.info(f"Scraped {len(batch)} reviews for {bank_name} (Total: {len(reviews_data)})")
            
            # Exit conditions
            if not token or len(reviews_data) >= REVIEWS_PER_BANK:
                break
                
            time.sleep(SLEEP_TIME)
            attempt = 0  # Reset attempt counter after success
            
        except Exception as e:
            attempt += 1
            wait_time = SLEEP_TIME * attempt * 2  # Exponential backoff
            logging.error(f"Attempt {attempt}/5 failed for {bank_name}: {e}. Retrying in {wait_time}s")
            time.sleep(wait_time)
    
    return reviews_data[:REVIEWS_PER_BANK]  # Return max requested reviews

def save_to_csv(reviews, bank_name):
    """Save reviews to CSV with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/raw/{bank_name.replace(" ", "_")}_reviews_{timestamp}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'review_text', 'rating', 'date', 'bank_name', 'source'
        ])
        writer.writeheader()
        writer.writerows(reviews)
    
    logging.info(f"✅ Saved {len(reviews)} reviews to {filename}")
    return filename

def main():
    """Main scraping workflow"""
    logging.info("Starting Google Play Store scraping")
    
    for bank_name, app_id in BANK_APPS.items():
        if not app_id:
            logging.warning(f"Skipping {bank_name} - no package ID provided")
            continue
            
        logging.info(f"Scraping reviews for {bank_name} ({app_id})")
        bank_reviews = scrape_bank_reviews(bank_name, app_id)
        
        if bank_reviews:
            save_to_csv(bank_reviews, bank_name)
        else:
            logging.error(f"No reviews collected for {bank_name}")
    
    logging.info("Scraping completed")

if __name__ == "__main__":
    main()