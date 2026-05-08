import asyncio
import logging
import re
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Set, List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(
        self, 
        base_url: str, 
        max_depth: int = settings.MAX_CRAWL_DEPTH, 
        concurrency: int = settings.MAX_CONCURRENT_REQUESTS,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = self.normalize_url(base_url)
        self.domain = urlparse(self.base_url).netloc
        self.max_depth = max_depth
        self.concurrency = concurrency
        self.headers = headers or {"User-Agent": settings.USER_AGENT}
        
        self.visited: Set[str] = set()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.results: List[Dict[str, Any]] = []
        self.semaphore = asyncio.Semaphore(concurrency)
        
    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        # Remove fragments and normalize scheme/host
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

    def is_in_scope(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc == self.domain

    async def fetch(self, client: httpx.AsyncClient, url: str, depth: int) -> Optional[Dict[str, Any]]:
        async with self.semaphore:
            try:
                logger.info(f"Crawling: {url} (depth: {depth})")
                response = await client.get(url, headers=self.headers, follow_redirects=True, timeout=15.0)
                
                content_type = response.headers.get("Content-Type", "")
                is_html = "text/html" in content_type
                
                return {
                    "html": response.text if is_html else "",
                    "headers": dict(response.headers),
                    "status_code": response.status_code,
                    "url": str(response.url) # Actual URL after redirects
                }
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None

    def extract_assets(self, html: str, current_url: str) -> Dict[str, Any]:
        if not html: return {"links": set(), "forms": [], "params": set()}
        
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        forms = []
        params = set()
        
        # 1. Links and Query Parameters
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(current_url, href)
            parsed_href = urlparse(full_url)
            
            # Extract query params from links
            if parsed_href.query:
                q_params = parse_qs(parsed_href.query)
                for p in q_params: params.add(p)

            normalized = self.normalize_url(full_url)
            if self.is_in_scope(normalized):
                links.add(normalized)
        
        # 2. Forms and Inputs
        for form in soup.find_all("form"):
            form_data = {
                "action": urljoin(current_url, form.get("action", "")),
                "method": form.get("method", "get").lower(),
                "inputs": []
            }
            for input_tag in form.find_all(["input", "textarea", "select"]):
                name = input_tag.get("name")
                if name:
                    params.add(name)
                    form_data["inputs"].append({
                        "name": name,
                        "type": input_tag.get("type", "text"),
                        "value": input_tag.get("value", "")
                    })
            forms.append(form_data)
            
            # Add form action to links to crawl if in scope
            normalized_action = self.normalize_url(form_data["action"])
            if self.is_in_scope(normalized_action):
                links.add(normalized_action)
        
        # 3. Scripts and JS Endpoints
        for script in soup.find_all("script", src=True):
            src = script["src"]
            full_src = urljoin(current_url, src)
            # We don't necessarily crawl JS files for more HTML links, 
            # but we record them as assets
            if self.is_in_scope(self.normalize_url(full_src)):
                links.add(self.normalize_url(full_src))
            
        return {"links": links, "forms": forms, "params": list(params)}

    async def crawl_worker(self, client: httpx.AsyncClient):
        while True:
            url, depth = await self.queue.get()
            # Early-exit checks must mark the queue task as done before continuing
            if depth > self.max_depth or url in self.visited or len(self.results) >= 50:
                self.queue.task_done()
                continue

            try:
                self.visited.add(url)
                res = await self.fetch(client, url, depth)
                
                if res:
                    assets = self.extract_assets(res["html"], url)
                    
                    self.results.append({
                        "url": res["url"],
                        "original_url": url,
                        "depth": depth,
                        "headers": res["headers"],
                        "status_code": res["status_code"],
                        "html": res["html"],
                        "forms": assets["forms"],
                        "params": assets["params"]
                    })
                    
                    # Log progress every 10 pages
                    if len(self.results) % 10 == 0:
                        logger.info(f"Crawl progress: {len(self.results)} pages discovered...")
                    
                    if len(self.results) < 50:
                        for link in assets["links"]:
                            if link not in self.visited:
                                await self.queue.put((link, depth + 1))
            except Exception as e:
                logger.error(f"Worker error on {url}: {e}")
            finally:
                self.queue.task_done()

    async def run(self) -> List[Dict[str, Any]]:
        logger.info(f"Crawl engine started for {self.base_url} (Max Depth: {self.max_depth}, Max Pages: 50)")
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=10.0) as client:
            await self.queue.put((self.base_url, 0))
            
            workers = [asyncio.create_task(self.crawl_worker(client)) for _ in range(self.concurrency)]
            
            try:
                # Add a timeout to the entire crawl join to prevent infinite hanging
                await asyncio.wait_for(self.queue.join(), timeout=300.0) 
            except asyncio.TimeoutError:
                logger.warning("Crawl timed out after 5 minutes. Proceeding with discovered endpoints.")
            
            for worker in workers:
                worker.cancel()
                
        logger.info(f"Crawl complete. Total endpoints discovered: {len(self.results)}")
        return self.results
