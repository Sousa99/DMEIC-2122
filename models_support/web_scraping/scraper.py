import abc
import tqdm

from typing import Generic, List, Generator, TypeVar

import driver

# =========================================================== MAIN CLASSES DEFINITION ===========================================================

ScrapedInfo = TypeVar("ScrapedInfo")

class WebScraper(abc.ABC, Generic[ScrapedInfo]):

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name : str = name

    @abc.abstractmethod
    def get_pages_to_scrape(self, driver: driver.Driver) -> Generator[str, None, None]:
        exit(f"🚨 Method 'get_pages_to_scrape' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def scrape_page(self, link: str, driver: driver.Driver) -> List[ScrapedInfo]:
        exit(f"🚨 Method 'scrape_page' not defined for '{self.__class__.__name__}'")

    def get_scraped_info(self, driver: driver.Driver) -> List[ScrapedInfo]:

        all_scrapped_info : List[ScrapedInfo] = []
        for page_to_scrape in tqdm.tqdm(self.get_pages_to_scrape(driver), desc=f"🌐 Scrapping '{self.name}' for its information", leave=True):
            scrapped_info = self.scrape_page(page_to_scrape, driver)
            all_scrapped_info.extend(scrapped_info)
        
        return all_scrapped_info

# ===================================================== MAIN TYPES OF SCRAPED INFO TYPES DEFINITION =====================================================

class ScrapedInfoValence():

    def __init__(self) -> None: pass

    @abc.abstractmethod
    def get_text(self) -> str:
        exit(f"🚨 Method 'get_text' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def get_valence_score(self, limit_floor: float, limit_ceil: float) -> float:
        exit(f"🚨 Method 'get_text' not defined for '{self.__class__.__name__}'")