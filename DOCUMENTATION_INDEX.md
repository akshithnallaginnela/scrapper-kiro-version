# Documentation Index

Complete guide to all documentation for the Organic Products Web Scraper.

## Getting Started

### For New Users

1. **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
   - Installation steps
   - First run
   - Basic configuration
   - Common tasks

2. **[README.md](README.md)** - Main documentation
   - Features overview
   - Installation instructions
   - Usage examples
   - Project structure

### For Experienced Users

1. **[config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md)** - Configuration reference
2. **[config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md)** - Selector examples
3. **[examples/README.md](examples/README.md)** - Usage examples

---

## Core Documentation

### Main Guides

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [README.md](README.md) | Main documentation and overview | First-time setup, general reference |
| [QUICK_START.md](QUICK_START.md) | Fast setup guide | Quick installation and first run |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problem solving guide | When encountering errors |
| [ERROR_CODES.md](ERROR_CODES.md) | Error reference | Understanding error messages |

### Configuration

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [config/README.md](config/README.md) | Configuration overview | Understanding config files |
| [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md) | Complete config reference | Customizing scraper behavior |
| [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md) | Selector examples | Adding new sources |

### Examples and Samples

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [examples/README.md](examples/README.md) | Usage examples | Learning by example |
| [examples/example_output.json](examples/example_output.json) | Sample JSON output | Understanding output format |
| [examples/example_output.csv](examples/example_output.csv) | Sample CSV output | Understanding CSV format |

### Performance

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) | Performance guide | Optimizing scraper speed |

---

## Documentation by Task

### Installation

**Primary:** [README.md - Installation](README.md#installation)  
**Quick:** [QUICK_START.md - Installation](QUICK_START.md#installation-2-minutes)  
**Troubleshooting:** [TROUBLESHOOTING.md - Installation Issues](TROUBLESHOOTING.md#installation-issues)

**Key Topics:**
- Python version requirements
- Dependency installation
- WebDriver setup
- Virtual environment setup

### Configuration

**Primary:** [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md)  
**Overview:** [config/README.md](config/README.md)  
**Quick:** [QUICK_START.md - Configuration](QUICK_START.md#configuration-2-minutes)

**Key Topics:**
- Configuration file formats (JSON/YAML)
- Source configuration
- Scraper type selection (BeautifulSoup vs Selenium)
- Performance tuning
- Test mode

### Adding Sources

**Primary:** [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md)  
**Guide:** [config/CONFIG_GUIDE.md - Adding Sources](config/CONFIG_GUIDE.md#adding-new-sources)  
**Examples:** [config/README.md - Adding New Sources](config/README.md#adding-new-sources)

**Key Topics:**
- CSS selector patterns
- Platform-specific selectors (Amazon, Flipkart, etc.)
- Testing selectors
- Selector best practices

### Usage

**Primary:** [README.md - Usage](README.md#usage)  
**Examples:** [examples/README.md](examples/README.md)  
**Quick:** [QUICK_START.md - First Run](QUICK_START.md#first-run-1-minute)

**Key Topics:**
- Basic usage
- Command line options
- Custom configuration
- Automated scheduling
- Python integration

### Troubleshooting

**Primary:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)  
**Errors:** [ERROR_CODES.md](ERROR_CODES.md)  
**Quick:** [QUICK_START.md - Troubleshooting](QUICK_START.md#troubleshooting)

**Key Topics:**
- Installation issues
- Configuration errors
- Scraping problems
- Performance issues
- Debugging tips

### Error Handling

**Primary:** [ERROR_CODES.md](ERROR_CODES.md)  
**Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Key Topics:**
- Exit codes
- Exception types
- HTTP status codes
- Error messages
- Log levels

### Output Files

**Primary:** [README.md - Output](README.md#output)  
**Examples:** [examples/example_output.json](examples/example_output.json), [examples/example_output.csv](examples/example_output.csv)  
**Guide:** [examples/README.md - Output File Examples](examples/README.md#output-file-examples)

**Key Topics:**
- JSON output format
- CSV output format
- Metadata structure
- Data analysis

### Testing

**Primary:** [README.md - Testing](README.md#testing)  
**Config:** [config/CONFIG_GUIDE.md - Test Mode](config/CONFIG_GUIDE.md#test-mode)

**Key Topics:**
- Running tests
- Test mode
- Property-based tests
- Coverage reports

### Performance

**Primary:** [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)  
**Config:** [config/CONFIG_GUIDE.md - Performance Tuning](config/CONFIG_GUIDE.md#performance-tuning)

**Key Topics:**
- Speed optimization
- Memory management
- Concurrent requests
- BeautifulSoup vs Selenium

---

## Documentation by User Type

### Beginners

**Start here:**
1. [QUICK_START.md](QUICK_START.md) - Get running in 5 minutes
2. [README.md](README.md) - Understand the basics
3. [examples/README.md](examples/README.md) - Learn from examples

**When you need help:**
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common problems
- [QUICK_START.md - Troubleshooting](QUICK_START.md#troubleshooting) - Quick fixes

### Intermediate Users

**Configuration:**
1. [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md) - Complete config reference
2. [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md) - Add sources

**Usage:**
1. [examples/README.md](examples/README.md) - Advanced examples
2. [README.md - Usage](README.md#usage) - All usage options

**Troubleshooting:**
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed solutions
2. [ERROR_CODES.md](ERROR_CODES.md) - Error reference

### Advanced Users

**Optimization:**
1. [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) - Performance tuning
2. [config/CONFIG_GUIDE.md - Performance](config/CONFIG_GUIDE.md#performance-tuning)

**Integration:**
1. [examples/README.md - Python Integration](examples/README.md#python-integration)
2. [examples/README.md - Data Analysis](examples/README.md#data-analysis)

**Development:**
1. [README.md - Development](README.md#development)
2. [README.md - Testing](README.md#testing)

### System Administrators

**Deployment:**
1. [examples/README.md - Automated Scheduling](examples/README.md#automated-scheduling)
2. [examples/README.md - Error Handling in Scripts](examples/README.md#error-handling-in-scripts)

**Monitoring:**
1. [ERROR_CODES.md](ERROR_CODES.md) - Exit codes and errors
2. [README.md - Logging](README.md#logging-and-monitoring)

**Troubleshooting:**
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - All issues
2. [ERROR_CODES.md - Debugging](ERROR_CODES.md#debugging-error-messages)

---

## Documentation by Topic

### Architecture

- [README.md - Features](README.md#features)
- [README.md - How It Works](README.md#how-it-works)
- [README.md - Project Structure](README.md#project-structure)

### Configuration Files

- [config/README.md](config/README.md) - Overview
- [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md) - Complete guide
- [config/config.json](config/config.json) - Default JSON config
- [config/config.yaml](config/config.yaml) - Default YAML config
- [config/config.example.json](config/config.example.json) - Extended example
- [config/config.comprehensive.json](config/config.comprehensive.json) - Full example

### CSS Selectors

- [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md) - Complete reference
- [config/CSS_SELECTORS_REFERENCE.md - B2C Platforms](config/CSS_SELECTORS_REFERENCE.md#b2c-platforms)
- [config/CSS_SELECTORS_REFERENCE.md - B2B Marketplaces](config/CSS_SELECTORS_REFERENCE.md#b2b-marketplaces)
- [config/CSS_SELECTORS_REFERENCE.md - Organic Sites](config/CSS_SELECTORS_REFERENCE.md#organic-product-websites)

### Error Handling

- [ERROR_CODES.md](ERROR_CODES.md) - Complete reference
- [ERROR_CODES.md - Exit Codes](ERROR_CODES.md#exit-codes)
- [ERROR_CODES.md - HTTP Status Codes](ERROR_CODES.md#http-status-codes)
- [ERROR_CODES.md - Exception Types](ERROR_CODES.md#exception-types)

### Examples

- [examples/README.md](examples/README.md) - All examples
- [examples/README.md - Usage Examples](examples/README.md#usage-examples)
- [examples/README.md - Configuration Examples](examples/README.md#configuration-examples)
- [examples/example_output.json](examples/example_output.json) - Sample JSON
- [examples/example_output.csv](examples/example_output.csv) - Sample CSV

### Logging

- [README.md - Logging](README.md#logging-and-monitoring)
- [ERROR_CODES.md - Log Level Messages](ERROR_CODES.md#log-level-messages)
- [TROUBLESHOOTING.md - Check Log File](TROUBLESHOOTING.md#check-log-file)

### Performance

- [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) - Complete guide
- [config/CONFIG_GUIDE.md - Performance Tuning](config/CONFIG_GUIDE.md#performance-tuning)
- [TROUBLESHOOTING.md - Performance Issues](TROUBLESHOOTING.md#performance-issues)

### Testing

- [README.md - Testing](README.md#testing)
- [config/CONFIG_GUIDE.md - Test Mode](config/CONFIG_GUIDE.md#test-mode)
- [README.md - Test Mode](README.md#test-mode)

### Troubleshooting

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Complete guide
- [TROUBLESHOOTING.md - Installation](TROUBLESHOOTING.md#installation-issues)
- [TROUBLESHOOTING.md - Configuration](TROUBLESHOOTING.md#configuration-issues)
- [TROUBLESHOOTING.md - Scraping](TROUBLESHOOTING.md#scraping-issues)
- [TROUBLESHOOTING.md - Performance](TROUBLESHOOTING.md#performance-issues)

---

## Quick Reference

### Most Common Documents

1. **Getting Started:** [QUICK_START.md](QUICK_START.md)
2. **Main Guide:** [README.md](README.md)
3. **Configuration:** [config/CONFIG_GUIDE.md](config/CONFIG_GUIDE.md)
4. **Selectors:** [config/CSS_SELECTORS_REFERENCE.md](config/CSS_SELECTORS_REFERENCE.md)
5. **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### By File Type

**Markdown Documentation:**
- README.md
- QUICK_START.md
- TROUBLESHOOTING.md
- ERROR_CODES.md
- PERFORMANCE_OPTIMIZATIONS.md
- DOCUMENTATION_INDEX.md (this file)
- config/README.md
- config/CONFIG_GUIDE.md
- config/CSS_SELECTORS_REFERENCE.md
- examples/README.md

**Configuration Files:**
- config/config.json
- config/config.yaml
- config/config.example.json
- config/config.example.yaml
- config/config.comprehensive.json
- config/config.test_mode.json

**Example Files:**
- examples/example_output.json
- examples/example_output.csv

---

## Documentation Statistics

- **Total Documents:** 15 markdown files
- **Configuration Files:** 6 files
- **Example Files:** 2 files
- **Total Pages:** ~100+ pages of documentation
- **Topics Covered:** 50+ topics

---

## Contributing to Documentation

When adding new documentation:

1. Update this index
2. Add cross-references to related documents
3. Follow existing formatting style
4. Include code examples where appropriate
5. Add to appropriate section in README.md

---

## Feedback

If you find documentation issues:
- Missing information
- Unclear explanations
- Broken links
- Outdated content

Please report them so we can improve the documentation.

