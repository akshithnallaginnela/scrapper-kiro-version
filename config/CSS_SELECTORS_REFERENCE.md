# CSS Selectors Reference for Common Platforms

This guide provides CSS selector examples for popular e-commerce and B2B platforms. Use these as starting points and verify with browser DevTools as website structures change frequently.

## Table of Contents

- [B2C Platforms](#b2c-platforms)
  - [Amazon](#amazon)
  - [Flipkart](#flipkart)
  - [eBay](#ebay)
  - [Walmart](#walmart)
- [B2B Marketplaces](#b2b-marketplaces)
  - [IndiaMART](#indiamart)
  - [TradeIndia](#tradeindia)
  - [Alibaba](#alibaba)
  - [Made-in-China](#made-in-china)
- [Organic Product Websites](#organic-product-websites)
  - [Organic India](#organic-india)
  - [Thrive Market](#thrive-market)
  - [iHerb](#iherb)
- [Testing Selectors](#testing-selectors)

---

## B2C Platforms

### Amazon

**Platform Type:** BeautifulSoup (static HTML)

**Search URL Pattern:**
```
https://www.amazon.com/s?k=organic+products
https://www.amazon.in/s?k=organic+products
```

**Selectors:**
```json
{
  "container": ".s-result-item[data-component-type='s-search-result']",
  "name": "h2 .a-text-normal",
  "price": ".a-price-whole",
  "link": "h2 a.a-link-normal",
  "image": ".s-image"
}
```

**Alternative Selectors:**
```json
{
  "container": "div[data-asin]:not([data-asin=''])",
  "name": "span.a-size-medium",
  "price": "span.a-price span.a-offscreen",
  "link": "a.a-link-normal.s-no-outline",
  "image": "img.s-image"
}
```

**Notes:**
- Amazon frequently changes class names
- Use `data-asin` attribute for reliable product identification
- Price may be in `.a-price-whole` or `.a-offscreen`
- Sponsored products have different structure

---

### Flipkart

**Platform Type:** Selenium (JavaScript-rendered)

**Search URL Pattern:**
```
https://www.flipkart.com/search?q=organic+products
```

**Selectors:**
```json
{
  "container": "._1AtVbE",
  "name": "._4rR01T",
  "price": "._30jeq3",
  "link": "._1fQZEK",
  "image": "._396cs4"
}
```

**Alternative Selectors:**
```json
{
  "container": "div[data-id]",
  "name": "a.IRpwTa",
  "price": "div._30jeq3._1_WHN1",
  "link": "a.IRpwTa",
  "image": "img._396cs4"
}
```

**Notes:**
- Flipkart uses obfuscated class names (e.g., `_1AtVbE`)
- Requires Selenium due to lazy loading
- Wait for elements to load: `wait_selector: "._1AtVbE"`
- Class names change frequently; use data attributes when possible

---

### eBay

**Platform Type:** BeautifulSoup (static HTML)

**Search URL Pattern:**
```
https://www.ebay.com/sch/i.html?_nkw=organic+products
```

**Selectors:**
```json
{
  "container": ".s-item",
  "name": ".s-item__title",
  "price": ".s-item__price",
  "link": ".s-item__link",
  "image": ".s-item__image-img"
}
```

**Notes:**
- eBay has consistent class naming
- First result is often a promoted listing (skip if needed)
- Price includes currency symbol
- Multiple images available (use first)

---

### Walmart

**Platform Type:** Selenium (JavaScript-rendered)

**Search URL Pattern:**
```
https://www.walmart.com/search?q=organic+products
```

**Selectors:**
```json
{
  "container": "[data-item-id]",
  "name": "span[data-automation-id='product-title']",
  "price": "span[data-automation-id='product-price']",
  "link": "a[link-identifier]",
  "image": "img[data-automation-id='product-image']"
}
```

**Notes:**
- Use `data-automation-id` attributes for reliability
- Requires Selenium for dynamic content
- Price format: `$XX.XX`

---

## B2B Marketplaces

### IndiaMART

**Platform Type:** BeautifulSoup (static HTML)

**Search URL Pattern:**
```
https://www.indiamart.com/impcat/organic-products.html
https://www.indiamart.com/search.mp?ss=organic+products
```

**Selectors:**
```json
{
  "container": ".lst",
  "name": ".pnm",
  "price": ".prc",
  "link": ".pnm a",
  "image": ".pimg img"
}
```

**Alternative Selectors:**
```json
{
  "container": "div[class*='lst']",
  "name": "a.pnm",
  "price": "span.prc",
  "link": "a.pnm",
  "image": "img.pimg"
}
```

**Notes:**
- Price often shows "Get Latest Price" instead of actual price
- Multiple contact options available
- Supplier information in separate elements

---

### TradeIndia

**Platform Type:** BeautifulSoup (static HTML)

**Search URL Pattern:**
```
https://www.tradeindia.com/products/organic-products.html
https://www.tradeindia.com/search.html?ss=organic+products
```

**Selectors:**
```json
{
  "container": ".product-box",
  "name": ".product-name",
  "price": ".product-price",
  "link": ".product-name a",
  "image": ".product-img img"
}
```

**Alternative Selectors:**
```json
{
  "container": "div.catProdBox",
  "name": "h2.catProdName",
  "price": "span.catProdPrice",
  "link": "a.catProdLink",
  "image": "img.catProdImg"
}
```

**Notes:**
- Price format varies (INR, USD, "Price on Request")
- Minimum order quantity often displayed
- Supplier ratings available

---

### Alibaba

**Platform Type:** Selenium (JavaScript-rendered)

**Search URL Pattern:**
```
https://www.alibaba.com/trade/search?SearchText=organic+products
```

**Selectors:**
```json
{
  "container": ".organic-list-offer",
  "name": ".organic-list-offer-title",
  "price": ".organic-list-offer-price",
  "link": ".organic-list-offer-outter a",
  "image": ".organic-list-offer-img img"
}
```

**Notes:**
- Requires Selenium for lazy loading
- Price shows range (e.g., "$10.00 - $50.00")
- MOQ (Minimum Order Quantity) displayed
- Supplier verification badges available

---

### Made-in-China

**Platform Type:** BeautifulSoup (static HTML)

**Search URL Pattern:**
```
https://www.made-in-china.com/products-search/hot-china-products/organic_products.html
```

**Selectors:**
```json
{
  "container": ".item-wrap",
  "name": ".title",
  "price": ".price",
  "link": ".title a",
  "image": ".lazy-img"
}
```

**Notes:**
- Price in USD
- FOB price often displayed
- Supplier gold member status shown

---

## Organic Product Websites

### Organic India

**Platform Type:** Selenium (Shopify-based)

**Search URL Pattern:**
```
https://www.organicindia.com/collections/all
https://www.organicindia.com/search?q=products
```

**Selectors:**
```json
{
  "container": ".product-item",
  "name": ".product-item__title",
  "price": ".product-item__price",
  "link": ".product-item__link",
  "image": ".product-item__image img"
}
```

**Shopify Alternative:**
```json
{
  "container": ".grid-product",
  "name": ".grid-product__title",
  "price": ".grid-product__price",
  "link": ".grid-product__link",
  "image": ".grid-product__image"
}
```

**Notes:**
- Shopify-based sites have similar structure
- Lazy loading requires Selenium
- Sale prices in separate element

---

### Thrive Market

**Platform Type:** Selenium (React-based)

**Search URL Pattern:**
```
https://thrivemarket.com/search?keywords=organic
```

**Selectors:**
```json
{
  "container": "[data-testid='product-card']",
  "name": "[data-testid='product-title']",
  "price": "[data-testid='product-price']",
  "link": "[data-testid='product-link']",
  "image": "[data-testid='product-image']"
}
```

**Notes:**
- Uses `data-testid` attributes (very reliable)
- Requires login for full access
- Membership pricing shown

---

### iHerb

**Platform Type:** BeautifulSoup (static HTML)

**Search URL Pattern:**
```
https://www.iherb.com/search?kw=organic+products
```

**Selectors:**
```json
{
  "container": ".product-cell",
  "name": ".product-title",
  "price": ".product-price",
  "link": ".product-cell-container a",
  "image": ".product-image img"
}
```

**Notes:**
- Multiple currency options
- Discount prices shown separately
- Customer ratings available

---

## Testing Selectors

### Using Browser DevTools

1. **Open DevTools:** Right-click → Inspect Element (or F12)
2. **Open Console:** Click "Console" tab
3. **Test Selector:** Run JavaScript:

```javascript
// Test if selector finds elements
document.querySelectorAll('.s-result-item').length

// Test specific selector
document.querySelector('h2 .a-text-normal')?.textContent

// Test all product names
Array.from(document.querySelectorAll('.s-result-item')).map(
  item => item.querySelector('h2 .a-text-normal')?.textContent
)
```

### Using Python (BeautifulSoup)

```python
from bs4 import BeautifulSoup
import requests

url = "https://www.amazon.com/s?k=organic+products"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Test product selector
products = soup.select('.s-result-item')
print(f"Found {len(products)} products")

# Test name selector
for product in products[:3]:
    name = product.select_one('h2 .a-text-normal')
    print(name.text if name else "Name not found")
```

### Using Python (Selenium)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.flipkart.com/search?q=organic+products")

# Wait for elements
driver.implicitly_wait(10)

# Test product selector
products = driver.find_elements(By.CSS_SELECTOR, '._1AtVbE')
print(f"Found {len(products)} products")

# Test name selector
for product in products[:3]:
    name = product.find_element(By.CSS_SELECTOR, '._4rR01T')
    print(name.text)

driver.quit()
```

---

## Selector Best Practices

### 1. Prefer Stable Attributes

**Good:**
- `[data-testid='product']`
- `[data-component-type='s-search-result']`
- `[data-asin]`

**Avoid:**
- `.css-1234abc` (generated class names)
- `._1AtVbE` (obfuscated class names)

### 2. Use Specific Selectors

**Good:**
- `.product-item .product-title`
- `div[data-id] h2.title`

**Avoid:**
- `div div h2` (too generic)
- `.title` (too broad)

### 3. Handle Missing Elements

```python
# Always provide fallback
name = product.select_one('.name')
name_text = name.text if name else "Not Available"
```

### 4. Test Regularly

- Website structures change frequently
- Test selectors monthly
- Monitor scraper logs for extraction failures
- Keep backup selectors ready

### 5. Respect Rate Limits

- Add delays between requests (1-3 seconds)
- Use appropriate scraper type (BeautifulSoup vs Selenium)
- Monitor for HTTP 429 (Too Many Requests)

---

## Common Selector Patterns

### Product Container
```css
.product-item
.s-result-item
[data-product-id]
div[class*='product']
```

### Product Name
```css
.product-title
.product-name
h2.title
[data-testid='product-title']
```

### Product Price
```css
.product-price
.price
[data-testid='product-price']
span[class*='price']
```

### Product Link
```css
a.product-link
.product-title a
[href*='/product/']
```

### Product Image
```css
.product-image img
img[data-testid='product-image']
img.lazy
```

---

## Troubleshooting

### Selector Returns Empty

**Causes:**
- JavaScript-rendered content (use Selenium)
- Incorrect selector syntax
- Element not loaded yet (add wait)
- Website structure changed

**Solutions:**
1. Inspect HTML in browser DevTools
2. Test selector in browser console
3. Try alternative selectors
4. Add explicit waits (Selenium)

### Selector Returns Wrong Data

**Causes:**
- Selector too broad (matches multiple elements)
- Nested elements interfering
- Sponsored/ad content mixed in

**Solutions:**
1. Make selector more specific
2. Use `:not()` to exclude elements
3. Filter results in code
4. Use data attributes

### Performance Issues

**Causes:**
- Too many Selenium instances
- Complex selectors
- No caching

**Solutions:**
1. Use BeautifulSoup when possible
2. Simplify selectors
3. Reduce concurrent requests
4. Cache results

---

## Additional Resources

- [CSS Selectors Reference (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Chrome DevTools Guide](https://developer.chrome.com/docs/devtools/)

---

**Note:** This reference is for educational purposes. Always respect website terms of service, robots.txt files, and implement appropriate rate limiting. Website structures change frequently; verify selectors before use.
