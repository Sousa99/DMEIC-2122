import abc
import tqdm
import pickle

from typing     import Any, Dict, Generic, Generator, TypeVar

import driver

# =========================================================== MAIN CLASSES DEFINITION ===========================================================

ScrapedInfo = TypeVar("ScrapedInfo")

class WebScraper(abc.ABC, Generic[ScrapedInfo]):

    def __init__(self, name: str, version: str, state: Dict[str, Any]) -> None:
        super().__init__()
        self.name : str = name
        self.version : str = version
        self.state : Dict[str, Any] = state

    @abc.abstractmethod
    def get_pages_to_scrape(self, driver: driver.Driver) -> Generator[str, None, None]:
        exit(f"🚨 Method 'get_pages_to_scrape' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def scrape_page(self, link: str, driver: driver.Driver) -> Generator[ScrapedInfo, None, None]:
        exit(f"🚨 Method 'scrape_page' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def callback_accessible(self, page_source: str) -> bool:
        return True

    def get_scraped_info(self, driver: driver.Driver) -> Generator[ScrapedInfo, None, None]:

        for page_to_scrape in tqdm.tqdm(self.get_pages_to_scrape(driver), desc=f"🌐 Scrapping '{self.name}' for its information", leave=True):
            for scrapped_info in self.scrape_page(page_to_scrape, driver):
                yield scrapped_info

    def get_file_save_prefix(self) -> str:
        return f'{self.name}_{self.version}_';

    def save_state(self, path_to_save: str):
        # Save iteration checkpointa
        file = open(path_to_save, "wb")
        pickle.dump(self.state, file)
        file.close()

    def load_state(self, path_to_load: str):
        # Load iteration checkpointa
        file = open(path_to_load, "rb")
        self.state = pickle.load(file)
        file.close()

# ===================================================== MAIN TYPES OF SCRAPED INFO TYPES DEFINITION =====================================================

class ScrapedInfoValence():

    def __init__(self) -> None: pass

    @abc.abstractmethod
    def get_text(self) -> str:
        exit(f"🚨 Method 'get_text' not defined for '{self.__class__.__name__}'")
    @abc.abstractmethod
    def get_valence_score(self, limit_floor: float, limit_ceil: float) -> float:
        exit(f"🚨 Method 'get_text' not defined for '{self.__class__.__name__}'")
    @abc.abstractclassmethod
    def get_metadata(self) -> Dict[str, Any]:
        return {}