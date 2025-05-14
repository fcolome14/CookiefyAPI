import requests
from bs4 import BeautifulSoup
import pandas as pd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def scrap_website(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    restaurants = []

    for article in soup.select("article.grid__block"):
        title_tag = article.select_one("h3.block__title a")
        address_tag = article.select_one("div.direccion span")
        phone_tag = article.select_one("div.telefono a")
        price_tag = article.select_one("span.precio")
        barrio_tags = article.select("span.barrio")
        cuisine_tags = article.select("span.tipo_cocina")

        restaurants.append({
            "name": title_tag.text.strip() if title_tag else None,
            "link": title_tag["href"] if title_tag else None,
            "address": address_tag.text.strip() if address_tag else None,
            "phone": phone_tag.text.strip() if phone_tag else None,
            "price": price_tag.text.strip() if price_tag else None,
            "barrios": ", ".join([b.text.strip() for b in barrio_tags]),
            "cuisines": ", ".join([c.text.strip() for c in cuisine_tags]),
        })

    df = pd.DataFrame(restaurants)
    df.to_csv("asiatic_restaurants_bcn.csv", index=False, encoding="utf-8")
    logger.info("Saved to asiatic_restaurants_bcn.csv")
