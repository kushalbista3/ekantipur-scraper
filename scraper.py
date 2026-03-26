import json
import os
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# Target pages and output file (kept configurable for easy changes)
ENTERTAINMENT_URL = "https://ekantipur.com/entertainment"
HOMEPAGE_URL = "https://ekantipur.com/"
OUTPUT_PATH = "output.json"


# -----------------------------------------------------------------------------
# Extraction Functions
# -----------------------------------------------------------------------------
def extract_entertainment_news(page: Any, limit: int = 5) -> list[dict]:
    """
    Extract top entertainment news articles.

    Approach:
    - Use semantic selectors (h2, img, p) 
    - Extract data using index-based mapping (nth(i)) for predictability
    - Handle missing elements safely using try/except
    - Support lazy-loaded images (src OR data-src)
    """
    try:
        # Load page and wait until main content is available
        page.goto(ENTERTAINMENT_URL, wait_until="domcontentloaded")
        page.wait_for_selector("div.category-inner-wrapper")

        # Select all relevant elements
        titles = page.locator("div.category-inner-wrapper h2")
        images = page.locator("div.category-inner-wrapper figure img")
        authors = page.locator("div.category-inner-wrapper .author-name p")

        items = []

        # Iterate using index-based access to keep mapping simple and consistent
        for i in range(min(limit, titles.count())):

            # --- Title extraction ---
            # If element is missing or fails, fallback to empty string
            try:
                title = titles.nth(i).inner_text().strip()
            except:
                title = ""

            # --- Image extraction ---
            # Some images are lazy-loaded:
            # - 'src' may be empty
            # - actual URL may be in 'data-src'
            # So we check both and use whichever exists
            try:
                img = images.nth(i)
                src = img.get_attribute("src")
                data_src = img.get_attribute("data-src")
                raw = src or data_src

                # Convert relative URLs to absolute URLs
                if raw:
                    if raw.startswith("http"):
                        image_url = raw
                    elif raw.startswith("//"):
                        image_url = "https:" + raw
                    else:
                        image_url = HOMEPAGE_URL.rstrip("/") + "/" + raw.lstrip("/")
                else:
                    image_url = None
            except:
                image_url = None

            # --- Author extraction ---
            # If missing, return None instead of empty string
            try:
                author = authors.nth(i).inner_text().strip()
            except:
                author = None

            items.append(
                {
                    "title": title,
                    "image_url": image_url,
                    "category": "मनोरञ्जन",  # Fixed category as per requirement
                    "author": author,
                }
            )

        # Ensure exactly 'limit' items (requirement: must return 5 articles)
        # If fewer items found, pad with empty placeholders
        while len(items) < limit:
            items.append(
                {
                    "title": "",
                    "image_url": None,
                    "category": "मनोरञ्जन",
                    "author": None,
                }
            )

        return items

    except Exception as e:
        # If entire extraction fails, return safe fallback structure
        print(f"entertainment extraction failed: {e}")
        return [
            {
                "title": "",
                "image_url": None,
                "category": "मनोरञ्जन",
                "author": None,
            }
            for _ in range(limit)
        ]


def extract_cartoon_of_the_day(page: Any) -> dict:
    """
    Extract 'Cartoon of the Day' from homepage.

    Approach:
    - Locate section using container selector
    - Extract image and use its 'alt' attribute for title/author
    - Handle lazy-loaded images similar to news extraction
    """
    try:
        # Load homepage and wait for section to appear
        page.goto(HOMEPAGE_URL, wait_until="domcontentloaded")
        page.wait_for_selector("div.section-news")

        section = page.locator("div.section-news").first
        img = section.locator("a:has(img) img").first

        # --- Title and author ---
        # Site stores caption info inside image 'alt'
        try:
            title = img.get_attribute("alt")
        except:
            title = None

        # Author not separately available → reuse title (as per observed structure)
        author = title

        # --- Image extraction ---
        # Same lazy-loading handling as above
        try:
            src = img.get_attribute("src")
            data_src = img.get_attribute("data-src")
            raw = src or data_src

            if raw:
                if raw.startswith("http"):
                    image_url = raw
                elif raw.startswith("//"):
                    image_url = "https:" + raw
                else:
                    image_url = HOMEPAGE_URL.rstrip("/") + "/" + raw.lstrip("/")
            else:
                image_url = None
        except:
            image_url = None

        return {
            "title": title,
            "image_url": image_url,
            "author": author,
        }

    except Exception as e:
        # Fallback if extraction fails
        print(f"cartoon extraction failed: {e}")
        return {"title": None, "image_url": None, "author": None}


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    """
    Main execution flow:
    1. Launch browser (headless configurable via environment variable)
    2. Run both extraction functions
    3. Save results in required JSON format
    """
    output = {
        "entertainment_news": [],
        "cartoon_of_the_day": {},
    }

    with sync_playwright() as p:
        # Allow switching between headless/headed mode via env variable
        headless = os.getenv("SCRAPER_HEADLESS") == "1"
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        # Run extraction tasks
        output["entertainment_news"] = extract_entertainment_news(page, 5)
        output["cartoon_of_the_day"] = extract_cartoon_of_the_day(page)

        browser.close()

    # Save output as formatted JSON (UTF-8 to support Nepali text)
    Path(OUTPUT_PATH).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()