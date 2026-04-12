# 🌿 Organic Products Web Scraper - Kiro Version

A powerful Python-based web scraping system that identifies and ranks the top 5 trending organic products globally by aggregating data from multiple sources including B2C platforms, B2B marketplaces, and specialized organic product websites.


[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](tests/)

## ✨ Features

- 🔍 **Multi-Source Data Collection** - Scrapes from B2C platforms (Amazon, Flipkart), B2B marketplaces (IndiaMART), and organic product websites
- ⚡ **Hybrid Scraping** - Uses BeautifulSoup for static HTML and Selenium for JavaScript-rendered content
- 📊 **Trend Analysis** - Calculates trending scores based on mention frequency, recency, and source diversity
- 🛡️ **Robust Error Handling** - Continues operating despite individual source failures with retry logic
- 📁 **Flexible Output** - Generates results in both JSON and CSV formats
- ⚙️ **Highly Configurable** - External configuration files for easy customization
- 🧪 **Test Mode** - Uses cached responses for fast testing without hitting live websites
- 📈 **Performance Optimized** - Concurrent requests, connection pooling, DNS caching
- 🧪 **Comprehensive Testing** - 281 tests with 91% code coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser
- ChromeDriver or GeckoDriver

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scrapper-kiro-version.git
cd scrapper-kiro-version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python check_dependencies.py
```

### Run the Scraper

**Windows (Double-click):**
- `run_scraper.bat` - Quick test with cached data (recommended)
- `run_scraper_live.bat` - Scrape real websites (requires proxies)
- `view_results.bat` - View latest results

**Command Line:**
```bash
# Test mode (recommended for first run)
python -m src.main --config config/config.test_mode.json

# Live scraping
python -m src.main --config config/config.json

# Custom configuration
python -m src.main --config config/your_config.yaml
```

### View Results

Results are saved in the `output/` directory:
- `organic_products_YYYY-MM-DD_HH-MM-SS.json` - JSON format
- `organic_products_YYYY-MM-DD_HH-MM-SS.csv` - CSV format

## 📖 Documentation

- **[START_HERE.txt](START_HERE.txt)** - Quick start guide
- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Detailed running instructions
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[ERROR_CODES.md](ERROR_CODES.md)** - Complete error reference
- **[config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md)** - Configuration options
- **[config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md)** - CSS selectors for 10+ platforms

## 🎯 Example Output

```json
{
  "metadata": {
    "collection_timestamp": "2026-04-12T19:48:42",
    "total_sources_configured": 3,
    "sources_successfully_scraped": ["Amazon", "Flipkart", "IndiaMART"],
    "total_products_found": 14,
    "top_products_count": 5
  },
  "products": [
    {
      "name": "Organic Chia Seeds - 500g",
      "price": "₹399",
      "source": "Flipkart Organic",
      "mentions": 2,
      "sources_list": ["Flipkart Organic"]
    }
  ]
}
```

## 🏗️ Architecture

```
┌─────────────────┐
│ Configuration   │
│    Manager      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Source Manager  │◄──────┐
└────────┬────────┘       │
         │                │
    ┌────┴────┐          │
    ▼         ▼          │
┌─────────┐ ┌──────────┐│
│Beautiful│ │ Selenium ││
│  Soup   │ │ Scraper  ││
└────┬────┘ └─────┬────┘│
     │            │     │
     └──────┬─────┘     │
            ▼           │
    ┌───────────────┐   │
    │   Product     │   │
    │  Extractor    │   │
    └───────┬───────┘   │
            │           │
            ▼           │
    ┌───────────────┐   │
    │     Data      │   │
    │  Aggregator   │   │
    └───────┬───────┘   │
            │           │
            ▼           │
    ┌───────────────┐   │
    │    Trend      │   │
    │   Analyzer    │   │
    └───────┬───────┘   │
            │           │
            ▼           │
    ┌───────────────┐   │
    │    Output     │   │
    │   Formatter   │   │
    └───────────────┘   │
                        │
    ┌───────────────┐   │
    │    Logging    │───┘
    │    System     │
    └───────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_product_extractor.py -v
```

**Test Statistics:**
- Total Tests: 281
- Pass Rate: 100%
- Code Coverage: 91%

## ⚙️ Configuration

Create a configuration file (JSON or YAML):

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

timeout: 30
retry_attempts: 3
output_directory: "./output"
log_level: "INFO"
```

See [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md) for all options.

## 🔧 Project Structure

```
scrapper-kiro-version/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── config_manager.py  # Configuration handling
│   ├── source_manager.py  # Source management
│   ├── beautifulsoup_scraper.py
│   ├── selenium_scraper.py
│   ├── product_extractor.py
│   ├── data_aggregator.py
│   ├── trend_analyzer.py
│   ├── output_formatter.py
│   └── models.py          # Data models
├── tests/                 # Test suite (281 tests)
├── config/                # Configuration files
├── output/                # Generated output files
├── examples/              # Example outputs
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🚨 Important Notes

### Live Scraping Limitations

Major e-commerce sites (Amazon, Flipkart, etc.) actively block automated scraping. For production use, you'll need:

1. **Proxy Services** ($50-200/month) - Rotate IP addresses
2. **CAPTCHA Solvers** - Handle CAPTCHA challenges
3. **Rate Limiting** - Slow down requests (5-10 seconds)
4. **User Agent Rotation** - Mimic different browsers

**For testing and development, use test mode:**
```bash
python -m src.main --config config/config.test_mode.json
```

## 📊 Performance

- **Execution Time**: < 5 minutes for all sources
- **Memory Usage**: < 500 MB
- **Concurrent Requests**: Up to 5 simultaneous connections
- **Request Delays**: 1-3 seconds between requests
- **Retry Logic**: 3 attempts with exponential backoff

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Built with the help of assistants of  Kiro AI** -
- BeautifulSoup for HTML parsing
- Selenium for browser automation
- Hypothesis for property-based testing

## 📧 Contact

For questions or support, please open an issue on GitHub.
