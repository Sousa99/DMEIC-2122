from typing import Any, Dict, Generator, Optional
from bs4    import BeautifulSoup

import driver
import scraper

# =================================================================== CONSTANTS ===================================================================

TRUST_PILOT_SCORE_FLOOR : float = 0
TRUST_PILOT_SCORE_CEIL : float = 5

# ============================================================== AUXILIARY FUNCTIONS ==============================================================

# =========================================================== SCRAPED INFORMATION CLASS ===========================================================

class ScrapedInfoTrustPilot(scraper.ScrapedInfoValence):

    def __init__(self, company_name: str, score_floor: float, score_ceil: float,
        review_from: str, review_txt: str, review_score: float, review_date: str) -> None:
        
        self.company_name       = company_name
        self.score_floor        = score_floor
        self.score_ceil         = score_ceil
        self.review_from        = review_from
        self.review_txt         = review_txt
        self.review_score       = review_score
        self.review_date        = review_date

    def get_text(self) -> str: return self.review_txt

    def get_valence_score(self, limit_floor: float, limit_ceil: float) -> float:

        review_score_range  = self.score_ceil - self.score_floor
        limit_range         = limit_ceil - limit_floor

        value_normalized    = (self.review_score - self.score_floor) / (review_score_range)
        return limit_floor + (value_normalized * limit_range)

    def get_metadata(self) -> Dict[str, Any]:
        return { 'scraper': 'TrustPilot', 'company_name': self.company_name,
            'reviewer': self.review_from, 'review_date': self.review_date }

# ============================================================ WEB SCRAPER SPECIALIZED ============================================================

class WebScraperTrustPilot(scraper.WebScraper[ScrapedInfoTrustPilot]):

    BASE_LINK : str = 'https://pt.trustpilot.com'
    REVIEWS_LINK : str = 'https://pt.trustpilot.com/categories/money_insurance'

    def __init__(self) -> None:
        super().__init__('TrustPilot', { 'current_page': 0, 'reviews_page': 0 })

    def get_pages_to_scrape(self, driver: driver.Driver) -> Generator[str, None, None]:

        while True:
            self.state['current_page'] = self.state['current_page'] + 1

            # ============================ In fact get page with important information ============================
            driver.driver_get(f"{self.REVIEWS_LINK}?page={self.state['current_page']}")
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

            # Listings: Get the various listings and select one
            listings = link_soup.find_all('div', class_="styles_businessUnitCardsContainer__1ggaO")
            listing = listings[0]
            if len(listings) == 2: listing = listings[1]
            # Companies: Get various companies
            companies_listed = listing.find_all('div', class_="card_card__2F_07")
            if len(companies_listed) == 0: return
            # Reader's Reviews: Iterate and Get Link
            for company_card in companies_listed:
                review_item_link = company_card.find('a')
                yield f"{self.BASE_LINK}{review_item_link['href']}"

            exit(0)

    def scrape_page(self, link: str, driver: driver.Driver) -> Generator[ScrapedInfoTrustPilot, None, None]:
        
        self.state['reviews_page'] = 0
        while True:
            self.state['reviews_page'] = self.state['reviews_page'] + 1

            # ============================ In fact get page with reviews information ============================
            link_to_check = f"{link}?page={self.state['reviews_page']}"
            driver.driver_get(link_to_check)
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

            company_name = link_soup.find('span', class_="title_displayName__TtDDM").get_text().strip()

            if self.state['reviews_page'] != 1 and link_to_check != driver.driver_get_current_url(): return
            review_cards = link_soup.find_all('article', attrs={"data-service-review-card-paper": "true"})
            for review_card in review_cards:

                review_from = review_card.find('div', attrs={"data-consumer-name-typography": "true"}).get_text()

                review_score_elem = review_card.find('div', attrs={"data-service-review-rating": True})
                if review_score_elem is None: continue
                review_score = float(review_score_elem["data-service-review-rating"])

                review_text_elem = review_card.find('p', attrs={"data-service-review-text-typography": True})
                if review_text_elem is None: continue
                review_text = review_score_elem.get_text()

                review_date_elem = review_card.find('time', attrs={"data-service-review-date-time-ago": "true"})
                if review_date_elem is None: continue
                if not review_date_elem.has_attr('title'): continue
                review_date = review_date_elem['title']

                yield ScrapedInfoTrustPilot(company_name, TRUST_PILOT_SCORE_FLOOR, TRUST_PILOT_SCORE_CEIL,
                    review_from, review_text, review_score, review_date)

    def callback_accessible(self, page_source: str) -> bool:
        if "This site can't be reached" in page_source: return False
        return True
