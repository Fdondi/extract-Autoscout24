import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from time import sleep
from random import uniform


base_url = "https://www.autoscout24.ch"
lang = "it"  # SELECT LANGUAGE
lang_specific = {
    "it": "automobili/tutte-le-marche",
    "de": "autos/alle-marken",
    "fr": "voitures/toutes-les-marques"
}
index_url = f"{base_url}/{lang}/{lang_specific[lang]}"


def try_goto(link, browser, timeout=1):
    page = browser.new_page()
    try:
        page.goto(link)
    except PlaywrightTimeoutError:
        page.close()
        # Once we hit 1000 seconds, we include an increasing chance to give up 
        if uniform(0, 1) > 1000/timeout:
            print('roll failed, giving up')
            return None
        if timeout > 100:  # only warn once the delay becomes significant
            print(f'Timeout on {link}; sleeping {timeout}s then retrying')
        sleep(timeout)
        return try_goto(link, browser, 2 * timeout)
    except Exception as ex:
        print(f'Unknown exception {ex} on {link}, giving up')
        page.close()
        return None
    return page


def ensure_file(link, browser):
    filename = f'download/{link[6:]}.html'  # remove the language prefix, add folder and extension
    if os.path.isfile(filename):
        return
    page = try_goto(f'{base_url}{link}', browser)
    if page is not None:
        with open(filename, 'w') as f:
            f.write(page.content())
        page.close()
    sleep(uniform(0.1, 0.3))  # avoid making calls too close by keeping the page open between 0.1 and 3 seconds    


def read_index(i, browser):
    index_page = try_goto(f'{index_url}?page={i}&vehtyp=10', browser)
    if index_page is None:
        print(f'ERROR could not open index page #{i}, skipping')
        return
    link_elements = index_page.query_selector_all("article.vehicle-card a.base-a-link")
    for link_element in link_elements:
        ensure_file(link_element.get_attribute("href"), browser)
    index_page.close()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Headless seems to trigger bot detection.
    for i in range(1, 7716):
        read_index(i, browser)
        # avoid making calls too close by sleeping between 0.5 and 5 seconds
        sleep(uniform(0.5, 5))
    browser.close()
