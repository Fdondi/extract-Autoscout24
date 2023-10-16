from playwright.sync_api import sync_playwright

from time import sleep
from random import uniform


base_url = "https://www.autoscout24.ch"


def download(link, page):
    page.goto(f'{base_url}{link}')
    filename = f'download/{link[6:]}.html'  # remove the language prefix, add folder and extension
    with open(filename, 'w') as f:
        f.write(page.content())
    sleep(uniform(0.1, 0.3))  # avoid making calls too close by keeping the page open between 0.1 and 3 seconds
    page.close()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Headless seems to trigger bot detection.
    page = browser.new_page()
    for i in range(1, 7716):
        page.goto(f'{base_url}/it/automobili/tutte-le-marche?page={i}&vehtyp=10')
        link_elements = page.query_selector_all("article.vehicle-card a.base-a-link")
        for link_element in link_elements:
            link = link_element.get_attribute("href")
            download(link, browser.new_page())  # This will print each link URL to the console
        # avoid making calls too close by sleeping between 0.5 and 5 seconds
        sleep(uniform(0.5, 5))
    browser.close()
