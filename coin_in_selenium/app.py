import sys
from os import getcwd, getenv, path
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from coin_in_selenium.resources.portfolio import Portfolio
from coin_in_selenium.resources.report import generate_report
from coin_in_selenium import log


service = Service(
    executable_path=GeckoDriverManager().install(),
    env={"MOZ_HEADLESS": "1"},  # FOR HEADLESS
    # env={"DISPLAY": ":0.0"},  # TO DISPLAY
)

option = Options()
option.binary = "/usr/bin/firefox"
with webdriver.Firefox(service=service, options=option) as driver:

    driver.get("https://coin.zerodha.com/")
    log.debug(driver.current_url)

    login = driver.find_element(
        By.CSS_SELECTOR, ".redirect-btn-container > a:nth-child(1)"
    )
    login.click()
    log.debug(driver.current_url)

    sleep(5)
    # USER ID
    driver.find_element(By.CSS_SELECTOR, "#userid").send_keys(getenv("ZERODHA_ID"))

    # PASSWORD
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(getenv("ZERODHA_PASS"))

    # SUBMIT (1/2) - USER_ID , PASSWORD
    driver.find_element(By.CLASS_NAME, "button-orange.wide").send_keys(Keys.ENTER)

    sleep(1.5)
    # PIN
    driver.find_element(By.CSS_SELECTOR, "#pin").send_keys(getenv("ZERODHA_PIN"))

    # SUBMIT (2/2) - LOGIN
    driver.find_element(By.CLASS_NAME, "button-orange.wide").send_keys(Keys.ENTER)

    sleep(5)
    driver.get("https://coin.zerodha.com/dashboard/mf/portfolio")
    log.debug(driver.current_url)

    sleep(5)
    pf = Portfolio(driver.page_source)
    # print(pf.get_current())
    # print(pf.get_invested())
    # print(pf.get_pnl())

    with open("screenshot.png", "wb") as __input:
        __input.write(driver.get_screenshot_as_png())

    report = (
        generate_report(
            photo_path=path.join(getcwd(), "screenshot.png"),
            current=pf.get_current(),
            invested=pf.get_invested(),
            pnl=pf.get_pnl(),
        )
    )

    if report["ok"]:
        log.info(report)
    else:
        log.error(report)


    # if input("EXIT?") == "y":
    sys.exit(0)
# driver.close()
