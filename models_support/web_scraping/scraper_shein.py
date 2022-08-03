import json

from langdetect import detect
from typing     import Any, Dict, Generator, List, Optional
from bs4        import BeautifulSoup

import driver
import scraper
import scraper_valence

# =================================================================== CONSTANTS ===================================================================

SHEIN_SCORE_FLOOR : float = 1
SHEIN_SCORE_CEIL : float = 5

# ============================================================== AUXILIARY FUNCTIONS ==============================================================

# =========================================================== SCRAPED INFORMATION CLASS ===========================================================

class ScrapedInfoShein(scraper.ScrapedInfoValence):

    def __init__(self, clothe_title: str, clothe_score_floor: float, clothe_score_ceil: float,
        review_from: str, review_txt: str, review_score: float, review_date: str) -> None:
        
        self.clothe_title       = clothe_title
        self.clothe_score_floor = clothe_score_floor
        self.clothe_score_ceil  = clothe_score_ceil
        self.review_from        = review_from
        self.review_txt         = review_txt
        self.review_score       = review_score
        self.review_date        = review_date

    def get_text(self) -> str: return self.review_txt
    def get_valence_score(self, limit_floor: float, limit_ceil: float) -> float:

        clothe_score_range   = self.clothe_score_ceil - self.clothe_score_floor
        limit_range         = limit_ceil - limit_floor

        value_normalized    = (self.review_score - self.clothe_score_floor) / (clothe_score_range)
        return limit_floor + (value_normalized * limit_range)

    def get_metadata(self) -> Dict[str, Any]:
        return { 'scraper': 'Shein', 'clothe_title': self.clothe_title,
            'reviewer': self.review_from, 'review_date': self.review_date }

# ============================================================ WEB SCRAPER SPECIALIZED ============================================================

class WebScraperShein(scraper.WebScraper[ScrapedInfoShein]):

    BASE_LINK : str = 'https://pt.shein.com'
    REVIEWS_LINK : str = 'https://pt.shein.com/promotion/pt-dress-sc-02578099.html?ici=pt_tab01navbar03menu01dir01&scici=navbar_WomenHomePage~~tab01navbar03menu01dir01~~3_1_1~~itemPicking_02578099~~~~0&src_module=topcat&src_tab_page_id=page_select_class1654454021946&src_identifier=fc%3DWomen%60sc%3DMAIS%20VOTADO%60tc%3DCOMPRE%20POR%20CATEGORIA%60oc%3DVestidos%60ps%3Dtab01navbar03menu01dir01%60jc%3DitemPicking_02578099&srctype=category&userpath=category-MAIS-VOTADO-Vestidos'

    def __init__(self) -> None:
        super().__init__('Shein', '0.2', { 'current_page': 1, 'number_goods_parsed': 0 })

    def get_pages_to_scrape(self, driver : driver.Driver) -> Generator[str, None, None]:

        while True:

            # ============================ In fact get page with important information ============================
            driver.driver_get(f"{self.REVIEWS_LINK}&page={self.state['current_page']}")
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

            goods_urls = []
            item_wrappers = link_soup.find_all('div', class_='S-product-item__wrapper')
            for item_wrapper in item_wrappers:
                link_elem = item_wrapper.find('a')
                if link_elem is not None: goods_urls.append(link_elem['href'])

            for _ in range(min(self.state['number_goods_parsed'], len(goods_urls))): goods_urls.pop(0)
            for good_url in goods_urls:
                # Update State
                self.state['number_goods_parsed'] = self.state['number_goods_parsed'] + 1
                yield f'{self.BASE_LINK}{good_url}'

            # Update State
            self.state['current_page'] = self.state['current_page'] + 1
            self.state['number_goods_parsed'] = 0
        
    def scrape_page(self, link: str, driver : driver.Driver) -> Generator[ScrapedInfoShein, None, None]:

        # Get Current Page
        driver.driver_get(link)
        link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')
        blocks_passed_without_valid : int = 0

        while True:

            # Parse current Click
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')
            # Get Global Information
            clothe_title = link_soup.find('meta', { 'property': "og:title" })['content']

            # Iterate Reviews
            review_items = link_soup.find_all('div', class_="j-expose__common-reviews__list-item")
            if len(review_items) == 0: break
            for item in review_items:
                review_author   : str   = item.find('div', class_="nikename").text.strip()
                review_score    : float = float(item.find('div', class_="rate-star")['aria-label'].replace('Classificação', ''))
                review_text     : str   = item.find('div', class_="rate-des").text.replace('\n', ' ').strip()
                review_date     : str   = item.find('div', class_="date").text.strip()

                try:
                    if detect(review_text) == 'pt':
                        blocks_passed_without_valid = 0
                        yield ScrapedInfoShein(clothe_title, SHEIN_SCORE_FLOOR, SHEIN_SCORE_CEIL, review_author, review_text, review_score, review_date)
                    else: blocks_passed_without_valid = blocks_passed_without_valid + 1
                except: blocks_passed_without_valid = blocks_passed_without_valid + 1

            if blocks_passed_without_valid >= 50: break

            # Click next Page
            driver.driver_click_css('body > div.c-outermost-ctn.j-outermost-ctn > div.c-vue-coupon > div.S-dialog > div > i', throw_exception=False)
            element = link_soup.find(attrs={"aria-label": "Page Next"})
            if element is None or (element.has_attr('aria-disabled') and element['aria-disabled'] == "true"): break
            else:
                clicked = True
                try: driver.driver_click_css('[aria-label="Page Next"]')
                except: clicked = False
                if not clicked: break

    def callback_accessible(self, page_source: str) -> bool:
        if "Access Denied" in page_source: return False
        elif "This site can’t be reached" in page_source: return False
        elif "Your connection is not private" in page_source: return False
        elif "No internet" in page_source: return False
        return True

# ============================================================ MAIN FUNCTIONALITY ============================================================

scraper_to_use : WebScraperShein = WebScraperShein()
request_driver : driver.Driver = driver.Driver(rotate_proxies=True, rotate_proxies_rand=False, rotate_user_agents=True, max_requests=200, max_attempts_driver=20)
request_driver.set_callback_accessible(scraper_to_use.callback_accessible)
scraper_valence.run_scraper(scraper_to_use, request_driver)