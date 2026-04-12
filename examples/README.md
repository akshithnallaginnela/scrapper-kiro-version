# Examples Directory

This directory contains example output files and usage examples for the Organic Products Web Scraper.

## Contents

- [Sample Output Files](#sample-output-files)
- [Usage Examples](#usage-examples)
- [Configuration Examples](#configuration-examples)

---

## Sample Output Files

### example_output.json

Complete JSON output example showing:
- Metadata with collection timestamp and source statistics
- Top 5 trending products with all fields
- Product mentions and trending scores
- Source diversity information

**File:** `example_output.json`

### example_output.csv

CSV output example showing:
- All product fields in tabular format
- Easy to import into spreadsheet applications
- Suitable for data analysis and reporting

**File:** `example_output.csv`

---

## Usage Examples

### Basic Usage

Run with default configuration:

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

### Custom Configuration

Run with custom configuration file:

```bash
python -m src.main --config config/config.example.yaml
```

### Multiple Runs

Run scraper multiple times with different configurations:

```bash
# Quick scrape with 3 sources
python -m src.main --config config/config.json

# Comprehensive scrape with 8 sources
python -m src.main --config config/config.comprehensive.json

# Test mode with cached data
python -m src.main --config config/config.test_mode.json
```

### Automated Scheduling

Schedule scraper to run daily using cron (Linux/Mac):

```bash
# Edit crontab
crontab -e

# Add line to run daily at 9 AM
0 9 * * * cd /path/to/scraper && /path/to/venv/bin/python -m src.main --config config/config.yaml >> /path/to/logs/cron.log 2>&1
```

Using Windows Task Scheduler:

```batch
# Create batch file: run_scraper.bat
@echo off
cd C:\path\to\scraper
C:\path\to\venv\Scripts\python.exe -m src.main --config config\config.yaml
```

Then schedule in Task Scheduler.

### Error Handling in Scripts

Bash script with error handling:

```bash
#!/bin/bash

CONFIG="config/config.yaml"
LOG_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create log directory
mkdir -p "$LOG_DIR"

# Run scraper
python -m src.main --config "$CONFIG" > "$LOG_DIR/scraper_$TIMESTAMP.log" 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "Scraping succeeded at $(date)" >> "$LOG_DIR/success.log"
else
    echo "Scraping failed at $(date)" >> "$LOG_DIR/failure.log"
    # Send alert email
    echo "Scraper failed. Check logs." | mail -s "Scraper Alert" admin@example.com
fi
```

### Python Integration

Use scraper as a library in your Python code:

```python
from src.main import main

# Run scraper programmatically
exit_code = main(config_path="config/config.yaml")

if exit_code == 0:
    print("Scraping succeeded")
    # Process output files
    import json
    with open("output/latest_output.json") as f:
        data = json.load(f)
        products = data["products"]
        print(f"Found {len(products)} trending products")
else:
    print("Scraping failed")
```

### Data Analysis

Analyze output with pandas:

```python
import pandas as pd
import json

# Load JSON output
with open("output/organic_products_2024-01-15_10-30-45.json") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data["products"])

# Analysis
print(f"Total products: {len(df)}")
print(f"Average mentions: {df['mentions'].mean():.2f}")
print(f"Sources: {df['source'].unique()}")

# Top products by mentions
top_by_mentions = df.nlargest(5, 'mentions')
print("\nTop products by mentions:")
print(top_by_mentions[['name', 'mentions', 'source']])

# Price analysis (convert to numeric)
df['price_numeric'] = pd.to_numeric(df['price'].str.replace('[^0-9.]', '', regex=True), errors='coerce')
print(f"\nAverage price: ${df['price_numeric'].mean():.2f}")
```

Load CSV output:

```python
import pandas as pd

# Load CSV
df = pd.read_csv("output/organic_products_2024-01-15_10-30-45.csv")

# Quick statistics
print(df.describe())
print(df['source'].value_counts())
```

---

## Configuration Examples

### Minimal Configuration

Simplest possible configuration:

```json
{
  "sources": [
    {
      "name": "Amazon Organic",
      "url": "https://www.amazon.com/s?k=organic+products",
      "type": "beautifulsoup",
      "selectors": {
        "container": ".s-result-item",
        "name": "h2 .a-text-normal",
        "price": ".a-price-whole",
        "link": "h2 a",
        "image": ".s-image"
      }
    }
  ]
}
```

### Production Configuration

Optimized for reliability:

```yaml
sources:
  - name: "Amazon Organic Products"
    url: "https://www.amazon.com/s?k=organic+products"
    type: "beautifulsoup"
    selectors:
      container: ".s-result-item"
      name: "h2 .a-text-normal"
      price: ".a-price-whole"
      link: "h2 a"
      image: ".s-image"
  
  - name: "Flipkart Organic"
    url: "https://www.flipkart.com/search?q=organic+products"
    type: "selenium"
    selectors:
      container: "._1AtVbE"
      name: "._4rR01T"
      price: "._30jeq3"
      link: "._1fQZEK"
      image: "._396cs4"
  
  - name: "IndiaMART B2B"
    url: "https://www.indiamart.com/impcat/organic-products.html"
    type: "beautifulsoup"
    selectors:
      container: ".lst"
      name: ".pnm"
      price: ".prc"
      link: ".pnm a"
      image: ".pimg img"

# Reliable settings
timeout: 60
retry_attempts: 5
request_delay_min: 2.0
request_delay_max: 4.0
max_concurrent_requests: 3

# Output settings
output_directory: "./output"
log_level: "INFO"
log_file: "scraper.log"
max_log_size_mb: 20

# Browser settings
browser_type: "chrome"
headless: true
```

### Development Configuration

Optimized for testing:

```yaml
sources:
  - name: "Test Source"
    url: "https://example.com/products"
    type: "beautifulsoup"
    selectors:
      container: ".product"
      name: ".name"
      price: ".price"
      link: "a"
      image: "img"

# Fast settings for testing
timeout: 10
retry_attempts: 1
request_delay_min: 0.5
request_delay_max: 1.0
max_concurrent_requests: 1

# Debug output
output_directory: "./test_output"
log_level: "DEBUG"
log_file: "test.log"

# Test mode
test_mode: true
test_data_directory: "./test_data"
```

---

## Output File Examples

### JSON Output Structure

```json
{
  "metadata": {
    "collection_timestamp": "2024-01-15T10:30:00",
    "total_sources_configured": 3,
    "sources_successfully_scraped": ["Amazon", "Flipkart", "IndiaMART"],
    "sources_failed": [],
    "total_products_found": 47,
    "top_products_count": 5,
    "scraping_duration_seconds": 45.2,
    "version": "1.0.0"
  },
  "products": [
    {
      "name": "Organic Coconut Oil - 500ml",
      "price": "$12.99",
      "source": "Amazon",
      "link": "https://amazon.com/dp/B08X123456",
      "image_url": "https://images.amazon.com/...",
      "timestamp": "2024-01-15T10:30:00",
      "mentions": 3,
      "sources_list": ["Amazon", "Flipkart", "IndiaMART"]
    },
    {
      "name": "Organic Chia Seeds - 1kg",
      "price": "₹399",
      "source": "Flipkart",
      "link": "https://flipkart.com/...",
      "image_url": "https://images.flipkart.com/...",
      "timestamp": "2024-01-15T10:30:00",
      "mentions": 2,
      "sources_list": ["Flipkart", "IndiaMART"]
    }
  ]
}
```

### CSV Output Structure

```csv
name,price,source,link,image_url,timestamp,mentions,sources_list
Organic Coconut Oil - 500ml,$12.99,Amazon,https://amazon.com/dp/B08X123456,https://images.amazon.com/...,2024-01-15T10:30:00,3,"Amazon, Flipkart, IndiaMART"
Organic Chia Seeds - 1kg,₹399,Flipkart,https://flipkart.com/...,https://images.flipkart.com/...,2024-01-15T10:30:00,2,"Flipkart, IndiaMART"
```

---

## Common Use Cases

### 1. Daily Market Research

**Goal:** Track trending organic products daily

**Configuration:**
- 5-8 diverse sources
- Moderate delays (2-4 seconds)
- Reliable settings (high timeout, retries)

**Automation:**
- Schedule daily at 9 AM
- Save outputs with date stamps
- Compare trends over time

### 2. Quick Product Check

**Goal:** Quick check of current trends

**Configuration:**
- 2-3 fast sources
- Minimal delays (0.5-1 second)
- BeautifulSoup only

**Usage:**
```bash
python -m src.main --config config/quick_check.yaml
```

### 3. Comprehensive Analysis

**Goal:** Deep market analysis with maximum data

**Configuration:**
- 8+ sources (B2C, B2B, organic sites)
- Conservative delays (3-5 seconds)
- High reliability settings

**Post-processing:**
- Analyze with pandas
- Generate reports
- Track historical trends

### 4. Development Testing

**Goal:** Test selector changes without hitting live sites

**Configuration:**
- Test mode enabled
- Cached responses
- Debug logging

**Usage:**
```bash
python -m src.main --config config/config.test_mode.json
```

---

## Tips and Best Practices

### 1. Start Small

Begin with 2-3 sources and verify they work before adding more.

### 2. Monitor Logs

Always check `scraper.log` for issues:
```bash
tail -f scraper.log
```

### 3. Use Test Mode

Develop and test selectors using test mode to avoid hitting live sites repeatedly.

### 4. Respect Rate Limits

Use appropriate delays (2-4 seconds) to avoid being blocked.

### 5. Handle Failures Gracefully

The scraper continues if individual sources fail. Check logs to identify and fix issues.

### 6. Version Control

Track configuration changes in git to maintain history of selector updates.

### 7. Backup Outputs

Save output files regularly for historical analysis:
```bash
cp output/organic_products_*.json archive/
```

### 8. Automate Wisely

Schedule scraping during off-peak hours to reduce load on target websites.

---

## Additional Resources

- **Main Documentation:** `../README.md`
- **Configuration Guide:** `../config/CONFIG_GUIDE.md`
- **CSS Selectors Reference:** `../config/CSS_SELECTORS_REFERENCE.md`
- **Troubleshooting:** `../TROUBLESHOOTING.md`
- **Error Codes:** `../ERROR_CODES.md`

