import json
import os
import random
import time

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# If undetected_chromedriver's auto-download keeps failing (ConnectionResetError),
# set this to your installed Chrome's major version number (chrome://settings/help)
# e.g. CHROME_VERSION_MAIN = 139
CHROME_VERSION_MAIN = None

# Persistent Chrome profile directory - keeps you logged into Amazon between runs
# so you only have to sign in once instead of every single time.
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")

# If downloads keep getting reset even with retries, download chromedriver manually from
# https://googlechromelabs.github.io/chrome-for-testing/ and put the .exe path here, e.g.
# DRIVER_EXECUTABLE_PATH = r"C:\Users\TRETEC\Desktop\Review-Guardian\chromedriver.exe"
DRIVER_EXECUTABLE_PATH = None

# Silence the harmless "OSError: [WinError 6] The handle is invalid" that
# undetected_chromedriver's __del__ sometimes throws on interpreter shutdown (Windows only).
uc.Chrome.__del__ = lambda self: None

DEBUG_DIR = "debug"


def build_stealth_driver(headless=False, driver_path=None, retries=3):
    """Builds an undetected Chrome driver instance with stealth property overrides.

    Retries the chromedriver auto-download a few times since the download
    occasionally gets reset by AV/network interference (WinError 10054).
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")

    kwargs = {"options": options, "headless": headless}
    if CHROME_VERSION_MAIN:
        kwargs["version_main"] = CHROME_VERSION_MAIN
    if driver_path:
        kwargs["driver_executable_path"] = driver_path

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            driver = uc.Chrome(**kwargs)
            break
        except Exception as e:
            last_error = e
            print(f"[!] Chrome driver init failed (attempt {attempt}/{retries}): {e}")
            time.sleep(3)
    else:
        print("\n[x] Could not start Chrome after repeated attempts.")
        print("    This is usually antivirus/firewall blocking the chromedriver download.")
        print("    Fix options:")
        print("      1. Temporarily disable Windows Defender real-time protection and retry.")
        print("      2. Download chromedriver manually from:")
        print("         https://googlechromelabs.github.io/chrome-for-testing/")
        print("         then set DRIVER_EXECUTABLE_PATH at the top of this file to its .exe path.")
        raise last_error

    # Patch properties bot-detectors commonly inspect
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                window.chrome = {runtime: {}};
            """
        },
    )
    return driver


def human_delay(min_seconds=2.0, max_seconds=4.5):
    """Randomized pauses so request timing doesn't look automated."""
    time.sleep(random.uniform(min_seconds, max_seconds))


def check_for_captcha(driver):
    """Returns True if the current page looks like a CAPTCHA / robot check."""
    title_lower = driver.title.lower()
    source_lower = driver.page_source.lower()
    return (
        "robot check" in title_lower
        or "captcha" in title_lower
        or "captcha" in source_lower
        or "enter the characters you see below" in source_lower
    )


def check_for_signin_wall(driver):
    """Returns True if Amazon redirected to the sign-in page instead of showing reviews."""
    return "ap/signin" in driver.current_url or "signin" in driver.title.lower()


def dump_debug_info(driver, page):
    """Saves a screenshot + HTML snapshot so you can see exactly what the browser saw."""
    os.makedirs(DEBUG_DIR, exist_ok=True)
    shot_path = os.path.join(DEBUG_DIR, f"page{page}_failure.png")
    html_path = os.path.join(DEBUG_DIR, f"page{page}_failure.html")
    try:
        driver.save_screenshot(shot_path)
    except Exception as e:
        shot_path = f"(failed to save: {e})"
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception as e:
        html_path = f"(failed to save: {e})"

    print(f"    Current URL:   {driver.current_url}")
    print(f"    Page title:    {driver.title}")
    print(f"    Screenshot:    {shot_path}")
    print(f"    HTML snapshot: {html_path}")


def wait_for_reviews(driver, review_url, timeout=10, max_retries=3):
    """
    Waits for review elements to appear. If a CAPTCHA or sign-in wall is detected
    instead, pauses for manual action and retries (up to max_retries times).
    Returns True if reviews were found, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="review"]'))
        )
        return True
    except Exception:
        pass

    for attempt in range(1, max_retries + 1):
        if check_for_signin_wall(driver):
            print(f"\n🔒 Amazon is asking you to sign in (attempt {attempt}/{max_retries}).")
            print("    Please log into your Amazon account in the browser window.")
            print("    This only needs to happen once - the session will be saved for next time.")
            input("    Press Enter here once you're logged in...")
            driver.get(review_url)  # navigate back to the review page after login
            human_delay(2.0, 3.5)
        elif check_for_captcha(driver):
            print(f"\n⚠️  CAPTCHA / robot check detected (attempt {attempt}/{max_retries}).")
            print("    Please solve it manually in the browser window that opened.")
            input("    Press Enter here once you've solved it and the page has loaded...")
        else:
            break  # not a known blocker, no point retrying blindly

        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="review"]'))
            )
            return True
        except Exception:
            continue

    print("[-] No review elements found.")
    return False


def scrape_amazon_reviews(asin: str, max_pages: int = 3):
    """Scrapes product reviews for a given Amazon ASIN up to `max_pages`."""
    driver = build_stealth_driver(headless=False, driver_path=DRIVER_EXECUTABLE_PATH)
    reviews = []

    try:
        for page in range(1, max_pages + 1):
            url = f"https://www.amazon.com/product-reviews/{asin}?pageNumber={page}&sortBy=recent"
            print(f"\n[+] Fetching Page {page}: {url}")
            driver.get(url)

            human_delay(2.5, 5.0)

            found = wait_for_reviews(driver, review_url=url, timeout=10)
            if not found:
                dump_debug_info(driver, page)
                print(f"[-] Stopping at page {page}.")
                break

            review_elements = driver.find_elements(
                By.CSS_SELECTOR, '[data-hook="review"]'
            )
            print(f"[+] Found {len(review_elements)} reviews on page {page}.")

            for el in review_elements:
                # Review Title
                try:
                    title = el.find_element(
                        By.CSS_SELECTOR, '[data-hook="review-title"]'
                    ).text.strip()
                except Exception:
                    title = ""

                # Star Rating
                try:
                    rating = el.find_element(
                        By.CSS_SELECTOR, '[data-hook="review-star-rating"]'
                    ).get_attribute("textContent").strip()
                except Exception:
                    try:
                        rating = el.find_element(
                            By.CSS_SELECTOR, '[data-hook="cmps-review-star-rating"]'
                        ).get_attribute("textContent").strip()
                    except Exception:
                        rating = ""

                # Review Date
                try:
                    date = el.find_element(
                        By.CSS_SELECTOR, '[data-hook="review-date"]'
                    ).text.strip()
                except Exception:
                    date = ""

                # Review Text Body
                try:
                    body = el.find_element(
                        By.CSS_SELECTOR, '[data-hook="review-body"]'
                    ).text.strip()
                except Exception:
                    body = ""

                reviews.append(
                    {
                        "title": title,
                        "rating": rating,
                        "date": date,
                        "body": body,
                    }
                )

            # Check if we've reached the last page
            next_button = driver.find_elements(
                By.CSS_SELECTOR, "li.a-last:not(.a-disabled) a"
            )
            if not next_button:
                print("[+] Reached the final page of reviews.")
                break

            human_delay(1.5, 3.0)

    finally:
        driver.quit()

    return reviews


if __name__ == "__main__":
    product_asin = input("Enter Amazon Product ID (ASIN, e.g., B08N5WRWNW): ").strip()

    if product_asin:
        pages_to_scrape = 3  # Adjust max pages as needed
        data = scrape_amazon_reviews(product_asin, max_pages=pages_to_scrape)

        print(f"\n[✓] Total reviews scraped: {len(data)}")

        # Save output to JSON
        output_file = f"{product_asin}_reviews.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[✓] Saved results to '{output_file}'")