import sys
from os import getcwd, getenv, path, remove
from time import sleep

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chromium.options import ChromiumOptions as Options
from selenium.webdriver.chromium.service import ChromiumService as Service

from coin_in_selenium import logging
from coin_in_selenium.resources.portfolio import Portfolio
from coin_in_selenium.resources.protonmail import Protonmail
from coin_in_selenium.resources.report import generate_report

protonmail = Protonmail(getenv("PROTON_USERNAME"), getenv("PROTON_PASSWORD"))
option = Options()
option.binary_location = "/usr/bin/chromium"

match getenv("ENVIORNMENT"):
    case "dev":
        if int(getenv("HEADLESS")):
            logging.debug("Using Headless mode")

            service = Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                log_path="logs/chromium.log",
                start_error_message="FAILED",
            )
            option.add_argument("--headless")
        else:
            logging.debug("Using Headful mode")
            service = Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                log_path="logs/chromium.log",
                start_error_message="FAILED",
                env={"DISPLAY": f":{getenv('DISPLAY', '0.0')}".removeprefix(":")},
            )
    case "prod":
        ## in production, chromium will start in headless mode, and will use least memory possible

        service = Service(
            executable_path="/usr/bin/chromedriver",
            log_path="logs/chromium.log",
            start_error_message="Failed to start , try again",
        )
        option.add_argument("--headless")
        option.add_argument("--aggressive-cache-discard")
        option.add_argument("--aggressive-tab-discard")
        option.add_argument("--disable-accelerated-2d-canvas")
        option.add_argument("--disable-application-cache")
        option.add_argument("--disable-cache")
        option.add_argument("--disable-dev-shm-usage")
        option.add_argument("--disable-gpu")
        option.add_argument("--disable-offline-load-stale-cache")
        option.add_argument("--disable-setuid-sandbox")
        option.add_argument("--disable-setuid-sandbox")
        option.add_argument("--disable-site-isolation-trials")
        option.add_argument("--disk-cache-size=0")
        option.add_argument("--ignore-certificate-errors")
        option.add_argument("--no-first-run")
        option.add_argument("--no-sandbox")
        option.add_argument("--no-zygote")
        option.add_argument("--enable-low-end-device-mode")
        option.add_argument("--single-process")
        option.add_argument("--renderer-process-limit=2")

with webdriver.Chrome(
    service=service,
    options=option,
) as driver:
    driver.implicitly_wait(10)

    driver.get("https://coin.zerodha.com/")

    login = driver.find_element(
        By.CSS_SELECTOR, ".redirect-btn-container > a:nth-child(1)"
    )
    login.click()
    logging.debug(driver.current_url)

    if getenv("ENVIRONMENT") == "prod":
        sleep(int(getenv("WAIT", "5")))

    # USER ID
    driver.find_element(By.CSS_SELECTOR, "#userid").send_keys(getenv("ZERODHA_ID"))

    # PASSWORD
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(getenv("ZERODHA_PASS"))

    # SUBMIT (1/2) - USER_ID , PASSWORD
    driver.find_element(By.CLASS_NAME, "button-orange.wide").send_keys(Keys.ENTER)

    sleep(int(getenv("WAIT", "5")))

    # "Problem with External TOTP?"
    driver.find_element(By.CSS_SELECTOR, "a.text-light.forgot-link").click()

    sleep(20)
    # "SMS/Email OTP"
    driver.find_element(By.CSS_SELECTOR, "a.twofa-option").click()

    # PIN , Sent by "noreply@alertsmailer.zerodha.net", pin is in message and subject section
    otp_code = None
    while otp_code is None:

        otp_code = protonmail.get_subject_by_sender("noreply@alertsmailer.zerodha.net")
        if otp_code is not None:
            otp_code = otp_code.split(" ", maxsplit=1)[0]
            break
        sleep(int(getenv("WAIT", "5")))

    driver.find_element(
        By.CSS_SELECTOR,
        ".su-input-group > input:nth-child(2)",
    ).send_keys(otp_code)

    sleep(int(getenv("WAIT", "5")))
    
    driver.get("https://coin.zerodha.com/dashboard/mf/portfolio")
    
    sleep(int(getenv("WAIT", "5")))

    pf = Portfolio(driver.page_source)

    # driver.get_screenshot_as_file("screenshot/screenshot.png")
    # driver.
    body_element = driver.find_element(By.TAG_NAME, 'body')
    if body_element.screenshot("screenshot/screenshot.png"):

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

    driver.get("https://coin.zerodha.com/logout")  # LOGOUT from Zerodha
    sleep(int(getenv("WAIT", "5")))

    protonmail.proton_session.logout()
    remove(protonmail.session_file)
    sys.exit(0)
