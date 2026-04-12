# Error Codes and Exit Codes Reference

This document provides a comprehensive reference for all error codes, exit codes, and error messages used by the Organic Products Web Scraper.

## Exit Codes

The scraper returns standard Unix exit codes:

| Exit Code | Status | Description | When It Occurs |
|-----------|--------|-------------|----------------|
| 0 | Success | Scraping completed successfully | All operations completed without critical errors |
| 1 | Failure | Scraping failed | Critical error occurred (insufficient data, configuration error, unexpected exception) |

### Exit Code Usage

```bash
python -m src.main
echo $?  # Check exit code (0 = success, 1 = failure)
```

In scripts:
```bash
#!/bin/bash
python -m src.main --config config/config.yaml
if [ $? -eq 0 ]; then
    echo "Scraping succeeded"
else
    echo "Scraping failed"
    exit 1
fi
```

---

## Exception Types

### InsufficientDataException

**Type:** Custom Exception  
**Exit Code:** 1  
**Severity:** ERROR

**Description:**  
Raised when fewer than 2 sources are successfully scraped. This is a critical error because the scraper requires data from at least 2 sources to provide reliable trending analysis.

**Error Message Format:**
```
Insufficient data: Only X source(s) successfully scraped (minimum 2 required).
Failed sources: Source1, Source2, ...
Details:
  - Source1: Error message
  - Source2: Error message
```

**Causes:**
- Network connectivity issues
- Websites blocking requests (HTTP 403, 429)
- CAPTCHA detection
- Invalid CSS selectors
- Timeout errors
- All sources failed

**Resolution:**
1. Check log file for specific source failures
2. Increase timeout and retry attempts
3. Verify CSS selectors are correct
4. Check network connectivity
5. Reduce request frequency (increase delays)
6. Add more sources to configuration

**Example:**
```
ERROR: Insufficient data: Only 1 source(s) successfully scraped (minimum 2 required).
Failed sources: Amazon, Flipkart
Details:
  - Amazon: HTTP 403 Forbidden
  - Flipkart: Request timeout after 30 seconds
```

---

### KeyboardInterrupt

**Type:** Built-in Exception  
**Exit Code:** 1  
**Severity:** WARNING

**Description:**  
Raised when user interrupts scraping with Ctrl+C.

**Error Message:**
```
WARNING: Scraping interrupted by user
```

**Resolution:**  
This is intentional user action. The scraper performs cleanup and exits gracefully.

---

### Unexpected Exceptions

**Type:** Generic Exception  
**Exit Code:** 1  
**Severity:** ERROR

**Description:**  
Any unexpected error not explicitly handled by the scraper.

**Error Message Format:**
```
ERROR: Unexpected error during scraping: <error details>
<stack trace>
```

**Causes:**
- Programming errors (bugs)
- Unexpected data formats
- System resource exhaustion
- File system errors

**Resolution:**
1. Check log file for full stack trace
2. Report bug with error details
3. Try running with debug logging enabled

---

## HTTP Status Codes

The scraper handles various HTTP status codes when making requests:

| Code | Status | Severity | Action | Description |
|------|--------|----------|--------|-------------|
| 200 | OK | INFO | Continue | Request successful |
| 301 | Moved Permanently | INFO | Follow redirect | Resource moved |
| 302 | Found | INFO | Follow redirect | Temporary redirect |
| 400 | Bad Request | WARNING | Skip source | Invalid request |
| 403 | Forbidden | WARNING | Skip source | Access denied |
| 404 | Not Found | WARNING | Skip source | Resource not found |
| 429 | Too Many Requests | WARNING | Skip source | Rate limit exceeded |
| 500 | Internal Server Error | WARNING | Retry | Server error |
| 502 | Bad Gateway | WARNING | Retry | Gateway error |
| 503 | Service Unavailable | WARNING | Retry | Service temporarily down |
| 504 | Gateway Timeout | WARNING | Retry | Gateway timeout |

### HTTP Error Handling

**403 Forbidden:**
```
WARNING: Source returned HTTP 403 (Forbidden), skipping
```
- Website is blocking your requests
- Increase request delays
- Enable headless mode
- Check robots.txt

**429 Too Many Requests:**
```
WARNING: Source returned HTTP 429 (Too Many Requests), skipping
```
- Rate limit exceeded
- Increase delays significantly
- Reduce concurrent requests
- Wait before retrying

**404 Not Found:**
```
WARNING: Source returned HTTP 404 (Not Found), skipping
```
- URL is invalid or resource moved
- Check configuration
- Update URL

**5xx Server Errors:**
```
WARNING: Source returned HTTP 500 (Internal Server Error), retrying...
```
- Server-side issue
- Automatic retry with exponential backoff
- May succeed on retry

---

## Log Level Messages

### ERROR Level

Critical errors that prevent successful operation:

| Message | Cause | Resolution |
|---------|-------|------------|
| `Configuration file not found: <path>` | Invalid config path | Verify file path, use absolute path |
| `Invalid JSON format in configuration file` | JSON syntax error | Validate JSON at jsonlint.com |
| `Invalid YAML format in configuration file` | YAML syntax error | Validate YAML at yamllint.com |
| `Insufficient data: Only X source(s) successfully scraped` | Too few sources succeeded | Check logs, fix source issues |
| `Error extracting products from <source>: <error>` | Extraction failed | Check selectors, verify HTML structure |
| `Unexpected error during scraping: <error>` | Unexpected exception | Check logs, report bug |

### WARNING Level

Non-critical issues that don't prevent operation:

| Message | Cause | Resolution |
|---------|-------|------------|
| `Configuration file missing, using defaults` | No config file provided | Provide config file or accept defaults |
| `No selectors configured for <source>, using defaults` | Missing selectors | Add selectors to config |
| `Source returned HTTP 403 (Forbidden), skipping` | Access denied | Increase delays, check robots.txt |
| `Source returned HTTP 429 (Too Many Requests), skipping` | Rate limited | Increase delays, reduce concurrency |
| `CAPTCHA detected on source, skipping` | CAPTCHA required | Use different source or test mode |
| `Request timeout after X seconds` | Slow response | Increase timeout value |
| `Element wait timeout after X seconds` | Element didn't load | Increase wait timeout, check selector |
| `No products extracted from any source` | Selectors don't match | Verify selectors with DevTools |
| `Memory limit exceeded: X MB (limit: Y MB)` | High memory usage | Reduce concurrent requests |
| `Execution time exceeded 5 minutes: Xs` | Slow execution | Optimize configuration |
| `Error closing source manager: <error>` | Cleanup error | Usually harmless, check logs |

### INFO Level

Normal operational messages:

| Message | Description |
|---------|-------------|
| `Organic Products Web Scraper - Starting` | Scraper started |
| `Configuration loaded from: <path>` | Config loaded successfully |
| `All components initialized successfully` | Initialization complete |
| `Starting scraping workflow...` | Beginning scraping |
| `Scraping phase complete: X successful, Y failed` | Scraping finished |
| `Extracted X products from <source>` | Products extracted |
| `Aggregation complete: X unique products` | Deduplication done |
| `Trend analysis complete: Top X products identified` | Ranking complete |
| `Output files generated: JSON: <file>, CSV: <file>` | Files created |
| `Scraping completed successfully!` | Success |
| `Organic Products Web Scraper - Finished` | Scraper finished |

### DEBUG Level

Detailed debugging information (only when `log_level: "DEBUG"`):

| Message Type | Description |
|--------------|-------------|
| HTTP requests | Full request details (URL, headers, method) |
| HTTP responses | Response status, headers, body size |
| HTML parsing | BeautifulSoup parsing details |
| Selector matching | CSS selector results |
| Element extraction | Individual field extraction |
| Timing information | Operation durations |
| Memory usage | Detailed memory metrics |

---

## Component-Specific Errors

### Configuration Manager

| Error | Cause | Resolution |
|-------|-------|------------|
| `Configuration file not found` | Invalid path | Check file path |
| `Invalid JSON format` | Syntax error | Validate JSON |
| `Invalid YAML format` | Syntax error | Validate YAML |
| `Missing required field: sources` | Incomplete config | Add sources array |

### Source Manager

| Error | Cause | Resolution |
|-------|-------|------------|
| `Connection timeout` | Network issue | Check connectivity, increase timeout |
| `DNS resolution failed` | Invalid domain | Check URL |
| `Connection refused` | Server not responding | Verify URL, try later |
| `SSL certificate error` | Certificate issue | Check URL, update certificates |

### BeautifulSoup Scraper

| Error | Cause | Resolution |
|-------|-------|------------|
| `Request timeout after X seconds` | Slow response | Increase timeout |
| `HTTP error: <code>` | HTTP error | See HTTP status codes |
| `Connection error: <error>` | Network issue | Check connectivity |

### Selenium Scraper

| Error | Cause | Resolution |
|-------|-------|------------|
| `WebDriver not found` | Driver not installed | Install ChromeDriver/GeckoDriver |
| `Browser not found` | Browser not installed | Install Chrome/Firefox |
| `WebDriverException: <error>` | Browser error | Check browser version, update driver |
| `TimeoutException: <selector>` | Element didn't load | Increase timeout, check selector |
| `NoSuchElementException: <selector>` | Element not found | Verify selector |

### Product Extractor

| Error | Cause | Resolution |
|-------|-------|------------|
| `Error extracting products: <error>` | Extraction failed | Check selectors |
| `Invalid URL format: <url>` | Malformed URL | Check HTML structure |
| `Missing required field: name` | Name not found | Verify name selector |
| `Missing required field: source` | Source not provided | Internal error, report bug |

### Data Aggregator

| Error | Cause | Resolution |
|-------|-------|------------|
| `Error aggregating products: <error>` | Aggregation failed | Check logs for details |
| `Error deduplicating products: <error>` | Deduplication failed | Check product data |

### Trend Analyzer

| Error | Cause | Resolution |
|-------|-------|------------|
| `Error calculating trending scores: <error>` | Calculation failed | Check product data |
| `Error ranking products: <error>` | Ranking failed | Check scores |

### Output Formatter

| Error | Cause | Resolution |
|-------|-------|------------|
| `Cannot create output directory: <path>` | Permission issue | Check permissions |
| `Error writing JSON file: <error>` | Write failed | Check disk space, permissions |
| `Error writing CSV file: <error>` | Write failed | Check disk space, permissions |
| `JSON serialization error: <error>` | Invalid data | Check product data |

---

## Performance Warnings

### Memory Warnings

| Warning | Threshold | Action |
|---------|-----------|--------|
| `Memory limit exceeded` | > 500 MB | Reduce concurrent requests |
| `High memory usage` | > 400 MB | Monitor memory, consider optimization |

### Timing Warnings

| Warning | Threshold | Action |
|---------|-----------|--------|
| `Execution time exceeded 5 minutes` | > 300 seconds | Optimize configuration |
| `Source scraping slow` | > 60 seconds per source | Check network, increase timeout |

---

## Validation Errors

### Product Validation

| Error | Cause | Resolution |
|-------|-------|------------|
| `Product name is required` | Empty name | Check name selector |
| `Product source is required` | Empty source | Internal error, report bug |
| `Invalid URL format` | Malformed URL | Check link selector |

### Configuration Validation

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid timeout value` | Negative or zero | Use positive integer |
| `Invalid retry_attempts value` | Negative | Use positive integer |
| `Invalid browser_type` | Unknown browser | Use "chrome" or "firefox" |
| `Invalid log_level` | Unknown level | Use DEBUG, INFO, WARNING, or ERROR |

---

## Error Message Format

All error messages follow a consistent format:

```
<LEVEL>: <Component>: <Message>
```

Examples:
```
ERROR: ConfigurationManager: Configuration file not found: config/missing.yaml
WARNING: SourceManager: Source returned HTTP 403 (Forbidden), skipping
INFO: ProductExtractor: Extracted 15 products from Amazon
DEBUG: BeautifulSoupScraper: Fetching HTML from https://example.com
```

---

## Debugging Error Messages

### Enable Debug Logging

```yaml
log_level: "DEBUG"
```

### Check Log File

```bash
tail -f scraper.log
```

### Search for Specific Errors

```bash
grep "ERROR" scraper.log
grep "WARNING" scraper.log
grep "InsufficientDataException" scraper.log
```

### Filter by Component

```bash
grep "SourceManager" scraper.log
grep "ProductExtractor" scraper.log
```

---

## Error Recovery

### Automatic Recovery

The scraper automatically recovers from:
- Individual source failures (continues with other sources)
- Network errors (retries with exponential backoff)
- Parsing errors (logs and continues)
- Missing optional fields (uses "Not Available")

### Manual Recovery

For critical errors:
1. Check log file for root cause
2. Fix configuration or network issues
3. Re-run scraper
4. Use test mode for debugging

---

## Getting Help

If you encounter an error not listed here:

1. **Check the log file** (`scraper.log`) for detailed error messages
2. **Enable debug logging** for more information
3. **Search this document** for similar errors
4. **Check TROUBLESHOOTING.md** for common solutions
5. **Report bugs** with full error message and log file

---

## Error Code Summary

| Category | Count | Severity |
|----------|-------|----------|
| Exit Codes | 2 | N/A |
| Exceptions | 3 | ERROR/WARNING |
| HTTP Status Codes | 11 | INFO/WARNING |
| Configuration Errors | 8 | ERROR |
| Scraping Errors | 15 | WARNING |
| Extraction Errors | 6 | ERROR/WARNING |
| Output Errors | 4 | ERROR |
| Performance Warnings | 4 | WARNING |
| Validation Errors | 8 | ERROR |

**Total:** 61 documented error conditions

