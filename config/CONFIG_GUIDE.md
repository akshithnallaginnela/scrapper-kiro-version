# Configuration Guide

This guide explains all configuration options for the Organic Products Web Scraper.

## Configuration File Formats

The scraper supports both JSON and YAML configuration formats. Choose the format you prefer:

- **JSON**: `config/config.json`
- **YAML**: `config/config.yaml`

## Configuration Options

### Sources Configuration

The `sources` array defines the websites to scrape. Each source requires:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for the source |
| `url` | string | Yes | Target URL to scrape |
| `type` | string | Yes | Scraper type: `"beautifulsoup"` or `"selenium"` |
| `selectors` | object | Yes | CSS selectors for extracting product data |

#### Selector Configuration

Each source must define the following CSS selectors:

| Selector | Description | Example |
|----------|-------------|---------|
| `container` | Container element for each product | `.s-result-item` |
| `name` | Product name/title | `h2 .a-text-normal` |
| `price` | Product price | `.a-price-whole` |
| `link` | Product URL (href attribute) | `h2 a` |
| `image` | Product image (src attribute) | `.s-image` |

**Example Source Configuration:**

```json
{
  "name": "Amazon Organic Products",
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
```

### Scraper Type Selection

**BeautifulSoup (`"beautifulsoup"`)**
- Use for static HTML pages
- Faster performance (~70% faster than Selenium)
- Lower resource usage
- Best for: Amazon, eBay, most B2B sites

**Selenium (`"selenium"`)**
- Use for JavaScript-rendered pages
- Required for dynamic content
- Supports explicit waits for element loading
- Best for: Flipkart, social media, modern SPAs

### Global Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | integer | 30 | Request timeout in seconds |
| `retry_attempts` | integer | 3 | Number of retry attempts for failed requests |
| `output_directory` | string | `"./output"` | Directory for output files |
| `browser_type` | string | `"chrome"` | Browser for Selenium: `"chrome"` or `"firefox"` |
| `headless` | boolean | `true` | Run browser in headless mode |
| `request_delay_min` | float | 1.0 | Minimum delay between requests (seconds) |
| `request_delay_max` | float | 3.0 | Maximum delay between requests (seconds) |
| `max_concurrent_requests` | integer | 5 | Maximum concurrent connections |
| `log_level` | string | `"INFO"` | Logging level: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"` |
| `log_file` | string | `"scraper.log"` | Log file path |
| `max_log_size_mb` | integer | 10 | Maximum log file size before rotation |
| `test_mode` | boolean | `false` | Enable test mode to use cached responses instead of live requests |
| `test_data_directory` | string | `"./test_data"` | Directory containing cached HTML responses for test mode |

### Test Mode

Test mode allows you to run the scraper using cached HTML responses instead of making live HTTP requests. This is useful for:

- **Faster testing**: No network delays, instant results
- **Reproducible tests**: Same HTML every time, consistent results
- **Development**: Test extraction logic without hitting real websites
- **CI/CD pipelines**: Run tests without external dependencies

**Enabling Test Mode:**

```json
{
  "test_mode": true,
  "test_data_directory": "./test_data",
  "sources": [...]
}
```

**How It Works:**

1. When `test_mode: true`, the scraper looks for cached HTML files in `test_data_directory`
2. Cache files are named using the pattern: `{source_name}_{url_hash}.html`
3. If a cached file exists, it's used instead of making a live request
4. If no cached file exists, the scraper falls back to a live request (and logs a warning)

**Creating Cached Responses:**

Use the `regenerate_cache.py` script to create cached responses:

```bash
python regenerate_cache.py
```

This will scrape all configured sources and save the HTML to the test_data directory.

**Example Test Mode Configuration:**

See `config/config.test_mode.json` for a complete example.

### Performance Tuning

**For faster scraping:**
- Use `"beautifulsoup"` type when possible
- Increase `max_concurrent_requests` (up to 10)
- Reduce `request_delay_min` and `request_delay_max` (minimum 0.5s recommended)
- Enable `headless: true` for Selenium

**For more reliable scraping:**
- Increase `timeout` (up to 60 seconds)
- Increase `retry_attempts` (up to 5)
- Increase `request_delay_min` and `request_delay_max` (2-5 seconds)
- Reduce `max_concurrent_requests` (2-3)

### Rate Limiting

The scraper implements automatic rate limiting to avoid being blocked:

- Random delays between `request_delay_min` and `request_delay_max`
- Per-domain rate limiting (tracks last request time)
- Exponential backoff on retry attempts
- Respects HTTP 429 (Too Many Requests) responses

## Example Configurations

### Minimal Configuration

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

timeout: 45
retry_attempts: 4
output_directory: "./output"
browser_type: "chrome"
headless: true
request_delay_min: 2.0
request_delay_max: 4.0
max_concurrent_requests: 3
log_level: "INFO"
log_file: "scraper.log"
max_log_size_mb: 20
```

### Development/Testing Configuration

```json
{
  "sources": [
    {
      "name": "Test Source",
      "url": "https://example.com/products",
      "type": "beautifulsoup",
      "selectors": {
        "container": ".product",
        "name": ".name",
        "price": ".price",
        "link": "a",
        "image": "img"
      }
    }
  ],
  "timeout": 10,
  "retry_attempts": 1,
  "output_directory": "./test_output",
  "log_level": "DEBUG",
  "max_concurrent_requests": 1
}
```

## Using Configuration Files

### Command Line

```bash
# Use JSON configuration
python -m src.main --config config/config.json

# Use YAML configuration
python -m src.main --config config/config.yaml

# Use default configuration (if no --config specified)
python -m src.main
```

### Default Behavior

If no configuration file is specified, the scraper uses built-in defaults:
- Timeout: 30 seconds
- Retry attempts: 3
- Output directory: `./output`
- Browser: Chrome (headless)
- Log level: INFO

## Troubleshooting

### Configuration Not Loading

**Error:** `Configuration file not found`
- Verify the file path is correct
- Use absolute path or path relative to working directory
- Check file permissions

**Error:** `Invalid JSON/YAML format`
- Validate JSON at https://jsonlint.com/
- Validate YAML at https://www.yamllint.com/
- Check for missing commas, quotes, or indentation

### Selector Not Working

**Symptoms:** Products not extracted, "Not Available" in output
- Inspect the target website's HTML structure
- Use browser DevTools to test CSS selectors
- Website structure may have changed (update selectors)
- Try using Selenium instead of BeautifulSoup

### Performance Issues

**Symptoms:** Scraping takes too long
- Reduce number of sources
- Use BeautifulSoup instead of Selenium when possible
- Increase `max_concurrent_requests`
- Reduce `request_delay_min` and `request_delay_max`

### Getting Blocked

**Symptoms:** HTTP 403, 429 errors, CAPTCHA
- Increase `request_delay_min` and `request_delay_max`
- Reduce `max_concurrent_requests`
- Enable `headless: true`
- Add more diverse sources instead of hammering one site

## Best Practices

1. **Start Small**: Test with 1-2 sources before adding more
2. **Respect Robots.txt**: Check website's robots.txt file
3. **Use Appropriate Delays**: 1-3 seconds minimum between requests
4. **Monitor Logs**: Check logs for errors and warnings
5. **Update Selectors**: Website structures change; maintain selectors
6. **Test Regularly**: Run test scrapes to verify selectors still work
7. **Handle Failures Gracefully**: Configure retry attempts appropriately
8. **Use Version Control**: Track configuration changes in git

## Advanced Configuration

### Custom User Agents

To add custom user agents (requires code modification):

```python
# In beautifulsoup_scraper.py or selenium_scraper.py
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### Proxy Support

To add proxy support (requires code modification):

```python
# In source_manager.py
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}
```

### Custom Selectors Per Platform

See `CSS_SELECTORS_REFERENCE.md` for platform-specific selector examples.
