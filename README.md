# Ekantipur Scraper - Audio Bee Web Scraping Intern Practical Test

This project is a complete Playwright-based web scraper built for the Audio Bee Web Scraping Intern practical assessment.

It extracts:

- Top 5 entertainment news articles from the Entertainment section
- Cartoon of the Day from the homepage

All data is scraped live with no hardcoding and saved in the exact JSON structure required by the test.

## Features

- Clean and minimal code using Playwright Sync API
- Robust error handling for missing elements
- Proper handling of relative image URLs (src / data-src)
- Always returns exactly 5 entertainment articles
- Supports Nepali text (UTF-8)
- Simple and readable structure

## Approach Summary

Selectors were found manually using Chrome DevTools (F12):
Entertainment cards → div.category-inner-wrapper
Title → h2, Image → figure img, Author → .author-class p
Cartoon → div.section-news + a:has(img) img (alt attribute)

Built using Cursor IDE with exactly 3 focused prompts (see prompts.txt).
Followed Playwright best practices: proper waits, safe element access, and clean JSON output.

## Output Format

  
The generated output.json follows the exact structure specified in the test:  
{  
  "entertainment_news": [ ... 5 articles ... ],  
  "cartoon_of_the_day": { ... }  
}