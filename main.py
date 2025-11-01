import logging
import json
import sys
from datetime import datetime
from time import sleep
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from scraper import get_tech_news, get_article_content
# Import the OllamaProcessor class instead of the function
from ollama_processor import OllamaProcessor
# Import the product generator function (now uses /api/chat)
from ollama_product_generator import generate_product_ideas
from notifier import send_email_notification, send_error_notification
from config import LOG_FILE, LOG_LEVEL, RATE_LIMIT_DELAY

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def remove_duplicates(use_cases):
    """Remove duplicate use cases"""
    seen = set()
    unique = []
    
    for uc in use_cases:
        product = uc.get('product', '').lower().strip()
        use_case = uc.get('use_case', '')[:100].lower().strip()
        key = (product, use_case)
        
        if key not in seen and product and use_case:
            seen.add(key)
            unique.append(uc)
    
    logger.info(f"Removed {len(use_cases) - len(unique)} duplicates")
    return unique


def save_results(use_cases, product_ideas):
    """Save results to JSON file"""
    try:
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_use_cases': len(use_cases),
            'total_product_ideas': len(product_ideas) if product_ideas else 0,
            'use_cases': use_cases,
            'product_ideas': product_ideas or []
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved report to {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        return None


def main():
    """Main execution function"""
    logger.info("="*60)
    logger.info("Starting AI News Agent with Product Idea Generation")
    logger.info("Using Ollama (Local AI)")
    logger.info("="*60)
    
    start_time = datetime.now()
    
    try:
        # Create an instance of the OllamaProcessor
        ollama_proc = OllamaProcessor()

        # Step 1: Get latest tech news
        logger.info("Fetching latest AI news...")
        articles = get_tech_news()
        
        # Limit to first 12 articles
        if len(articles) > 12:
            logger.info(f"Limiting from {len(articles)} to 12 articles")
            articles = articles[:12]
        
        if not articles:
            logger.warning("No articles found. Exiting.")
            return
        
        logger.info(f"Found {len(articles)} relevant articles")
        
        all_use_cases = []
        
        # Step 2: Process each article
        for i, article in enumerate(articles):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {i+1}/{len(articles)}")
            logger.info(f"Source: {article['source']}")
            logger.info(f"Title: {article['title']}")
            logger.info(f"{'='*60}")
            
            # Use RSS summary (since full article fetch is blocked by firewall)
            content = article.get('content') or article.get('summary')

            if content and len(content) > 50:  # Only process if summary has substance
                logger.info(f"Using RSS summary ({len(content)} chars)")
                # Call the method on the instance
                use_cases = ollama_proc.extract_use_cases(content, article['title']) # Note: swapped content and title order
            
                if use_cases:
                    # Assuming use_cases from the class method are strings
                    # If they are strings, wrap them or convert them to the expected dict format
                    # For now, let's assume they are strings and convert them
                    processed_use_cases = []
                    for uc_str in use_cases:
                        processed_use_cases.append({
                            'product': 'General', # Placeholder if product isn't extracted separately
                            'use_case': uc_str,
                            'source_article': article['title'],
                            'source_url': article['url'],
                            'source_name': article['source']
                        })
                    
                    all_use_cases.extend(processed_use_cases)
                    logger.info(f"Found {len(use_cases)} use cases")
                else:
                    logger.info("No use cases found in this article")
            else:
                logger.warning(f"Could not retrieve content")
            
            if i < len(articles) - 1:
                sleep(RATE_LIMIT_DELAY)
        
        # Step 3: Remove duplicates
        logger.info(f"\n{'='*60}")
        logger.info("Processing results...")
        unique_use_cases = remove_duplicates(all_use_cases)
        
        # Step 4: Generate Product Ideas
        product_ideas = []
        if unique_use_cases:
            logger.info(f"\n{'='*60}")
            logger.info("Generating product ideas from use cases...")
            # Pass the list of use case strings to the product generator
            use_case_strings = [uc['use_case'] for uc in unique_use_cases]
            product_ideas = generate_product_ideas(use_case_strings) # Pass list of strings
            
            if product_ideas:
                logger.info(f"Generated {len(product_ideas)} product ideas!")
            else:
                logger.warning("No product ideas generated")
        
        # Step 5: Save to file
        save_results(unique_use_cases, product_ideas)
        
        # Step 6: Send notification
        logger.info(f"\n{'='*60}")
        logger.info("Sending email notification...")
        
        if unique_use_cases or product_ideas:
            success = send_email_notification(unique_use_cases, product_ideas)
            
            if success:
                logger.info("Email sent successfully!")
            else:
                logger.error("Failed to send email")
        else:
            logger.warning("No use cases or product ideas found. Sending error notification...")
            success = send_error_notification(articles)
            
            if success:
                logger.info("Error notification sent successfully!")
            else:
                logger.error("Failed to send error notification")
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info("SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Articles processed: {len(articles)}")
        logger.info(f"Total use cases found: {len(all_use_cases)}")
        logger.info(f"Unique use cases: {len(unique_use_cases)}")
        logger.info(f"Product ideas generated: {len(product_ideas)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"{'='*60}")
        logger.info("AI News Agent completed successfully!")
        logger.info(f"{'='*60}")
        
    except KeyboardInterrupt:
        logger.info("\nAgent interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()