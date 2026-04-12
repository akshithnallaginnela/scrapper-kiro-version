"""Script to regenerate cached files with correct hash keys."""

from pathlib import Path
import logging
from src.cache_manager import CacheManager

# Setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
cm = CacheManager('./test_data', logger)

# Sources to regenerate
sources = [
    {
        'url': 'https://www.amazon.com/s?k=organic+products',
        'name': 'Amazon Organic Products',
        'html_file': 'Amazon_Organic_Products_5d41402a.html'
    },
    {
        'url': 'https://www.flipkart.com/search?q=organic+products',
        'name': 'Flipkart Organic',
        'html_file': 'Flipkart_Organic_8e296a06.html'
    },
    {
        'url': 'https://www.indiamart.com/impcat/organic-products.html',
        'name': 'IndiaMART B2B Organic',
        'html_file': 'IndiaMART_B2B_Organic_c20ad4d7.html'
    }
]

# Regenerate cache files
for source in sources:
    html_path = Path('test_data') / source['html_file']
    html_content = html_path.read_text(encoding='utf-8')
    
    metadata = {
        'cached_at': '2024-01-15T10:30:00Z',
        'description': f'Sample cached HTML for {source["name"]}'
    }
    
    cm.save_cached_html(source['url'], source['name'], html_content, metadata)
    print(f"Regenerated cache for {source['name']}")

print("\nCache files regenerated successfully!")
print("\nGenerated cache keys:")
for source in sources:
    key = cm._generate_cache_key(source['url'], source['name'])
    print(f"  {source['name']}: {key}")
