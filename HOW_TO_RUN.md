# How to Run the Organic Products Web Scraper

## Quick Start (Recommended)

**For immediate results, use the test mode:**

1. Double-click `run_scraper.bat`
2. Wait a few seconds
3. Check the `output` folder for results

This uses cached data and works instantly without any issues.

## Why Live Scraping Fails

When you tried `run_scraper_live.bat`, it failed because:

1. **Amazon** - Blocking requests (503 errors)
2. **Flipkart** - CAPTCHA detection
3. **IndiaMART** - URL not found (404)

This is **completely normal** for web scraping. Major e-commerce sites actively block automated scraping to protect their data.

## Solutions for Live Scraping

### Option 1: Use Test Mode (Easiest)
```bash
run_scraper.bat
```
- Uses cached HTML responses
- Works instantly
- Perfect for testing and development
- Shows you how the scraper works

### Option 2: Use Alternative Sources
Some websites are more scraper-friendly. Try:
- **eBay** - Generally more permissive
- **iHerb** - Organic products specialist
- **Smaller organic stores** - Less strict anti-bot measures

### Option 3: Advanced Setup (For Real Scraping)

To scrape real websites successfully, you need:

1. **Residential Proxies** - Rotate IP addresses
   - Services: BrightData, Oxylabs, SmartProxy
   - Cost: $50-200/month

2. **Browser Automation** - Use Selenium with real browser
   - Slower but more reliable
   - Can handle JavaScript-rendered pages
   - Better CAPTCHA avoidance

3. **Rate Limiting** - Slow down requests
   - 5-10 seconds between requests
   - Respect robots.txt
   - Scrape during off-peak hours

4. **User Agent Rotation** - Appear as different browsers
   - Randomize user agents
   - Mimic real browser behavior

5. **CAPTCHA Solving Services** - Handle CAPTCHAs
   - Services: 2Captcha, Anti-Captcha
   - Cost: $1-3 per 1000 CAPTCHAs

## What You Can Do Right Now

### 1. Use Test Mode (Works Perfectly)
```bash
run_scraper.bat
```

### 2. View the Results
```bash
view_results.bat
```

### 3. Analyze the Data
The output files contain:
- Product names
- Prices
- Sources
- Images
- Trending scores

## Understanding the Output

**JSON Output** (`output/organic_products_*.json`):
```json
{
  "metadata": {
    "collection_timestamp": "2026-04-12T19:48:42",
    "total_products_found": 14,
    "top_products_count": 5
  },
  "products": [
    {
      "name": "Organic Chia Seeds - 500g",
      "price": "₹399",
      "mentions": 2,
      "sources_list": ["Flipkart Organic"]
    }
  ]
}
```

**CSV Output** (`output/organic_products_*.csv`):
- Open in Excel or Google Sheets
- Easy to analyze and filter
- Perfect for reports

## For Production Use

If you need to scrape real websites regularly:

1. **Budget for proxies** ($50-200/month)
2. **Use Selenium** for JavaScript sites
3. **Implement delays** (5-10 seconds)
4. **Monitor for blocks** and adjust
5. **Have backup sources** in case one fails
6. **Consider APIs** if available (more reliable)

## Legal Considerations

- **Check Terms of Service** - Some sites prohibit scraping
- **Respect robots.txt** - Follow website rules
- **Rate limit** - Don't overload servers
- **Personal use only** - Commercial use may require permission

## Recommended Approach

**For Learning/Testing:**
- Use `run_scraper.bat` (test mode)
- Experiment with the code
- Understand how scraping works

**For Real Data:**
- Start with smaller, scraper-friendly sites
- Use proxies and rate limiting
- Consider paid APIs as alternative
- Budget for infrastructure

## Summary

✅ **Test mode works perfectly** - Use this for now
❌ **Live scraping is blocked** - Expected behavior
💡 **Need proxies for production** - Requires investment

**Bottom line:** Use `run_scraper.bat` for immediate results. For production scraping, you'll need additional infrastructure (proxies, CAPTCHA solvers, etc.).

## Questions?

- See `TROUBLESHOOTING.md` for common issues
- See `README.md` for full documentation
- See `ERROR_CODES.md` for error explanations
