# Quick Start Guide

Get up and running with the Organic Products Web Scraper in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser
- Internet connection

## Installation (2 minutes)

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/organic-products-scraper.git
cd organic-products-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install WebDriver

**For Chrome:**
```bash
# Download from https://chromedriver.chromium.org/
# Add to PATH or place in project directory
```

**For Firefox:**
```bash
# Download from https://github.com/mozilla/geckodriver/releases
# Add to PATH or place in project directory
```

### 3. Verify Installation

```bash
python check_dependencies.py
```

You should see:
```
✓ Python version: 3.8+
✓ All required libraries installed
✓ ChromeDriver found
All dependencies satisfied!
```

## First Run (1 minute)

### Run with Default Configuration

```bash
python -m src.main
```

Expected output:
```
Initializing Organic Products Web Scraper...

Scraping completed successfully!
Results saved to:
  - ./output/organic_products_2024-01-15_10-30-45.json
  - ./output/organic_products_2024-01-15_10-30-45.csv
```

### View Results

**JSON output:**
```bash
cat output/organic_products_*.json
```

**CSV output:**
```bash
cat output/organic_products_*.csv
```

Or open in Excel/Google Sheets.

## Configuration (2 minutes)

### Use Example Configuration

```bash
# 3 sources (fast)
python -m src.main --config config/config.json

# 5 sources (balanced)
python -m src.main --config config/config.example.json

# 8 sources (comprehensive)
python -m src.main --config config/config.comprehensive.json
```

### Create Custom Configuration

1. Copy example:
```bash
cp config/config.example.yaml config/my_config.yaml
```

2. Edit `config/my_config.yaml`:
```yaml
sources:
  - name: "Amazon Organic"
    url: "https://www.amazon.com/s?k=organic+products"
    type: "beautifulsoup"
    selectors:
      container: ".s-result-item"
      name: "h2 .a-text-normal"
      price: ".a-price-whole"
      link: "h2 a"
      image: ".s-image"

timeout: 30
retry_attempts: 3
output_directory: "./output"
log_level: "INFO"
```

3. Run with your config:
```bash
python -m src.main --config config/my_config.yaml
```

## Common Tasks

### Check Logs

```bash
tail -f scraper.log
```

### Run in Test Mode

```bash
python -m src.main --config config/config.test_mode.json
```

### Schedule Daily Runs

**Linux/Mac (cron):**
```bash
crontab -e
# Add: 0 9 * * * cd /path/to/scraper && /path/to/venv/bin/python -m src.main
```

**Windows (Task Scheduler):**
Create `run_scraper.bat`:
```batch
@echo off
cd C:\path\to\scraper
C:\path\to\venv\Scripts\python.exe -m src.main
```

## Troubleshooting

### Problem: WebDriver not found

**Solution:**
```bash
python check_dependencies.py
# Follow instructions to install ChromeDriver/GeckoDriver
```

### Problem: HTTP 403 or 429 errors

**Solution:** Increase delays in config:
```yaml
request_delay_min: 3.0
request_delay_max: 5.0
```

### Problem: No products extracted

**Solution:** Verify selectors with browser DevTools:
1. Open target website in browser
2. Right-click product → Inspect Element
3. Test selector in console: `document.querySelectorAll('.your-selector')`
4. Update selectors in config

### Problem: Scraping too slow

**Solution:** Use BeautifulSoup instead of Selenium:
```yaml
type: "beautifulsoup"  # Instead of "selenium"
```

## Next Steps

### Learn More

- **Full Documentation:** [README.md](README.md)
- **Configuration Guide:** [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md)
- **CSS Selectors:** [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Error Codes:** [ERROR_CODES.md](ERROR_CODES.md)
- **Examples:** [examples/README.md](examples/README.md)

### Add More Sources

See [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md) for selectors for:
- Amazon, Flipkart, eBay, Walmart
- IndiaMART, TradeIndia, Alibaba
- Organic India, iHerb, Thrive Market

### Analyze Results

Use pandas for data analysis:
```python
import pandas as pd
df = pd.read_csv("output/organic_products_*.csv")
print(df.describe())
```

### Automate

Set up daily scraping and track trends over time.

## Quick Reference

### Commands

```bash
# Basic run
python -m src.main

# With config
python -m src.main --config config/my_config.yaml

# Check dependencies
python check_dependencies.py

# View logs
tail -f scraper.log

# Run tests
pytest
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `timeout` | 30 | Request timeout (seconds) |
| `retry_attempts` | 3 | Retry attempts |
| `request_delay_min` | 1.0 | Min delay (seconds) |
| `request_delay_max` | 3.0 | Max delay (seconds) |
| `log_level` | INFO | Logging level |
| `browser_type` | chrome | Browser (chrome/firefox) |
| `headless` | true | Headless mode |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Failure |

### File Locations

```
organic-products-scraper/
├── config/              # Configuration files
├── output/              # Output files (JSON, CSV)
├── examples/            # Example outputs
├── scraper.log          # Log file
└── src/                 # Source code
```

## Support

- **Issues:** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Errors:** See [ERROR_CODES.md](ERROR_CODES.md)
- **Examples:** See [examples/README.md](examples/README.md)

---

**You're ready to start scraping!** 🚀

Run your first scrape:
```bash
python -m src.main
```

