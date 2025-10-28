import json
import random
import time
import os
import platform
import urllib.request
import tarfile
import zipfile
import shutil
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

FIREFOX_VERSION = "125.0.3"

def get_firefox_url():
    system = platform.system()
    arch = platform.machine()

    if system == "Windows":
        return f"https://ftp.mozilla.org/pub/firefox/releases/{FIREFOX_VERSION}/win64/en-US/firefox-{FIREFOX_VERSION}.zip"
    elif system == "Darwin":
        if "aarch64" in arch.lower() or "arm64" in arch.lower():
             return f"https://ftp.mozilla.org/pub/firefox/releases/{FIREFOX_VERSION}/mac-aarch64/en-US/Firefox%20{FIREFOX_VERSION}.dmg"
        else:
            return f"https://ftp.mozilla.org/pub/firefox/releases/{FIREFOX_VERSION}/mac/en-US/Firefox%20{FIREFOX_VERSION}.dmg"
    elif system == "Linux":
        return f"https://ftp.mozilla.org/pub/firefox/releases/{FIREFOX_VERSION}/linux-x86_64/en-US/firefox-{FIREFOX_VERSION}.tar.bz2"
    else:
        raise Exception(f"Unsupported operating system: {system}")

def setup_portable_firefox():
    firefox_dir = os.path.join(os.getcwd(), "firefox_portable")
    firefox_exe = os.path.join(firefox_dir, "firefox", "firefox.exe" if platform.system() == "Windows" else "firefox")

    if not os.path.exists(firefox_exe):
        print("Portable Firefox not found. Downloading...")
        url = get_firefox_url()
        filename = url.split("/")[-1].replace("%20", " ")
        download_path = os.path.join(os.getcwd(), filename)

        with urllib.request.urlopen(url) as response, open(download_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        print(f"Downloaded {filename}. Extracting...")

        if filename.endswith(".zip"):
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(firefox_dir)
        elif filename.endswith(".tar.bz2"):
            with tarfile.open(download_path, "r:bz2") as tar:
                tar.extractall(firefox_dir)
        elif filename.endswith(".dmg"):
            print("DMG downloaded. Please mount it and copy the Firefox application to the 'firefox_portable' directory.")
            pass

        os.remove(download_path)
        print("Extraction complete.")

    return firefox_exe

def load_search_terms(filename="search_terms.json"):
    with open(filename, "r") as f:
        return json.load(f)

def human_like_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.02, 0.1))

def check_for_captcha(driver):
    try:
        text1_present = driver.find_element(By.XPATH, "//*[contains(text(), 'One last step')]")
        text2_present = driver.find_element(By.XPATH, "//*[contains(text(), 'Please solve the challenge below to continue')]")
        
        if text1_present and text2_present:
            while True:
                print("Captcha or unexpected page detected. The script is paused.")
                input("Please solve the captcha or resolve the issue in the browser, then press Enter here to continue...")
                try:
                    # After user solves captcha, we expect the search results to be present
                    driver.find_element(By.ID, "b_results")
                    return # Captcha solved
                except:
                    continue # Captcha not solved yet
    except:
        pass # No captcha text found

def human_like_actions(driver):
    check_for_captcha(driver)
    if random.random() < 0.2: # 20% chance to scroll
        print("Scrolling...")
        scroll_percentage = random.uniform(0.3, 0.8)
        driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_percentage});")
        time.sleep(random.uniform(0.5, 1.5))

    check_for_captcha(driver)
    if random.random() < 0.05: # 5% chance to click a link
        print("Clicking a link...")
        try:
            links = driver.find_elements(By.CSS_SELECTOR, "#b_results .b_algo h2 a")
            if links:
                random.choice(links).click()
                time.sleep(random.uniform(2, 5))
                driver.back()
        except:
            pass

# def simulate_recommended_search(driver, search_term):
#     print("Simulating recommended search...")
#     search_bar = driver.find_element(By.ID, "sb_form_q")
#     search_bar.clear()
#     words = search_term.split()
#     for i, word in enumerate(words):
#         human_like_typing(search_bar, word + " ")
#         time.sleep(random.uniform(0.2, 0.5))
#         try:
#             suggestions = driver.find_elements(By.CSS_SELECTOR, "#sa_ul .sa_sg")
#             for suggestion in suggestions:
#                 if suggestion.text.lower() == search_term.lower():
#                     suggestion.click()
#                     return
#         except:
#             pass
#     search_bar.send_keys(Keys.RETURN)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--private", action="store_true", help="Use a private window.")
    args = parser.parse_args()

    print("Starting the Microsoft Rewards points scraper.")
    print("This script uses a portable version of Firefox to ensure compatibility.")

    try:
        firefox_binary = setup_portable_firefox()
        options = FirefoxOptions()
        options.binary_location = firefox_binary
        if args.private:
            options.add_argument("-private")
        else:
            profile_path = os.path.join(os.getcwd(), 'firefox_persistent_profile')
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
            options.add_argument(f"-profile")
            options.add_argument(profile_path)

        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 10)
    except Exception as e:
        print(f"Error setting up the driver: {e}")
        return

    driver.get("https://www.bing.com")
    print("\n>>> The browser window has opened. <<<")
    input("Please ensure you are logged in to your Microsoft account, then press Enter here to continue...")

    main_window = driver.current_window_handle
    search_chains = load_search_terms()
    searches = []
    while len(searches) < 33:
        searches.extend(random.choice(search_chains))

    print(f"Performing {len(searches)} searches.")

    for i, search_term in enumerate(searches):
        try:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get("https://www.bing.com")
            
            check_for_captcha(driver)
            # if random.random() < 0.3: # 30% chance to simulate recommended search
            #     simulate_recommended_search(driver, search_term)
            # else:
            search_bar = wait.until(EC.presence_of_element_located((By.ID, "sb_form_q")))
            search_bar.clear()
            human_like_typing(search_bar, search_term)
            search_bar.send_keys(Keys.RETURN)

            check_for_captcha(driver)

            print(f"Search {i + 1}/{len(searches)}: {search_term}")
            time.sleep(random.uniform(2, 5))
            human_like_actions(driver)

            driver.close()
            driver.switch_to.window(main_window)

        except Exception as e:
            print(f"An error occurred during search {i + 1}: {e}")
            # Attempt to recover by closing the tab and going back to the main window
            try:
                driver.close()
            except:
                pass
            driver.switch_to.window(main_window)
            driver.get("https://www.bing.com")

    print("All searches completed.")

    print("Opening Microsoft Rewards dashboard...")
    driver.get("https://rewards.bing.com/")
    # driver.quit()

if __name__ == "__main__":
    main()
