# QWEN.md - Scrapy Project Context

## Project Overview
This directory is intended for a Python web scraping project using the Scrapy framework. Scrapy is a powerful and flexible open-source web crawling framework for Python, designed for extracting data from websites.

## Project Structure
Since this directory is currently empty, here's the typical structure of a Scrapy project:

- `scrapy.cfg`: Deployment configuration file
- `PROJECT_NAME/`: Main project directory
  - `spiders/`: Contains spider classes for scraping
  - `items.py`: Defines data structures for scraped items
  - `pipelines.py`: Processes scraped items (saving to database, etc.)
  - `middlewares.py`: Custom middleware components
  - `settings.py`: Project settings

## Key Concepts
1. **Spiders**: Classes that define how to follow links and extract data from web pages
2. **Items**: Containers for scraped data, similar to dictionaries with predefined keys
3. **Pipelines**: Process items after they're scraped (validation, deduplication, storage)
4. **Middlewares**: Hook points for processing requests/responses in the scraping pipeline

## Development Setup
1. Install Scrapy: `pip install scrapy`
2. Create project: `scrapy startproject PROJECT_NAME .`
3. Navigate to project directory
4. Create spiders in the `spiders/` directory
5. Run spider: `scrapy crawl SPIDER_NAME`

## Common Commands
- `scrapy startproject PROJECT_NAME .` - Create new project
- `scrapy genspider SPIDER_NAME DOMAIN` - Generate new spider
- `scrapy crawl SPIDER_NAME` - Run a spider
- `scrapy shell URL` - Interactive scraping shell
- `scrapy list` - List available spiders
- `scrapy check` - Check spider contracts
- `scrapy bench` - Run benchmark test

## Best Practices
1. Use Scrapy's built-in selectors (CSS or XPath) for data extraction
2. Handle errors gracefully with proper exception handling
3. Respect robots.txt and website terms of service
4. Implement proper delays between requests to avoid overloading servers
5. Use item pipelines for data processing and storage
6. Write tests for spiders using contracts
7. Store credentials securely (don't hardcode in source)
8. Use Scrapy's built-in logging for debugging

## Expected File Types
- Python files (.py) for spiders, items, pipelines, settings
- JSON/CSV files for data output
- Configuration files (scrapy.cfg)