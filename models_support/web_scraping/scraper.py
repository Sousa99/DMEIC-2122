import abc
import tqdm

from typing import Generic, List, Generator, Optional, TypeVar

# =========================================================== MAIN CLASSES DEFINITION ===========================================================

ScrapedInfo = TypeVar("ScrapedInfo")

class WebScraper(abc.ABC, Generic[ScrapedInfo]):

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name : str = name

    @abc.abstractmethod
    def get_pages_to_scrape(self) -> Generator[str, None, None]:
        exit(f"🚨 Method 'get_pages_to_scrape' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def scrape_page(self, link: str) -> Optional[ScrapedInfo]:
        exit(f"🚨 Method 'scrape_page' not defined for '{self.__class__.__name__}'")

    def get_scraped_info(self) -> List[ScrapedInfo]:

        all_scrapped_info : List[ScrapedInfo] = []
        for page_to_scrape in tqdm.tqdm(self.get_pages_to_scrape(), desc=f"🌐 Scrapping '{self.name}' for its information", leave=True):
            scrapped_info = self.scrape_page(page_to_scrape)
            if scrapped_info is not None:
                all_scrapped_info.append(scrapped_info)

        return all_scrapped_info

