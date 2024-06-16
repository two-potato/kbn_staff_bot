import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import logging
from logging.handlers import RotatingFileHandler
from os import getenv

# Logger settings
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler = RotatingFileHandler(
    "logs/scraper.log", mode="w", maxBytes=10000, backupCount=2, encoding="utf-8"
)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)


def get_product_url(search_query: str) -> object:
    """
    Search query transform to soup object. Depends on search url
    """
    search_url = f"https://spb.complexbar.ru/?match=all&subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={search_query}&dispatch=products.search&security_hash=79bedb42e2ceb29d2274d45831b8ec7c&page=1"
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching search results: {e}")
        return None

    return BeautifulSoup(response.text, "html.parser")


def get_product_list_data(search_query: str) -> list[dict]:
    """
    Get elements usingg bs4
    """
    try:
        soup = get_product_url(search_query)
        if not soup:
            logger.warning(f"Bad product link: {search_query}")
            return None

        product_elements = soup.find_all(
            "div", class_="cmx-product-grid__item-body ut2-gl__body"
        )
        if not product_elements:
            logger.warning(f"No products found for query: {search_query}")
            return None

        product_data = []
        for element in product_elements:
            title_element = element.find("a", class_="product-title")
            price_element = element.find("span", class_="ty-price")
            brand_element = element.find(
                "div", class_="cmx-product-grid__item-brand cmx-products-brand-name"
            )
            url_element = element.find("a", class_="product-title")
            art_element = element.find(
                "div", class_="ty-control-group ty-sku-item cm-hidden-wrapper"
            ).find("span")
            img_element = element.find(
                "div",
                class_="cm-gallery-item cm-item-gallery cb-hover-gallery__image-wrapper",
            ).find("img")["data-src"]
            # img_element = "asd"
            if (
                not title_element
                or not price_element
                or not brand_element
                or not url_element
                or not art_element
                or not img_element
            ):
                logger.warning(f"Missing some elements for product: {element}")
                continue

            title = title_element.text.strip()
            price = price_element.text.strip()
            brand = brand_element.text.strip()
            url = url_element["href"]
            art = art_element.text.strip()
            img = img_element

            product_data.append(
                {
                    "title": title,
                    "price": price,
                    "brand": brand,
                    "art": art,
                    "img": img,
                    "url": f"https://spb.complexbar.ru/{url}",
                }
            )
        print(product_data)
        return product_data
    except AttributeError as e:
        logger.error(f"Error parsing product details: {e}")
        return None


def fetch_stock_info(driver, xpath):
    try:
        return (
            WebDriverWait(driver, 5)
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
            .text.strip()
        )
    except TimeoutException:
        logger.warning(f"Timeout while fetching stock info for xpath: {xpath}")
        return "Отсутствует =("


def parse_product_info(search_query: str) -> list[dict]:
    product_data = get_product_list_data(search_query)
    if not product_data:
        return None

    all_products_info = []

    for product in product_data:
        product_url = product.get("url")
        if not product_url:
            continue

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(options=options)

        try:
            driver.get(product_url)
            clarify_stock_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ga-clarify-stock"))
            )
            clarify_stock_link.click()

            stock_info = {
                "stock_warehouse": fetch_stock_info(
                    driver,
                    "//span[contains(text(), 'На складе:')]/following-sibling::span",
                ),
                "remote_warehouse": fetch_stock_info(
                    driver,
                    "//span[contains(text(), 'На удаленном складе:')]/following-sibling::span",
                ),
                "showroom_stock": fetch_stock_info(
                    driver,
                    "//span[contains(text(), 'В шоуруме:')]/following-sibling::span",
                ),
            }

            data = {
                "title": product.get("title", "Неизвестно"),
                "price": product.get("price", "Неизвестно"),
                "brand": product.get("brand", "Неизвестно"),
                "url": product.get("url", "Неизвестно"),
                "art": product.get("art", "Неизвестно"),
                "img": product.get("img", "Неизвестно"),
                **stock_info,
            }

            logger.info(f"Product data: {data}")
            all_products_info.append(data)
        except TimeoutException as e:
            logger.error(f"Error: {e}")
        finally:
            driver.quit()

    return all_products_info
