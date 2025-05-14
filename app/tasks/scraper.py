from celery import shared_task
from app.services.web_scraper_service import scrap_website
from app.utils.logger import get_logger

logger = get_logger(__name__)

@shared_task
def scrap():
    url = "https://bcnfoodieguide.com/tipo-cocina/asiatica/"
    headlines = scrap_website(url)
    logger.info(f"Scraped {len(headlines)} headlines")
    return headlines
