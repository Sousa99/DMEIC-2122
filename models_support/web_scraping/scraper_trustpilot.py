from selenium   import webdriver
from typing     import Any, Dict, Generator, List
from bs4        import BeautifulSoup


import driver
import scraper
import scraper_valence

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
    REVIEWS_LINKS : List[str] = [
        'https://pt.trustpilot.com/categories/money_insurance',
        'https://pt.trustpilot.com/categories/vehicles_transportation',
        'https://pt.trustpilot.com/categories/jewelry_store',
        'https://pt.trustpilot.com/categories/clothing_store',
        'https://pt.trustpilot.com/categories/electronics_technology',
        'https://pt.trustpilot.com/categories/fitness_and_nutrition_service'
    ]

    def __init__(self) -> None:
        state = { 'current_category': 0,
            'current_page': 1, 'number_companies_parsed': 0 ,
            'reviews_page': 1, 'number_reviews_parsed': 0 }
        super().__init__('TrustPilot', '0.2', state)

    def get_pages_to_scrape(self, driver: driver.Driver) -> Generator[str, None, None]:

        review_links_to_use = self.REVIEWS_LINKS[self.state['current_category']:]
        for review_link in review_links_to_use:
            review_link_total = f"{review_link}?numberofreviews=0&status=all&timeperiod=0&"

            while True:

                # ============================ In fact get page with important information ============================
                driver.driver_get(f"{review_link_total}page={self.state['current_page']}")
                link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

                # Listings: Get the various listings and select one
                listings = link_soup.find_all('div', class_="styles_businessUnitCardsContainer__1ggaO")
                if (len(listings)) == 0: break
                listing = listings[0]
                if len(listings) == 2: listing = listings[1]
                # Companies: Get various companies
                companies_listed = listing.find_all('div', class_="card_card__2F_07")
                if len(companies_listed) == 0: break
                # Reader's Reviews: Iterate and Get Link
                for _ in range(self.state['number_companies_parsed'] - 1): companies_listed.pop(0)
                for company_card in companies_listed:
                    # Update State
                    self.state['number_companies_parsed'] = self.state['number_companies_parsed'] + 1

                    review_item_link = company_card.find('a')
                    yield f"{self.BASE_LINK}{review_item_link['href']}"
                    # Update State
                    self.state['reviews_page'] = 1
                
                # Update State
                self.state['current_page'] = self.state['current_page'] + 1
                self.state['number_companies_parsed'] = 0

            # Update State
            self.state['current_category'] = self.state['current_category'] + 1
            self.state['current_page'] = 1

    def scrape_page(self, link: str, driver: driver.Driver) -> Generator[ScrapedInfoTrustPilot, None, None]:
        
        while True:

            # ============================ In fact get page with reviews information ============================
            link_to_check = f"{link}?page={self.state['reviews_page']}"
            driver.driver_get(link_to_check)
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

            def wait_until_loaded(driver: webdriver.Chrome) -> bool:
                link_soup = BeautifulSoup(driver.page_source, 'html.parser')
                return link_soup.find('span', class_="title_displayName__TtDDM") != None
            try: driver.driver_wait_until(wait_until_loaded)
            except: pass

            company_name = link_soup.find('span', class_="title_displayName__TtDDM").get_text().strip()

            # Finished Parsing Reviews
            if self.state['reviews_page'] != 1 and link_to_check != driver.driver_get_current_url():
                self.state['reviews_page'] = 0
                return
            
            review_cards = link_soup.find_all('article', attrs={"data-service-review-card-paper": "true"})
            for _ in range(self.state['number_reviews_parsed']): review_cards.pop(0)
            for review_card in review_cards:
                # Update State
                self.state['number_reviews_parsed'] = self.state['number_reviews_parsed'] + 1

                review_from = review_card.find('div', attrs={"data-consumer-name-typography": "true"}).get_text()

                review_score_elem = review_card.find('div', attrs={"data-service-review-rating": True})
                if review_score_elem is None: continue
                review_score = float(review_score_elem["data-service-review-rating"])

                review_text_elem = review_card.find('p', attrs={"data-service-review-text-typography": "true"})
                if review_text_elem is None: continue
                review_text = review_text_elem.get_text()

                review_date_elem = review_card.find('time', attrs={"data-service-review-date-time-ago": "true"})
                if review_date_elem is None: continue
                if not review_date_elem.has_attr('title'): continue
                review_date = review_date_elem['title']

                yield ScrapedInfoTrustPilot(company_name, TRUST_PILOT_SCORE_FLOOR, TRUST_PILOT_SCORE_CEIL,
                    review_from, review_text, review_score, review_date)
            
            # Update State
            self.state['reviews_page'] = self.state['reviews_page'] + 1
            self.state['number_reviews_parsed'] = 0

    def callback_accessible(self, page_source: str) -> bool:
        if "Access Denied" in page_source: return False
        elif "This site can’t be reached" in page_source: return False
        elif "Your connection is not private" in page_source: return False
        elif "No internet" in page_source: return False
        elif "This page isn’t working" in page_source: return False
        elif "We have received an unusually large amount of requests from your IP so you have been rate limited" in page_source: return False
        return True

# ============================================================ MAIN FUNCTIONALITY ============================================================

scraper_to_use : WebScraperTrustPilot = WebScraperTrustPilot()
request_driver : driver.Driver = driver.Driver(rotate_proxies=True, rotate_proxies_rand=True, rotate_user_agents=True, max_requests=200, max_attempts_driver=20)
request_driver.set_callback_accessible(scraper_to_use.callback_accessible)
scraper_valence.run_scraper(scraper_to_use, request_driver)