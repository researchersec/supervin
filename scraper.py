import sqlite3
from types import NotImplementedType
import re
import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_website(url):
    service = Service(executable_path=r'chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    SCROLL_PAUSE_TIME = 3  # Increase pause time
    PRODUCT_HEIGHT = 300  # Adjust this value if needed
    num_scrolls = 3100  # Arbitrarily set a high number for num_scrolls to ensure reaching the end

    for _ in range(num_scrolls):
        driver.execute_script(f"window.scrollBy(0, {PRODUCT_HEIGHT});")
        time.sleep(SCROLL_PAUSE_TIME)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles = soup.find_all('article', class_='col-12 col-sm-6 col-lg-4')

    driver.quit()
    return articles

def create_or_connect_database():
    conn = sqlite3.connect('supervin.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            wine_link TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price_1 TEXT,
            price_6 TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            name_id INTEGER,
            FOREIGN KEY (name_id) REFERENCES names(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT,
            name_id INTEGER,
            FOREIGN KEY (name_id) REFERENCES names(id)
        )
    ''')

    return cursor, conn

def update_or_insert_data(cursor, conn, articles):
    for article in articles:
        wine_name = article.find('h4') and article.find('h4').text.strip()
        prices = article.find_all('span', class_='price')
        wine_link = article.find('a', href=True) and article.find('a')['href'].strip()

        name_id = None

        if prices:
            wine_price_1 = prices[0].text.strip().replace('DKK', '')
            wine_price_6 = prices[1].text.strip().replace('DKK', '') if len(prices) > 1 else None

            cursor.execute('''
                SELECT prices.id, price_1, price_6
                FROM prices
                INNER JOIN names ON prices.name_id = names.id
                WHERE names.name = ?
            ''', (wine_name,))
            existing_prices = cursor.fetchone()

            if existing_prices:
                if existing_prices[1] != wine_price_1 or existing_prices[2] != wine_price_6:
                    cursor.execute('INSERT INTO prices (price_1, price_6, name_id) VALUES (?, ?, ?)',
                                   (wine_price_1, wine_price_6, existing_prices[0]))
                name_id = existing_prices[0]

            elif not existing_prices:
                cursor.execute('SELECT id FROM names WHERE name = ?', (wine_name,))
                existing_name = cursor.fetchone()

                if existing_name:
                    name_id = existing_name[0]
                else:
                    cursor.execute('INSERT INTO names (name, wine_link) VALUES (?, ?)', (wine_name, wine_link))
                    name_id = cursor.lastrowid

                cursor.execute('INSERT INTO prices (price_1, price_6, name_id) VALUES (?, ?, ?)',
                               (wine_price_1, wine_price_6, name_id))

            cursor.execute('INSERT INTO reviews (review, name_id) VALUES (?, ?)', ('', name_id))

    conn.commit()
    conn.close()

def main():
    url = "https://www.supervin.dk/vin/rodvin?Products%5BrefinementList%5D%5Bfacet_types%5D%5B0%5D=R%C3%B8dvin"
    articles = scrape_website(url)
    cursor, conn = create_or_connect_database()
    update_or_insert_data(cursor, conn, articles)

if __name__ == "__main__":
    main()
