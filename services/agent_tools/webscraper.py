from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List
from langchain.docstore.document import Document
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


class RetrieveDataArgs(BaseModel):
    web_links: List[str] = Field(...,
                                description="The web links to be scraped. Make sure that their format is correct.")


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
            # Launch browser with specific options
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
                # Navigate with a more lenient strategy
                try:
                    # First try with commit navigation
                    await page.goto(url, wait_until='commit', timeout=10000)
                except PlaywrightTimeout:
                    # If that fails, try with domcontentloaded
                    await page.goto(url, wait_until='domcontentloaded', timeout=20000)
                
                # Wait for any one of these selectors to appear
                try:
                    await page.wait_for_selector('main, article, [role="main"], #content, .content', 
                                               timeout=5000,
                                               state='attached')
                except PlaywrightTimeout:
                    pass  # Continue even if no specific selector is found
                
                # Additional wait for dynamic content
                await asyncio.sleep(2)
                
                try:
                    # Try to find and click any cookie/consent buttons
                    for button_text in ['Accept', 'Accept All', 'Continue', 'Got it']:
                        button = page.get_by_text(button_text, exact=False)
                        if await button.count() > 0:
                            await button.click()
                            await asyncio.sleep(1)
                except Exception:
                    pass  # Ignore if no consent buttons found
                
                # Try multiple methods to get content
                content = ''
                try:
                    # First try to get the main content area
                    main_content = await page.evaluate("""() => {
                        const selectors = ['main', 'article', '[role="main"]', '#content', '.content'];
                        for (const selector of selectors) {
                            const element = document.querySelector(selector);
                            if (element) return element.innerText;
                        }
                        // If no specific content area found, try to get all visible text
                        const walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            {
                                acceptNode: function(node) {
                                    // Skip hidden elements
                                    const style = window.getComputedStyle(node.parentElement);
                                    if (style.display === 'none' || style.visibility === 'hidden') {
                                        return NodeFilter.FILTER_REJECT;
                                    }
                                    return NodeFilter.FILTER_ACCEPT;
                                }
                            }
                        );
                        let text = '';
                        let node;
                        while (node = walker.nextNode()) {
                            text += node.textContent + '\\n';
                        }
                        return text;
                    }""")
                    content = main_content
                except Exception:
                    # Last resort: get all text content
                    content = await page.evaluate('() => document.body.innerText')
                
                await browser.close()
                return content.strip()
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Error scraping content: {str(e)}")

    async def _arun(self, web_links: List[str]) -> List[Document] | str:
        try:
            docs = []
            for url in web_links:
                try:
                    content = await self._scrape_with_playwright(url)
                    if content and len(content.strip()) > 0:
                        docs.append(Document(
                            page_content=content,
                            metadata={"source": url}
                        ))
                except Exception as e:
                    print(f"Error scraping {url}: {str(e)}")
                    continue
            return docs if docs else "No content could be extracted from the provided URLs."
        except Exception as e:
            return f"Error scraping content: {str(e)}"

    def _run(self, query: str) -> str:
        """Run the tool synchronously."""
        raise NotImplementedError("This tool only supports async execution")


webscraper_tool = AsyncWebScraper()
