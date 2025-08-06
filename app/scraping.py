import httpx
from bs4 import BeautifulSoup
import pandas as pd

async def scrape_wikipedia_table(url: str) -> pd.DataFrame:
    """
    Scrape the first wikitable from the Wikipedia URL and return as DataFrame
    """
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "wikitable"})
        if not table:
            return None

        # Use pandas to parse html table for robustness
        dfs = pd.read_html(str(table))
        if dfs:
            return dfs[0]
        return None
