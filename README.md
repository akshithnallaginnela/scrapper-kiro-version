# Organic Products Web Scraper

A Python-based web scraping system that identifies and ranks the top 5 trending organic products globally by aggregating data from multiple sources including B2C platforms, B2B marketplaces, specialized organic product websites, and social media platforms.

## Quick Start

**New to the scraper?** See [QUICK_START.md](QUICK_START.md) for a 5-minute setup guide.

**Experienced user?** Jump to [Usage](#usage) or [Configuration](#configuration).

## Features

- **Multi-Source Data Collection**: Scrapes data from B2C platforms (Amazon, Flipkart), B2B marketplaces, organic product websites, and social media
- **Hybrid Scraping Approach**: Uses BeautifulSoup for static HTML and Selenium for JavaScript-rendered content
- **Trend Analysis**: Calculates trending scores based on mention frequency, recency, and source diversity
- **Robust Error Handling**: Continues operating despite individual source failures with retry logic and exponential backoff
- **Flexible Output**: Generates results in both JSON and CSV formats with metadata
- **Configurable**: External configuration files for easy customization without code changes

## Requirements

- Python 3.8 or higher
- Chrome or Firefox browser (for Selenium)
- ChromeDriver or GeckoDriver (matching your browser version)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/organic-products-scraper.git
cd organic-products-scraper
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Verify dependencies

Before installing, you can verify your system has all required dependencies:

```bash
python check_dependencies.py
```

On Unix-like systems (Linux/macOS), you can also make it executable:

```bash
chmod +x check_dependencies.py
./check_dependencies.py
```

This script will check:
- Python version (3.8+)
- Required Python libraries
- WebDriver availability (ChromeDriver/GeckoDriver)
- Display clear error messages for missing dependencies

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

Or install the package in development mode:

```bash
pip install -e .
```

### 5. Install WebDriver

**For Chrome:**
- Download ChromeDriver from https://chromedriver.chromium.org/
- Ensure it matches your Chrome browser version
- Add ChromeDriver to your system PATH

**For Firefox:**
- Download GeckoDriver from https://github.com/mozilla/geckodriver/releases
- Add GeckoDriver to your system PATH

**Verify installation:**
```bash
python check_dependencies.py
```

This will confirm all dependencies are properly installed and configured.

## Usage

### Basic Usage

Run the scraper with default configuration:

```bash
python -m src.main
```

Or run directly:

```bash
python src/main.py
```

### With Custom Configuration

Specify a custom configuration file (JSON or YAML):

```bash
python -m src.main --config config/custom_config.yaml
```

Or:

```bash
python src/main.py --config config/scraper_config.json
```

### Command Line Options

```bash
python -m src.main --help
```

Options:
- `--config`, `-c`: Path to configuration file (JSON or YAML)

### How It Works

The main orchestrator coordinates all components in the following workflow:

1. **Configuration Loading**: Loads settings from config file or uses defaults
2. **Logging Initialization**: Sets up dual output (console + rotating file)
3. **Component Initialization**: Creates all scraper components
4. **Source Scraping**: Scrapes all configured sources with retry logic
5. **Product Extraction**: Extracts structured product data from HTML
6. **Data Aggregation**: Combines and deduplicates products from all sources
7. **Trend Analysis**: Calculates trending scores and ranks products
8. **Output Generation**: Creates JSON and CSV files with results
9. **Graceful Cleanup**: Closes all resources and logs summary

The scraper will:
- Continue operating if individual sources fail
- Raise `InsufficientDataException` if fewer than 2 sources succeed
- Handle keyboard interrupts gracefully
- Track scraping duration and metadata
- Log all activities with timestamps

### Configuration

The scraper uses configuration files to define data sources and behavior. Configuration files support both JSON and YAML formats.

#### Quick Start

Use the provided default configuration files:

```bash
# Use JSON configuration
python -m src.main --config config/config.json

# Use YAML configuration
python -m src.main --config config/config.yaml
```

#### Configuration Files

The `config/` directory contains:

- **`config.json`** - Default JSON configuration with 3 sources (Amazon, Flipkart, IndiaMART)
- **`config.yaml`** - Default YAML configuration (same sources)
- **`config.example.json`** - Extended example with 5 sources including B2B sites
- **`config.example.yaml`** - Extended YAML example
- **`CONFIG_GUIDE.md`** - Complete configuration documentation
- **`CSS_SELECTORS_REFERENCE.md`** - CSS selectors for 10+ platforms

#### Configuration Options

Key configuration options:

| Option | Default | Description |
|--------|---------|-------------|
| `sources` | [] | Array of data sources to scrape |
| `timeout` | 30 | Request timeout in seconds |
| `retry_attempts` | 3 | Number of retry attempts |
| `output_directory` | `./output` | Output directory path |
| `browser_type` | `chrome` | Browser for Selenium (`chrome` or `firefox`) |
| `headless` | `true` | Run browser in headless mode |
| `request_delay_min` | 1.0 | Minimum delay between requests (seconds) |
| `request_delay_max` | 3.0 | Maximum delay between requests (seconds) |
| `max_concurrent_requests` | 5 | Maximum concurrent connections |
| `log_level` | `INFO` | Logging level |

#### Example Configuration

```yaml
# config/custom_config.yaml
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
  
  - name: "IndiaMART B2B"
    url: "https://www.indiamart.com/impcat/organic-products.html"
    type: "beautifulsoup"
    selectors:
      container: ".lst"
      name: ".pnm"
      price: ".prc"
      link: ".pnm a"
      image: ".pimg img"

timeout: 30
retry_attempts: 3
output_directory: "./output"
browser_type: "chrome"
headless: true
log_level: "INFO"
```

#### Adding New Sources

To add a new data source:

1. Inspect the target website's HTML structure using browser DevTools
2. Identify CSS selectors for product container, name, price, link, and image
3. Add source configuration to your config file
4. Choose scraper type: `"beautifulsoup"` (static HTML) or `"selenium"` (JavaScript-rendered)
5. Test with a small sample first

**See `config/CSS_SELECTORS_REFERENCE.md` for selector examples for 10+ platforms including:**
- B2C: Amazon, Flipkart, eBay, Walmart
- B2B: IndiaMART, TradeIndia, Alibaba, Made-in-China
- Organic Sites: Organic India, Thrive Market, iHerb

**See `config/CONFIG_GUIDE.md` for complete configuration documentation.**

### Output

The scraper generates two output files in the `output/` directory:

- `trending_products_YYYY-MM-DD_HH-MM-SS.json` - JSON format with full metadata
- `trending_products_YYYY-MM-DD_HH-MM-SS.csv` - CSV format for spreadsheet analysis

**Example JSON output:**
```json
{
  "metadata": {
    "collection_timestamp": "2024-01-15T10:30:00",
    "total_sources_configured": 5,
    "sources_successfully_scraped": ["Amazon", "Flipkart"],
    "sources_failed": ["Source3"],
    "total_products_found": 47,
    "top_products_count": 5,
    "scraping_duration_seconds": 45.2
  },
  "products": [
    {
      "name": "Organic Coconut Oil",
      "price": "$12.99",
      "source": "Amazon",
      "link": "https://amazon.com/...",
      "image_url": "https://...",
      "mentions": 3,
      "trending_score": 0.87
    }
  ]
}
```

See [examples/](examples/) directory for complete sample output files.

## Error Codes and Exit Codes

The scraper uses standard Unix exit codes:

| Exit Code | Status | Description |
|-----------|--------|-------------|
| 0 | Success | Scraping completed successfully |
| 1 | Failure | Scraping failed (see error message) |

**Common errors:**

- **InsufficientDataException:** Fewer than 2 sources succeeded (exit code 1)
- **HTTP 403 Forbidden:** Website blocking requests (warning, continues)
- **HTTP 429 Too Many Requests:** Rate limit exceeded (warning, continues)
- **CAPTCHA detected:** CAPTCHA verification required (warning, continues)
- **Timeout errors:** Request or element wait timeout (warning, continues)

For complete error reference, see [ERROR_CODES.md](ERROR_CODES.md)

**Check exit code in scripts:**
```bash
python -m src.main
if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed"
fi
```

## Testing

### Run all tests

```bash
pytest
```

### Run with coverage report

```bash
pytest --cov=src --cov-report=html
```

### Run property-based tests only

```bash
pytest -k "property" -v
```

### Run specific test file

```bash
pytest tests/test_product_extractor.py -v
```

### Test Mode

The scraper includes a test mode that uses cached HTML responses instead of making live HTTP requests. This provides:

- **Faster test execution**: No network delays
- **Reproducible tests**: Same HTML every time
- **No external dependencies**: Tests run offline
- **Development convenience**: Test extraction logic without hitting real websites

**Enable test mode** by setting `test_mode: true` in your configuration:

```json
{
  "test_mode": true,
  "test_data_directory": "./test_data",
  "sources": [...]
}
```

**Run with test mode configuration:**

```bash
python -m src.main --config config/config.test_mode.json
```

**Generate cached responses:**

```bash
python regenerate_cache.py
```

This will scrape all configured sources and save the HTML to the `test_data/` directory for future test runs.

See `config/CONFIG_GUIDE.md` for complete test mode documentation.

## Project Structure

```
organic-products-scraper/
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── config_manager.py         # Configuration handling
│   ├── source_manager.py         # Source connection management
│   ├── beautifulsoup_scraper.py  # Static HTML scraping
│   ├── selenium_scraper.py       # Dynamic content scraping
│   ├── product_extractor.py      # Product data extraction
│   ├── data_aggregator.py        # Data aggregation and deduplication
│   ├── trend_analyzer.py         # Trend analysis and ranking
│   ├── output_formatter.py       # Output file generation
│   └── models.py                 # Data models
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_product_extractor.py
│   ├── test_trend_analyzer.py
│   ├── test_data_aggregator.py
│   └── property_tests/           # Property-based tests
├── output/                       # Generated output files
├── config/                       # Configuration files
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Package configuration
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Development

### Install development dependencies

```bash
pip install -e ".[test]"
```

### Code style

This project follows PEP 8 style guidelines. Format code using:

```bash
black src/ tests/
```

### Adding new data sources

1. Add source configuration to `config/scraper_config.yaml`
2. Specify CSS selectors for product extraction
3. Choose scraper type: "beautifulsoup" or "selenium"
4. Test with a small sample first

## Troubleshooting

For common issues and solutions, see the comprehensive troubleshooting guide:

**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Complete troubleshooting guide covering:
- Installation issues
- Configuration problems
- Scraping errors
- Performance issues
- Output problems
- Debugging tips

### Quick Solutions

**Dependency Issues:**
```bash
python check_dependencies.py
```

**WebDriver not found:**
- Install ChromeDriver/GeckoDriver and add to PATH
- Verify driver version matches browser version

**CAPTCHA blocking:**
- Increase request delays: `request_delay_min: 3.0`
- Use headless mode: `headless: true`

**Timeout errors:**
- Increase timeout: `timeout: 60`
- Check network connectivity

**Memory issues:**
- Reduce concurrent requests: `max_concurrent_requests: 3`
- Enable headless mode

For detailed solutions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Documentation

**Complete Documentation Index:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Find any documentation quickly

### Core Documentation

- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide for new users
- **[README.md](README.md)** - This file, main documentation and quick start guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide for common issues
- **[ERROR_CODES.md](ERROR_CODES.md)** - Complete reference for error codes and exit codes

### Configuration Documentation

- **[config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md)** - Complete configuration options guide
- **[config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md)** - CSS selectors for 10+ platforms
- **[config/README.md](config/README.md)** - Configuration files overview

### Examples

- **[examples/README.md](examples/README.md)** - Usage examples and sample configurations
- **[examples/example_output.json](examples/example_output.json)** - Sample JSON output
- **[examples/example_output.csv](examples/example_output.csv)** - Sample CSV output

### Performance

- **[PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)** - Performance optimization guide

## Disclaimer

This tool is for educational and research purposes. Always respect website terms of service and robots.txt files. Implement appropriate rate limiting and obtain permission before scraping commercial websites.
