from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Union
from langchain.docstore.document import Document
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


class RetrieveDataArgs(BaseModel):
    web_links: Union[List[str], str] = Field(...,
                                description="The web links to be scraped. Can be a single URL or a list of URLs. Make sure that their format is correct.")


class AsyncWebScraper(BaseTool):
    name: str = Field(default="web_scraper", description="The name of the tool")
    description: str = Field(
        default="Use this tool to scrape web data, like news, articles, and blogs etc."
    )
    args_schema: type[BaseModel] = Field(default=RetrieveDataArgs)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _scrape_with_playwright(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-web-security', '--disable-features=IsolateOrigins,site-per-process']
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            try:
                # Navigate with optimized strategy
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                
                # Efficiently wait for content
                await page.wait_for_load_state('networkidle', timeout=5000)
                
                # Handle cookie consent without delay
                try:
                    for button_text in ['Accept', 'Accept All', 'Continue', 'Got it']:
                        button = page.get_by_text(button_text, exact=False)
                        if await button.count() > 0:
                            await button.click()
                except Exception:
                    pass

                # Optimized content extraction
                content = await page.evaluate("""() => {
                    function isVisible(element) {
                        const style = window.getComputedStyle(element);
                        return style.display !== 'none' && 
                               style.visibility !== 'hidden' && 
                               style.opacity !== '0';
                    }

                    // Try to get main content first
                    const mainSelectors = ['main', 'article', '[role="main"]', '#content', '.content'];
                    for (const selector of mainSelectors) {
                        const element = document.querySelector(selector);
                        if (element && isVisible(element)) {
                            return element.innerText;
                        }
                    }

                    // Fallback: get all visible text content efficiently
                    const textNodes = [];
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        {
                            acceptNode: (node) => {
                                if (!node.parentElement || !isVisible(node.parentElement)) {
                                    return NodeFilter.FILTER_REJECT;
                                }
                                const text = node.textContent.trim();
                                return text ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
                            }
                        }
                    );

                    while (walker.nextNode()) {
                        textNodes.push(walker.currentNode.textContent.trim());
                    }
                    
                    return textNodes.join('\\n');
                }""")
                
                return content.strip()

            except PlaywrightTimeout as e:
                return f"Error: Timeout while loading {url}: {str(e)}"
            except Exception as e:
                return f"Error: Failed to scrape {url}: {str(e)}"
            finally:
                await page.close()
                await context.close()
                await browser.close()

    async def _arun(self, web_links: Union[List[str], str]) -> List[Document]:
        """Run web scraping asynchronously.
        
        Args:
            web_links: Single URL or list of URLs to scrape
            
        Returns:
            List of Document objects containing scraped content
        """
        # Convert single URL to list if necessary
        if isinstance(web_links, str):
            web_links = [web_links]
            
        tasks = []
        for url in web_links:
            tasks.append(self._scrape_with_playwright(url))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        documents = []

        for url, result in zip(web_links, results):
            if isinstance(result, Exception):
                print(f"Error scraping {url}: {str(result)}")
                continue
            if result:
                documents.append(Document(page_content=result, metadata={"source": url}))

        return documents

    def _run(self, query: str) -> str:
        raise NotImplementedError("This tool only supports async execution")


webscraper_tool = AsyncWebScraper()
