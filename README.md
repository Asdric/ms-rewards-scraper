
# MS Rewards Scraper

This script automates the process of earning Microsoft Rewards points by performing Bing searches.

## Features

*   Automatically performs a random number of Bing searches (33+).
*   Uses search chains for more realistic search patterns.
*   Simulates human-like behavior, including typing speed, scrolling, and clicking links.
*   Pauses for the user to solve captchas.
*   Uses a portable version of Firefox to ensure compatibility and avoid conflicts.
*   Keeps the user logged in between sessions by using a persistent profile.
*   Option to use a private window.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd MS-Rewards-Scraper
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Install the dependencies:**
    ```bash
    venv/bin/python -m pip install -r requirements.txt
    ```

## Usage

1.  **Run the script:**
    ```bash
    venv/bin/python points_scraper.py
    ```

2.  **Private Mode:**
    To run the script in a private window (you will need to log in each time), use the `--private` flag:
    ```bash
    venv/bin/python points_scraper.py --private
    ```

3.  **Follow the prompts:**
    *   The first time you run the script, it will download a portable version of Firefox. This may take a few moments.
    *   The script will then open a browser window and ask you to log in to your Microsoft account. After you have logged in, press Enter in the terminal to continue.
    *   If a captcha appears, the script will pause and ask you to solve it. After you have solved the captcha, press Enter in the terminal to continue.

## Troubleshooting

*   **Captcha Issues:** If you are having trouble with captchas, make sure you are solving them correctly in the browser window before pressing Enter in the terminal.
*   **Login Issues:** If you are not staying logged in, make sure you are not using the `--private` flag.
