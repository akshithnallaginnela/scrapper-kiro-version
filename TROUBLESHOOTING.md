# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Organic Products Web Scraper.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Scraping Issues](#scraping-issues)
- [Performance Issues](#performance-issues)
- [Output Issues](#output-issues)
- [Error Codes Reference](#error-codes-reference)

---

## Installation Issues

### Python Version Error

**Error:**
```
ERROR: Python 3.8 or higher is required
```

**Cause:** Your Python version is too old.

**Solution:**
1. Check your Python version:
   ```bash
   python --version
   ```
2. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
3. Use a virtual environment with the correct version:
   ```bash
   python3.8 -m venv venv
   source venv/bin/activate
   ```

### Dependency Installation Fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Cause:** Package not available or network issues.

**Solution:**
1. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```
2. Install dependencies one by one to identify the problematic package:
   ```bash
   pip install beautifulsoup4
   pip install selenium
   pip install requests
   ```
3. Check your internet connection
4. Try using a different package index:
   ```bash
   pip install -r requirements.txt --index-url https://pypi.org/simple
   ```

### WebDriver Not Found

**Error:**
```
ERROR: ChromeDriver not found in PATH
ERROR: GeckoDriver not found in PATH
```

**Cause:** WebDriver executable not installed or not in system PATH.

**Solution:**

**For Chrome:**
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Check your Chrome version: `chrome://version`
3. Download matching ChromeDriver version
4. Add to PATH:
   - **Linux/Mac:** Move to `/usr/local/bin/`
   - **Windows:** Add directory to PATH environment variable

**For Firefox:**
1. Download GeckoDriver from https://github.com/mozilla/geckodriver/releases
2. Add to PATH (same as above)

**Verify installation:**
```bash
python check_dependencies.py
```

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Cause:** Running from wrong directory or package not installed.

**Solution:**
1. Ensure you're in the project root directory
2. Install in development mode:
   ```bash
   pip install -e .
   ```
3. Or run as module:
   ```bash
   python -m src.main
   ```

---

## Configuration Issues

### Configuration File Not Found

**Error:**
```
ERROR: Configuration file not found: config/my_config.yaml
```

**Cause:** File path is incorrect or file doesn't exist.

**Solution:**
1. Verify file exists:
   ```bash
   ls -la config/my_config.yaml
   ```
2. Use absolute path:
   ```bash
   python -m src.main --config /full/path/to/config.yaml
   ```
3. Check current working directory:
   ```bash
   pwd
   ```

### Invalid JSON/YAML Format

**Error:**
```
ERROR: Invalid JSON format in configuration file
ERROR: Invalid YAML format in configuration file
```

**Cause:** Syntax error in configuration file.

**Solution:**
1. Validate JSON at https://jsonlint.com/
2. Validate YAML at https://www.yamllint.com/
3. Common issues:
   - Missing commas in JSON
   - Incorrect indentation in YAML
   - Unquoted strings with special characters
   - Missing closing brackets/braces

**Example of valid JSON:**
```json
{
  "sources": [
    {
      "name": "Amazon",
      "url": "https://amazon.com/s?k=organic",
      "type": "beautifulsoup",
      "selectors": {
        "container": ".s-result-item",
        "name": "h2 .a-text-normal",
        "price": ".a-price-whole",
        "link": "h2 a",
        "image": ".s-image"
      }
    }
  ],
  "timeout": 30
}
```

### Missing Required Configuration Fields

**Error:**
```
WARNING: Configuration file missing, using defaults
```

**Cause:** Configuration file doesn't have required fields.

**Solution:**
1. Use example configuration as template:
   ```bash
   cp config/config.example.json config/my_config.json
   ```
2. Ensure all required fields are present:
   - `sources` (array)
   - Each source must have: `name`, `url`, `type`, `selectors`

---

## Scraping Issues

### Insufficient Data Error

**Error:**
```
ERROR: Insufficient data: Only 1 source(s) successfully scraped (minimum 2 required)
```

**Exit Code:** 1

**Cause:** Fewer than 2 sources were successfully scraped.

**Solution:**
1. Check the log file for details on why sources failed
2. Common causes:
   - Network connectivity issues
   - Websites blocking requests (403, 429 errors)
   - CAPTCHA detection
   - Invalid CSS selectors
   - Timeout errors
3. Try running with fewer sources first to identify the problem
4. Increase timeout and retry attempts in configuration:
   ```yaml
   timeout: 60
   retry_attempts: 5
   ```

### HTTP 403 Forbidden

**Error:**
```
WARNING: Source returned HTTP 403 (Forbidden), skipping
```

**Cause:** Website is blocking your requests.

**Solution:**
1. Increase request delays:
   ```yaml
   request_delay_min: 3.0
   request_delay_max: 5.0
   ```
2. Enable headless mode (if using Selenium):
   ```yaml
   headless: true
   ```
3. Reduce concurrent requests:
   ```yaml
   max_concurrent_requests: 1
   ```
4. Check website's robots.txt file
5. Consider using a different source

### HTTP 429 Too Many Requests

**Error:**
```
WARNING: Source returned HTTP 429 (Too Many Requests), skipping
```

**Cause:** You're making requests too quickly.

**Solution:**
1. Increase request delays significantly:
   ```yaml
   request_delay_min: 5.0
   request_delay_max: 10.0
   ```
2. Reduce concurrent requests:
   ```yaml
   max_concurrent_requests: 1
   ```
3. Wait before retrying (the website may have rate limit windows)

### CAPTCHA Detected

**Error:**
```
WARNING: CAPTCHA detected on source, skipping
```

**Cause:** Website requires CAPTCHA verification.

**Solution:**
1. Use different sources that don't require CAPTCHA
2. Increase delays between requests
3. Use headless mode
4. Consider using test mode for development:
   ```yaml
   test_mode: true
   ```

### Timeout Errors

**Error:**
```
ERROR: Request timeout after 30 seconds
ERROR: Element wait timeout after 10 seconds
```

**Cause:** Website is slow or unresponsive.

**Solution:**
1. Increase timeout values:
   ```yaml
   timeout: 60
   ```
2. Check your internet connection
3. Try accessing the website manually in a browser
4. The website may be temporarily down

### No Products Extracted

**Error:**
```
WARNING: No products extracted from any source
```

**Cause:** CSS selectors are incorrect or website structure changed.

**Solution:**
1. Verify selectors using browser DevTools:
   - Right-click on product → Inspect Element
   - Test selector in console: `document.querySelectorAll('.your-selector')`
2. Check if website structure has changed
3. Update selectors in configuration
4. See `config/CSS_SELECTORS_REFERENCE.md` for examples
5. Try using Selenium instead of BeautifulSoup:
   ```yaml
   type: "selenium"
   ```

### Parsing Errors

**Error:**
```
ERROR: Error extracting products from Source: ...
```

**Cause:** HTML structure doesn't match expected format.

**Solution:**
1. Check log file for detailed error message
2. Verify selectors are correct
3. Test with a single source first
4. Use more specific selectors
5. Handle missing elements gracefully (scraper should do this automatically)

---

## Performance Issues

### Scraping Takes Too Long

**Symptom:** Scraping takes more than 5 minutes.

**Cause:** Too many sources, slow websites, or inefficient configuration.

**Solution:**
1. Reduce number of sources
2. Use BeautifulSoup instead of Selenium when possible:
   ```yaml
   type: "beautifulsoup"
   ```
3. Increase concurrent requests:
   ```yaml
   max_concurrent_requests: 10
   ```
4. Reduce request delays:
   ```yaml
   request_delay_min: 0.5
   request_delay_max: 1.5
   ```
5. Enable headless mode for Selenium:
   ```yaml
   headless: true
   ```

### High Memory Usage

**Warning:**
```
WARNING: Memory limit exceeded: 550.00 MB (limit: 500.00 MB)
```

**Cause:** Too many concurrent requests or large HTML responses.

**Solution:**
1. Reduce concurrent requests:
   ```yaml
   max_concurrent_requests: 3
   ```
2. Process sources sequentially instead of concurrently
3. Enable headless mode (uses less memory):
   ```yaml
   headless: true
   ```
4. Close browser instances properly (scraper should do this automatically)

### Browser Crashes

**Error:**
```
ERROR: WebDriverException: Chrome crashed
```

**Cause:** Browser instability or resource exhaustion.

**Solution:**
1. Enable headless mode:
   ```yaml
   headless: true
   ```
2. Reduce concurrent Selenium instances
3. Update ChromeDriver/GeckoDriver to latest version
4. Increase system resources (RAM)
5. Try Firefox instead of Chrome:
   ```yaml
   browser_type: "firefox"
   ```

---

## Output Issues

### Output Directory Not Created

**Error:**
```
ERROR: Cannot create output directory
```

**Cause:** Permission issues or invalid path.

**Solution:**
1. Check directory permissions:
   ```bash
   ls -la output/
   ```
2. Create directory manually:
   ```bash
   mkdir -p output
   chmod 755 output
   ```
3. Use absolute path in configuration:
   ```yaml
   output_directory: "/full/path/to/output"
   ```

### Empty Output Files

**Symptom:** JSON/CSV files are created but contain no products.

**Cause:** No products were extracted from sources.

**Solution:**
1. Check log file for extraction errors
2. Verify CSS selectors are correct
3. Test sources manually in browser
4. See "No Products Extracted" section above

### Invalid JSON Output

**Error:**
```
ERROR: Cannot parse JSON output file
```

**Cause:** Serialization error or file corruption.

**Solution:**
1. Check log file for serialization errors
2. Validate JSON at https://jsonlint.com/
3. Re-run scraper to regenerate output
4. Check for special characters in product data

---

## Error Codes Reference

### Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Scraping completed successfully |
| 1 | Failure | Scraping failed (see error message) |

### Common Error Messages

| Error | Severity | Meaning |
|-------|----------|---------|
| `InsufficientDataException` | ERROR | Fewer than 2 sources succeeded |
| `Configuration file not found` | ERROR | Config file path is invalid |
| `Invalid JSON/YAML format` | ERROR | Config file has syntax errors |
| `HTTP 403 Forbidden` | WARNING | Website blocking requests |
| `HTTP 429 Too Many Requests` | WARNING | Rate limit exceeded |
| `CAPTCHA detected` | WARNING | CAPTCHA verification required |
| `Request timeout` | WARNING | Request took too long |
| `Element wait timeout` | WARNING | Selenium element didn't load |
| `No products extracted` | WARNING | CSS selectors didn't match |
| `Memory limit exceeded` | WARNING | Memory usage over 500 MB |
| `Execution time exceeded` | WARNING | Scraping took over 5 minutes |

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success |
| 403 | Forbidden | Website blocking - increase delays |
| 404 | Not Found | URL invalid - check configuration |
| 429 | Too Many Requests | Rate limited - increase delays |
| 500 | Internal Server Error | Website issue - retry later |
| 502 | Bad Gateway | Website issue - retry later |
| 503 | Service Unavailable | Website down - retry later |

---

## Debugging Tips

### Enable Debug Logging

Set log level to DEBUG for detailed information:

```yaml
log_level: "DEBUG"
```

This will log:
- All HTTP requests and responses
- HTML parsing details
- Selector matching results
- Timing information

### Check Log File

The log file contains detailed information about all operations:

```bash
tail -f scraper.log
```

Look for:
- ERROR messages (critical issues)
- WARNING messages (non-critical issues)
- Timing information (performance)
- Source success/failure status

### Test Individual Sources

Test one source at a time to isolate issues:

```yaml
sources:
  - name: "Test Source"
    url: "https://example.com"
    type: "beautifulsoup"
    selectors:
      container: ".product"
      name: ".name"
      price: ".price"
      link: "a"
      image: "img"
```

### Use Test Mode

Enable test mode to use cached responses:

```yaml
test_mode: true
test_data_directory: "./test_data"
```

This eliminates network issues and allows you to focus on extraction logic.

### Verify Dependencies

Run the dependency checker:

```bash
python check_dependencies.py
```

This verifies:
- Python version
- Required libraries
- WebDriver availability

### Test CSS Selectors

Test selectors in browser console:

```javascript
// Test container selector
document.querySelectorAll('.s-result-item').length

// Test name selector
document.querySelector('h2 .a-text-normal')?.textContent

// Test all products
Array.from(document.querySelectorAll('.s-result-item')).map(
  item => item.querySelector('h2 .a-text-normal')?.textContent
)
```

---

## Getting Help

If you're still experiencing issues:

1. **Check the log file** for detailed error messages
2. **Review configuration** against examples in `config/` directory
3. **Test selectors** using browser DevTools
4. **Enable debug logging** for more information
5. **Try test mode** to eliminate network issues
6. **Reduce complexity** by testing with fewer sources

For additional help:
- See `README.md` for general usage
- See `config/CONFIG_GUIDE.md` for configuration details
- See `config/CSS_SELECTORS_REFERENCE.md` for selector examples
- See `ERROR_CODES.md` for complete error reference

---

## Common Solutions Summary

| Problem | Quick Solution |
|---------|---------------|
| Installation fails | Upgrade pip: `pip install --upgrade pip` |
| WebDriver not found | Run: `python check_dependencies.py` |
| Config file error | Validate at jsonlint.com or yamllint.com |
| Insufficient data | Check logs, increase timeout/retries |
| HTTP 403/429 | Increase delays, reduce concurrent requests |
| CAPTCHA detected | Use different sources or test mode |
| Timeout errors | Increase timeout in configuration |
| No products | Verify selectors with browser DevTools |
| Slow performance | Use BeautifulSoup, increase concurrency |
| High memory | Reduce concurrent requests, use headless |
| Empty output | Check logs for extraction errors |

