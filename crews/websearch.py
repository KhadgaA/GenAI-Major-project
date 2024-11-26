from typing import List, Dict, Any
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from crewai_tools import BaseTool

class WebSearchTool(BaseTool):
    name: str = "websearch tool"
    description: str = "Perform web search using DuckDuckGo."

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search using DuckDuckGo.
        """
        try:
            results = list(DDGS().text(
                query,
                max_results=1
            ))
            for r in results:
                r['link'] = r.pop('href')
                # r['snippet'] = r.pop('body')

            return results
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")

    def fetch_page_content(self, url: str) -> str:
        """
        Fetch and parse content from a webpage.
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text
        except Exception as e:
            return f"Error fetching content: {str(e)}"

    def enrich_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich search results with actual page content.
        """
        enriched_results = []
        for result in results:
            content = self.fetch_page_content(result['link'])
            enriched_results.append({
                **result,
                'full_content': content
            })
        return enriched_results

    def _run(self, query: str) -> List[Dict[str, Any]]:
        """
        Run the web search and enrich the results with page content.
        """
        # Perform the search
        search_results = self.search(query)
        
        # Enrich the search results
        enriched_results = self.enrich_search_results(search_results)
        
        return enriched_results


# # Assuming that you have a setup that looks like this:
# web_search_tool = WebSearchTool(max_results=5)

# # Now, create the agent passing the tool instance
# agent = Agent(
#     tools=[web_search_tool]  # List of tools, WebSearchTool should now be correctly recognized as a valid tool
# )
