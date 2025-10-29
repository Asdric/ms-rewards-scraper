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
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def find_installed_firefox():
    """Find installed Firefox browser on the system"""
    system = platform.system()
    if system == "Windows":
        # Check common installation locations for Firefox on Windows
        firefox_locations = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Mozilla Firefox", "firefox.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Mozilla Firefox", "firefox.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Users\\Default\\AppData\\Local"), "Mozilla Firefox", "firefox.exe")
        ]
        for location in firefox_locations:
            if os.path.exists(location):
                return location
    elif system == "Darwin":  # macOS
        location = "/Applications/Firefox.app/Contents/MacOS/firefox"
        if os.path.exists(location):
            return location
    elif system == "Linux":
        # Check common locations or use which command
        import subprocess
        try:
            result = subprocess.run(["which", "firefox"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        # Check common installation locations for Linux
        linux_locations = [
            "/usr/bin/firefox",
            "/usr/local/bin/firefox",
            "/snap/bin/firefox"
        ]
        for location in linux_locations:
            if os.path.exists(location):
                return location

    return None

def find_installed_chrome():
    """Find installed Chrome browser on the system"""
    system = platform.system()
    if system == "Windows":
        # Check common installation locations for Chrome on Windows
        chrome_locations = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Users\\Default\\AppData\\Local"), "Google", "Chrome", "Application", "chrome.exe"),  # User-specific installation
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google", "Chrome Dev", "Application", "chrome.exe"),  # Chrome Dev
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google", "Chrome Dev", "Application", "chrome.exe"),
        ]
        for location in chrome_locations:
            if os.path.exists(location):
                return location
    elif system == "Darwin":  # macOS
        location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(location):
            return location
    elif system == "Linux":
        # Check common locations or use which command
        import subprocess
        try:
            result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            result = subprocess.run(["which", "google-chrome-stable"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        # Check common installation locations for Linux
        linux_locations = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/local/bin/google-chrome",
            "/snap/bin/google-chrome"
        ]
        for location in linux_locations:
            if os.path.exists(location):
                return location

    return None

def find_installed_edge():
    """Find installed Edge browser on the system"""
    system = platform.system()
    if system == "Windows":
        # Check common installation locations for Edge on Windows
        edge_locations = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Users\\Default\\AppData\\Local"), "Microsoft", "Edge", "Application", "msedge.exe")
        ]
        for location in edge_locations:
            if os.path.exists(location):
                return location
    elif system == "Darwin":  # macOS
        location = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        if os.path.exists(location):
            return location
    elif system == "Linux":
        # Check common locations or use which command
        import subprocess
        try:
            result = subprocess.run(["which", "microsoft-edge"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        # Check common installation locations for Linux
        linux_locations = [
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable",
            "/usr/local/bin/microsoft-edge"
        ]
        for location in linux_locations:
            if os.path.exists(location):
                return location

    return None

def setup_browser():
    """Find and set up an installed browser for use"""
    print("Looking for installed browsers...")
    
    # Try Firefox first
    firefox_path = find_installed_firefox()
    if firefox_path:
        print(f"Found Firefox at: {firefox_path}")
        return "firefox", firefox_path

    # Then try Chrome
    chrome_path = find_installed_chrome()
    if chrome_path:
        print(f"Found Chrome at: {chrome_path}")
        return "chrome", chrome_path

    # Finally try Edge
    edge_path = find_installed_edge()
    if edge_path:
        print(f"Found Edge at: {edge_path}")
        return "edge", edge_path

    # If no browser is found, raise an exception
    raise Exception("No supported browser (Firefox, Chrome, or Edge) found on the system.")

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
    parser.add_argument("--browser", choices=["firefox", "chrome", "edge"], help="Specify which browser to use (default: auto-detect)")
    args = parser.parse_args()

    print("Starting the Microsoft Rewards points scraper.")
    print("This script will use an installed browser (Firefox, Chrome, or Edge) on your system.")

    try:
        # Set up the browser based on user preference or auto-detection
        if args.browser:
            browser_type = args.browser
            if args.browser == "firefox":
                browser_path = find_installed_firefox()
            elif args.browser == "chrome":
                browser_path = find_installed_chrome()
            elif args.browser == "edge":
                browser_path = find_installed_edge()
            
            if not browser_path:
                raise Exception(f"{args.browser} not found on the system.")
        else:
            browser_type, browser_path = setup_browser()

        if browser_type == "firefox":
            options = FirefoxOptions()
            options.binary_location = browser_path
            if args.private:
                options.add_argument("-private-window")  # Firefox uses -private-window for private browsing
            else:
                profile_path = os.path.join(os.getcwd(), 'firefox_persistent_profile')
                if not os.path.exists(profile_path):
                    os.makedirs(profile_path)
                options.add_argument("-profile")
                options.add_argument(profile_path)

            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
        elif browser_type == "chrome":
            options = ChromeOptions()
            options.binary_location = browser_path
            if args.private:
                options.add_argument("--incognito")
            else:
                user_data_dir = os.path.join(os.getcwd(), 'chrome_persistent_profile')
                if not os.path.exists(user_data_dir):
                    os.makedirs(user_data_dir)
                options.add_argument(f"--user-data-dir={user_data_dir}")

            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        elif browser_type == "edge":
            options = EdgeOptions()
            options.binary_location = browser_path
            if args.private:
                options.add_argument("--inprivate")
            else:
                user_data_dir = os.path.join(os.getcwd(), 'edge_persistent_profile')
                if not os.path.exists(user_data_dir):
                    os.makedirs(user_data_dir)
                options.add_argument(f"--user-data-dir={user_data_dir}")

            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
        else:
            raise Exception(f"Unsupported browser type: {browser_type}")

        wait = WebDriverWait(driver, 10)
    except Exception as e:
        print(f"Error setting up the driver: {e}")
        return

    driver.get("https://www.bing.com")
    print("\n>>> The browser window has opened. <<<")
    input("Please ensure you are logged in to your Microsoft account, then press Enter here to continue...")

    main_window = driver.current_window_handle
    print("Loading search terms...")
    search_chains = load_search_terms()
    print(f"Loaded {len(search_chains)} search chains")
    
    searches = []
    while len(searches) < 33:
        searches.extend(random.choice(search_chains))

    print(f"Performing {len(searches)} searches.")

    for i, search_term in enumerate(searches):
        try:
            # Check if main window is still available, if not, try to find a valid window
            try:
                driver.switch_to.window(main_window)
            except:
                # If main window is not available, use the current window or first available
                if len(driver.window_handles) > 0:
                    main_window = driver.window_handles[0]
                    driver.switch_to.window(main_window)
                else:
                    print("No windows available, stopping execution.")
                    break
            
            driver.execute_script("window.open('');")
            # Get the new window handle (last in the list)
            new_window_handle = driver.window_handles[-1]
            driver.switch_to.window(new_window_handle)
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

            # Close current window and return to main window
            driver.close()
            
            # Switch back to main window, but validate it exists first
            if main_window in driver.window_handles:
                driver.switch_to.window(main_window)
            elif len(driver.window_handles) > 0:
                # If main window doesn't exist, use the first available window as main
                main_window = driver.window_handles[0]
                driver.switch_to.window(main_window)
            else:
                print("No windows available after closing search window.")
                break

        except Exception as e:
            print(f"An error occurred during search {i + 1}: {e}")
            # Attempt to recover by checking for available windows
            try:
                if len(driver.window_handles) > 0:
                    # Check if main window still exists, otherwise use first available
                    if main_window in driver.window_handles:
                        driver.switch_to.window(main_window)
                    else:
                        main_window = driver.window_handles[0]
                        driver.switch_to.window(main_window)
                else:
                    print("No windows available to recover to.")
                    break
            except:
                print("Could not switch to any window, stopping execution.")
                break

    print("All searches completed.")

    print("Opening Microsoft Rewards dashboard...")
    driver.get("https://rewards.bing.com/")
    # driver.quit()

if __name__ == "__main__":
    main()
