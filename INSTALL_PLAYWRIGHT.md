# Installing Playwright Browsers

Playwright is already integrated into the code. You just need to install the browser binaries.

## Quick Install

Run this command in your terminal:

```bash
uv run playwright install chromium
```

This will download the Chromium browser (~170MB) that Playwright uses to render pages.

## What This Does

- Downloads Chromium browser binaries
- Stores them in Playwright's cache directory
- Allows the app to use browser automation when sites block regular HTTP requests

## After Installation

Once installed, the app will automatically:
1. Try regular HTTP requests first (fast)
2. If blocked (403 error), automatically use Playwright (slower but more reliable)
3. Extract streams from the rendered page

## Testing

After installation, you can test it with:
```bash
uv run python test_playwright.py
```

Or just use the app normally - it will automatically use Playwright when needed!

