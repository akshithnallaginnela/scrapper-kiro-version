# Configuration Files Directory

This directory contains all configuration files and documentation for the Organic Products Web Scraper.

## Configuration Files

### Default Configurations

**`config.json`** - Default JSON configuration
- 3 sources: Amazon, Flipkart, IndiaMART B2B
- Balanced settings for production use
- Use with: `python -m src.main --config config/config.json`

**`config.yaml`** - Default YAML configuration
- Same sources as config.json
- YAML format for better readability
- Use with: `python -m src.main --config config/config.yaml`

### Example Configurations

**`config.example.json`** - Extended JSON example
- 5 sources including B2C and B2B platforms
- Amazon, Flipkart, IndiaMART, TradeIndia, Organic India
- Good starting point for customization

**`config.example.yaml`** - Extended YAML example
- Same sources as config.example.json
- YAML format alternative

**`config.comprehensive.json`** - Comprehensive configuration
- 8 sources covering B2C, B2B, and organic product websites
- Includes: Amazon, Flipkart, IndiaMART, TradeIndia, Alibaba, Organic India, iHerb, eBay
- Production-ready settings with higher timeouts and retry attempts
- Use for maximum data coverage

### Test Configuration

**`test_config.json`** - Test configuration
- Mock sources for testing
- Used by automated test suite
- Do not modify unless updating tests

## Documentation Files

**`CONFIG_GUIDE.md`** - Complete configuration documentation
- Detailed explanation of all configuration options
- Performance tuning guidelines
- Troubleshooting tips
- Best practices
- Example configurations for different use cases

**`CSS_SELECTORS_REFERENCE.md`** - CSS selectors reference
- Selector examples for 10+ platforms
- B2C platforms: Amazon, Flipkart, eBay, Walmart
- B2B marketplaces: IndiaMART, TradeIndia, Alibaba, Made-in-China
- Organic product websites: Organic India, Thrive Market, iHerb
- Testing and troubleshooting guide
- Common selector patterns

## Quick Start

### Using Default Configuration

```bash
# JSON format
python -m src.main --config config/config.json

# YAML format
python -m src.main --config config/config.yaml
```

### Using Extended Configuration

```bash
# 5 sources (recommended for balanced coverage)
python -m src.main --config config/config.example.json

# 8 sources (maximum coverage)
python -m src.main --config config/config.comprehensive.json
```

### Creating Custom Configuration

1. Copy an example file:
   ```bash
   cp config/config.example.yaml config/my_config.yaml
   ```

2. Edit the file to add/remove sources and adjust settings

3. Run with your custom config:
   ```bash
   python -m src.main --config config/my_config.yaml
   ```

## Configuration Structure

All configuration files follow this structure:

```yaml
sources:
  - name: "Source Name"
    url: "https://example.com/search"
    type: "beautifulsoup"  # or "selenium"
    selectors:
      container: ".product-container"
      name: ".product-name"
      price: ".product-price"
      link: ".product-link"
      image: ".product-image"

# Global settings
timeout: 30
retry_attempts: 3
output_directory: "./output"
browser_type: "chrome"
headless: true
request_delay_min: 1.0
request_delay_max: 3.0
max_concurrent_requests: 5
log_level: "INFO"
log_file: "scraper.log"
max_log_size_mb: 10
```

## Selector Keys

Each source requires these CSS selectors:

| Key | Description | Example |
|-----|-------------|---------|
| `container` | Product container element | `.s-result-item` |
| `name` | Product name/title | `h2 .a-text-normal` |
| `price` | Product price | `.a-price-whole` |
| `link` | Product URL (href) | `h2 a` |
| `image` | Product image (src) | `.s-image` |

## Scraper Types

**`beautifulsoup`** - For static HTML pages
- Faster performance
- Lower resource usage
- Best for: Amazon, eBay, most B2B sites

**`selenium`** - For JavaScript-rendered pages
- Required for dynamic content
- Supports explicit waits
- Best for: Flipkart, social media, modern SPAs

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `timeout` | 30 | Request timeout (seconds) |
| `retry_attempts` | 3 | Number of retry attempts |
| `output_directory` | `./output` | Output directory path |
| `browser_type` | `chrome` | Browser for Selenium |
| `headless` | `true` | Headless browser mode |
| `request_delay_min` | 1.0 | Min delay between requests |
| `request_delay_max` | 3.0 | Max delay between requests |
| `max_concurrent_requests` | 5 | Max concurrent connections |
| `log_level` | `INFO` | Logging level |
| `log_file` | `scraper.log` | Log file path |
| `max_log_size_mb` | 10 | Max log file size |

## Adding New Sources

To add a new data source:

1. Inspect the website's HTML using browser DevTools
2. Identify CSS selectors for container, name, price, link, and image
3. Determine if the site needs BeautifulSoup or Selenium
4. Add source configuration to your config file
5. Test with a small sample first

See `CSS_SELECTORS_REFERENCE.md` for selector examples.

## Validation

All configuration files in this directory have been validated:

- JSON files: Valid JSON syntax
- YAML files: Valid YAML syntax
- Selector keys: Consistent with implementation
- Required fields: All present

## Support

For detailed documentation:
- Configuration options: See `CONFIG_GUIDE.md`
- CSS selectors: See `CSS_SELECTORS_REFERENCE.md`
- General usage: See `../README.md`

## File Summary

```
config/
├── config.json                      # Default JSON config (3 sources)
├── config.yaml                      # Default YAML config (3 sources)
├── config.example.json              # Extended example (5 sources)
├── config.example.yaml              # Extended YAML example (5 sources)
├── config.comprehensive.json        # Comprehensive config (8 sources)
├── test_config.json                 # Test configuration
├── CONFIG_GUIDE.md                  # Complete configuration guide
├── CSS_SELECTORS_REFERENCE.md       # CSS selectors for 10+ platforms
└── README.md                        # This file
```

## Requirements Satisfied

This configuration setup satisfies the following requirements:

- **8.1**: Configuration from JSON/YAML files ✓
- **8.2**: Configurable target data sources ✓
- **8.3**: Configurable request timeout values ✓
- **8.4**: Configurable retry attempts ✓
- **8.5**: Configurable output directory path ✓
- **8.6**: Configurable browser type for Selenium ✓

All configuration files include example sources for:
- B2C platforms: Amazon, Flipkart, eBay, Walmart
- B2B marketplaces: IndiaMART, TradeIndia, Alibaba
- Organic product websites: Organic India, iHerb, Thrive Market
