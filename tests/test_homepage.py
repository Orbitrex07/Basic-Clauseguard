import os

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()

    # Keep Chrome visible while developing tests.
    browser = webdriver.Chrome(options=options)
    browser.set_window_size(1440, 900)

    yield browser
    browser.quit()


def test_clauseguard_homepage_loads(driver):
    base_url = os.getenv(
        "CLAUSEGUARD_URL",
        "http://127.0.0.1:8000"
    )

    driver.get(base_url)

    # Wait until the document has loaded.
    WebDriverWait(driver, 15).until(
        lambda browser:
            browser.execute_script(
                "return document.readyState"
            ) == "complete"
    )

    assert driver.current_url.startswith(base_url)
    assert driver.find_element("tag name", "body").is_displayed()
    assert driver.find_element("tag name", "body").text.strip()
