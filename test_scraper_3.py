# GUIA CAT RESTAURANTS WEBSITE: https://guiacat.cat/en

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://guiacat.cat"


def extract_categories(url: str) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("ul.btn_list a")

    categories = []
    for link in links:
        name = link.get_text(strip=True).split("(")[0].strip()
        slug = link.get("slug")
        href = link.get("href")
        full_url = f"{BASE_URL}{href}" if href else None

        categories.append({
            "name": name,
            "slug": slug,
            "url": full_url
        })
    
    return categories


def extract_restaurants(category: dict) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(category["url"], headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    restaurants = []
    for li in soup.select("ul.rest_description li"):
        name_tag = li.find("a", class_="r_name")
        if name_tag:
            name = name_tag.get_text(strip=True)
            href = name_tag.get("href")
            full_url = f"{BASE_URL}{href}" if href else None
            restaurants.append({
                "name": name,
                "category": category["name"],
                "url": full_url
            })
    return restaurants


def extract_restaurant_details(entry):
    url = entry["url"]
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Location (province, region, city)
        breadcrumb_items = soup.select("ol.breadcrumb li span")
        location = [item.get_text(strip=True) for item in breadcrumb_items]
        province, region, city = (location + [None] * 3)[:3]

        # Address and ZIP code
        address_tag = soup.select_one("address")
        raw_address = address_tag.get_text(strip=True) if address_tag else None

        if raw_address:
            cleaned_address = re.sub(r'\s+', ' ', raw_address).strip()
            address_list = cleaned_address.split(" ")
            zip_code = address_list[0]
            address_dir = " ".join(address_list[1:])
            full_address = f"{address_dir}, {city}, {region}"
        else:
            zip_code = None
            full_address = None

        # Cuisines (from #cusine-section)
        cuisine_list = []
        cuisine_section = soup.select_one("#cusine-section ul.detail-list")
        if cuisine_section:
            cuisine_list = [
                a.get_text(strip=True) for a in cuisine_section.select("li a")
                if a.get_text(strip=True)
            ]

        # Foods (from #food-section)
        food_list = []
        food_section = soup.select_one("#food-section ul.detail-list")
        if food_section:
            food_list = [
                a.get_text(strip=True) for a in food_section.select("li a")
                if a.get_text(strip=True)
            ]

        # Prices
        prices = soup.select(".ncs-avg-price .p2")
        raw_avg_price = prices[0].get_text(strip=True) if len(prices) > 0 else None
        avg_price = re.sub(r'\s*-\s*', ' - ', re.sub(r'\s+', ' ', raw_avg_price)).strip() if raw_avg_price else None
        menu_price = prices[1].get_text(strip=True) if len(prices) > 1 else None
        delivery = prices[2].get_text(strip=True) if len(prices) > 2 else None
        takeout = prices[3].get_text(strip=True) if len(prices) > 3 else None

        return {
            "name": entry['name'],
            "address": full_address,
            "city": city,
            "price": avg_price,
            "cuisine": ", ".join(cuisine_list),
            "opening_h": None,
            "description": None,
            "dishes": ", ".join(food_list),
            "ambience": None,
            "score": 0/10
        }

    except Exception as e:
        return {**entry, "error": str(e)}


if __name__ == "__main__":
    start_url = "https://guiacat.cat/en/contents/showCuisines/"
    all_restaurants = []

    #Step 1: Get all categories
    category_data = extract_categories(start_url)

    # Step 2: Loop through categories and extract restaurant listings
    for category in category_data:
        print(f"Scraping category: {category['name']}")
        restaurants = extract_restaurants(category)
        all_restaurants.extend(restaurants)
        time.sleep(1)  # polite delay

    # Step 3: Fetch details for each restaurant
    detailed_data = []
    for idx, r in enumerate(all_restaurants, start=1):
        print(f"[{idx}/{len(all_restaurants)}] Fetching details for: {r['name']}")
        detailed = extract_restaurant_details(r)
        detailed_data.append(detailed)
        time.sleep(1)  # polite delay

    # Step 4: Save to CSV
    df = pd.DataFrame(detailed_data)
    df.to_csv("guia_cat_detailed_restaurants.csv", index=False)
    print("✅ Saved to 'guia_cat_detailed_restaurants.csv'")
