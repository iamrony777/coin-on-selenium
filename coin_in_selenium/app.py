import sys
from os import getcwd, getenv, path
from time import sleep

from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from coin_in_selenium import logging
from coin_in_selenium.resources.portfolio import Portfolio
from coin_in_selenium.resources.protonmail import Protonmail
from coin_in_selenium.resources.report import generate_report

protonmail = Protonmail(getenv("PROTON_USERNAME"), getenv("PROTON_PASSWORD"))

if int(getenv("HEADLESS")):
    logging.debug("GOING HEADLESS")
    service = Service(
        executable_path=GeckoDriverManager(path="cache/").install(),
        log_path="logs/geckodriver.log",
        env={"MOZ_HEADLESS": "1"},  # FOR HEADLESS
    )
else:
    logging.debug("OPENING BROWSER")
    service = Service(
        executable_path=GeckoDriverManager(path="cache/").install(),
        log_path="logs/geckodriver.log",
        env={"DISPLAY": f":{getenv('DISPLAY', '0.0')}".removeprefix(":")},  # TO DISPLAY
    )
option = Options()
option.binary = "/usr/bin/firefox"
with webdriver.Firefox(
    service=service,
    options=option,
) as driver:

    driver.get("https://coin.zerodha.com/")

    login = driver.find_element(
        By.CSS_SELECTOR, ".redirect-btn-container > a:nth-child(1)"
    )
    login.click()
    logging.debug(driver.current_url)

    sleep(int(getenv("WAIT", "5")))
    # USER ID
    driver.find_element(By.CSS_SELECTOR, "#userid").send_keys(getenv("ZERODHA_ID"))

    # PASSWORD
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(
        getenv("ZERODHA_PASS")
    )

    # SUBMIT (1/2) - USER_ID , PASSWORD
    driver.find_element(By.CLASS_NAME, "button-orange.wide").send_keys(Keys.ENTER)

    sleep(int(getenv("WAIT", "5")))

    # IF ASKS FOR MOBILE CODE
    # driver.get_full_page_screenshot_as_file(f"screenshot/{time()}")

    if (
        driver.find_element(By.CSS_SELECTOR, ".su-input-label").text
        == "Mobile App Code"
    ):

        # "Problem with Mobile App Code?"
        driver.find_element(By.CSS_SELECTOR, ".forgot-link").click()

        sleep(20)  # Countdown

        # "SMS/Email OTP"
        driver.find_element(By.CLASS_NAME, "twofa-option").click()

        # PIN , Sent by "noreply@alertsmailer.zerodha.net", pin is in message and subject section
        otp_code = None
        while otp_code is None:
            otp_code = protonmail.get_subject_by_sender(
                "noreply@alertsmailer.zerodha.net"
            )
            if otp_code is not None:
                otp_code = otp_code.split(" ", maxsplit=1)[0]
                break
            sleep(int(getenv("WAIT", "5")))

        driver.find_element(
            By.CSS_SELECTOR,
            ".su-input-group > input:nth-child(2)",
        ).send_keys(otp_code)

    # SUBMIT (2/2) - LOGIN
    driver.find_element(By.CLASS_NAME, "button-orange.wide").send_keys(Keys.ENTER)

    sleep(int(getenv("WAIT", "5")))
    driver.get("https://coin.zerodha.com/dashboard/mf/portfolio")

    sleep(int(getenv("WAIT", "5")))
    pf = Portfolio(driver.page_source)

    driver.get_full_page_screenshot_as_file("screenshot/screenshot.png")

    report = generate_report(
        photo_path=path.join(getcwd(), "screenshot", "screenshot.png"),
        current=pf.get_current(),
        invested=pf.get_invested(),
        pnl=pf.get_pnl(),
    )

    if report["ok"]:
        logging.info(report)
    else:
        logging.error(report)

    # if input("EXIT?") == "y":
    sys.exit(0)
# driver.close()
