"""
DOM-based web crawler using Scrapy for benchmarking comparison.
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import json


class DOMBasedSpider(scrapy.Spider):
    """
    Traditional DOM-based spider for comparison with VLM approach.
    """
    
    name = "dom_spider"
    
    def __init__(
        self,
        start_url: str,
        goal: str,
        selectors: Dict[str, str],
        max_pages: int = 20,
        callback: Optional[Callable] = None,
        *args,
        **kwargs
    ):
        """
        Initialize DOM-based spider.
        
        Args:
            start_url: Starting URL
            goal: Crawling goal (for documentation)
            selectors: CSS/XPath selectors for target elements
            max_pages: Maximum pages to crawl
            callback: Optional callback for extracted data
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.goal = goal
        self.selectors = selectors
        self.max_pages = max_pages
        self.pages_crawled = 0
        self.data_callback = callback
        self.extracted_data = []
        self.action_history = []
    
    def parse(self, response: Response):
        """Parse the response and extract data."""
        self.pages_crawled += 1
        
        # Record action
        self.action_history.append({
            "url": response.url,
            "timestamp": datetime.now().isoformat(),
            "step": self.pages_crawled
        })
        
        # Extract data based on selectors
        for key, selector in self.selectors.items():
            if selector.startswith("//"):
                # XPath selector
                elements = response.xpath(selector).getall()
            else:
                # CSS selector
                elements = response.css(selector).getall()
            
            if elements:
                data = {
                    "field": key,
                    "values": elements,
                    "url": response.url,
                    "timestamp": datetime.now().isoformat()
                }
                self.extracted_data.append(data)
                
                if self.data_callback:
                    self.data_callback(data)
        
        # Follow links if not at max pages
        if self.pages_crawled < self.max_pages:
            for link in response.css('a::attr(href)').getall()[:5]:
                yield response.follow(link, self.parse)
    
    def closed(self, reason):
        """Called when spider closes."""
        self.logger.info(f"Spider closed. Pages crawled: {self.pages_crawled}")


class DOMCrawler:
    """
    Wrapper for DOM-based crawling using Scrapy.
    """
    
    def __init__(self, max_pages: int = 20):
        """
        Initialize DOM crawler.
        
        Args:
            max_pages: Maximum pages to crawl
        """
        self.max_pages = max_pages
        self.results_dir = Path("data")
        self.results_dir.mkdir(exist_ok=True)
    
    def crawl(
        self,
        url: str,
        goal: str,
        selectors: Dict[str, str]
    ) -> Dict:
        """
        Perform DOM-based crawling.
        
        Args:
            url: Starting URL
            goal: Crawling goal
            selectors: CSS/XPath selectors for target data
            
        Returns:
            Crawl results with metrics
        """
        start_time = datetime.now()
        
        # Setup crawler
        process = CrawlerProcess(settings={
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'ROBOTSTXT_OBEY': False,
            'CONCURRENT_REQUESTS': 1,
            'DOWNLOAD_DELAY': 1,
            'LOG_LEVEL': 'INFO'
        })
        
        spider_args = {
            'start_url': url,
            'goal': goal,
            'selectors': selectors,
            'max_pages': self.max_pages
        }
        
        # Run crawler
        spider = None
        
        def spider_opened(spider_instance):
            nonlocal spider
            spider = spider_instance
        
        from scrapy.signalmanager import dispatcher
        from scrapy import signals
        dispatcher.connect(spider_opened, signal=signals.spider_opened)
        
        process.crawl(DOMBasedSpider, **spider_args)
        process.start()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Compile results
        results = {
            "goal": goal,
            "start_url": url,
            "pages_crawled": spider.pages_crawled if spider else 0,
            "data_extracted": spider.extracted_data if spider else [],
            "action_history": spider.action_history if spider else [],
            "duration_seconds": duration,
            "success": len(spider.extracted_data) > 0 if spider else False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save results
        results_file = self.results_dir / f"dom_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def create_selectors_from_goal(self, goal: str) -> Dict[str, str]:
        """
        Create basic selectors based on goal (simplified heuristic).
        
        Args:
            goal: Crawling goal
            
        Returns:
            Dictionary of selectors
        """
        selectors = {}
        
        # Basic heuristics for common goals
        if "price" in goal.lower() or "laptop" in goal.lower():
            selectors["prices"] = ".price, .product-price, [class*='price']"
            selectors["products"] = ".product-name, .product-title, h2.title"
        
        if "login" in goal.lower():
            selectors["login_button"] = "button[type='submit'], input[type='submit']"
            selectors["forms"] = "form"
        
        if "article" in goal.lower() or "content" in goal.lower():
            selectors["articles"] = "article, .article, .post"
            selectors["headings"] = "h1, h2, h3"
        
        # Default: collect all links and text
        if not selectors:
            selectors["links"] = "a::attr(href)"
            selectors["text"] = "p::text"
        
        return selectors


class SimpleSeleniumCrawler:
    """
    Alternative simple crawler using Selenium for better JavaScript support.
    """
    
    def __init__(self, headless: bool = True):
        """Initialize Selenium-based crawler."""
        self.headless = headless
    
    def crawl(self, url: str, goal: str, selectors: Dict[str, str]) -> Dict:
        """
        Crawl using Selenium.
        
        Args:
            url: Starting URL
            goal: Crawling goal
            selectors: CSS selectors for target data
            
        Returns:
            Crawl results
        """
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        
        start_time = datetime.now()
        
        # Setup Chrome options
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            driver.implicitly_wait(5)
            
            extracted_data = []
            
            # Extract data using selectors
            for key, selector in selectors.items():
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    values = [elem.text or elem.get_attribute("href") for elem in elements]
                    
                    if values:
                        extracted_data.append({
                            "field": key,
                            "values": values,
                            "url": url
                        })
                except Exception as e:
                    print(f"Error extracting {key}: {e}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results = {
                "goal": goal,
                "url": url,
                "data_extracted": extracted_data,
                "duration_seconds": duration,
                "success": len(extracted_data) > 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            return {
                "goal": goal,
                "url": url,
                "error": str(e),
                "success": False
            }
        
        finally:
            driver.quit()
