# Joybuy Scraper Guide

## Overview

Scrapes product categories and items from joybuy.de using Playwright with Chrome CDP connection. joybuy.de blocks server-side requests (403), so we connect to a real Chrome browser on Windows.

## Prerequisites

- Windows with Chrome installed
- Python 3.11+
- Playwright: `pip install playwright`

## Step 1: Start Chrome with debug port

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

Leave this Chrome window open.

## Step 2: Run scraper

Double-click `scrape.bat` or run:

```powershell
python scrape_joybuy.py
```

## What it does

1. Connects to Chrome via CDP (http://localhost:9222)
2. Opens joybuy.de homepage
3. Auto-discovers category links (/minihome/ paths)
4. Visits each category and extracts product names, prices, image URLs
5. Writes products to PostgreSQL (db-node:5432, shop database)

## Output

- ~1000+ products per run
- Tables: products (name, category, price, image, stock)
- Old data is cleared before new scrape

## Files

| File | Purpose |
|------|---------|
| scrape_joybuy.py | Main scraper script |
| scrape.bat | One-click launcher (starts Chrome + runs script) |

## Notes

- joybuy.de returns 403 for headless/automated browsers, hence CDP approach
- Run from Windows, not from Linux VMs
- Products images use remote URLs from joy-sourcing.com
- Categories are auto-discovered, not hardcoded
