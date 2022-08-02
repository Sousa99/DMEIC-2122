from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium                   import webdriver
from typing                     import Any, Dict, Generator, List, Tuple
from tqdm                       import tqdm
from bs4                        import BeautifulSoup

import driver
import scraper
import scraper_valence

# =================================================================== CONSTANTS ===================================================================

BOOKING_SCORE_FLOOR : float = 0
BOOKING_SCORE_CEIL : float = 10

# ============================================================== AUXILIARY FUNCTIONS ==============================================================

def get_until_number_places(page_source: BeautifulSoup) -> int:

    navigation_elem = page_source.find('div', attrs={"data-testid": "pagination"})
    inside_div = navigation_elem.find('div', recursive=False)
    inside_span = inside_div.find('span')
    text = inside_span.get_text()

    number_reviews = int(text.replace('A mostrar ', '').split(' – ')[1])
    return number_reviews

# =========================================================== SCRAPED INFORMATION CLASS ===========================================================

class ScrapedInfoBooking(scraper.ScrapedInfoValence):

    def __init__(self, hotel_name: str, score_floor: float, score_ceil: float,
        review_from: str, review_txt: str, review_score: float, review_date: str) -> None:
        
        self.hotel_name       = hotel_name
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
        return { 'scraper': 'Booking', 'hotel_name': self.hotel_name,
            'reviewer': self.review_from, 'review_date': self.review_date }

# ============================================================ WEB SCRAPER SPECIALIZED ============================================================

class WebScraperBooking(scraper.WebScraper[ScrapedInfoBooking]):

    OFFSET_JUMP : int = 25
    BASE_LINK : str = 'https://www.booking.com'
    REVIEWS_LINK : str = 'https://www.booking.com/searchresults.pt-pt.html?aid=376389&label=Hoteis-dHPE1sykMRe*x3Pll8k6awS267724756065%3Apl%3Ata%3Ap1%3Ap22.563.000%3Aac%3Aap%3Aneg%3Afi%3Atikwd-65526620%3Alp1011769%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YfNeh-lbHkPZfvshG1kRNbU&sid=2bc1d200a27410f21cc9cb82dd6b0a89&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.pt-pt.html%3Faid%3D376389%26label%3DHoteis-dHPE1sykMRe%252Ax3Pll8k6awS267724756065%253Apl%253Ata%253Ap1%253Ap22.563.000%253Aac%253Aap%253Aneg%253Afi%253Atikwd-65526620%253Alp1011769%253Ali%253Adec%253Adm%253Appccp%253DUmFuZG9tSVYkc2RlIyh9YfNeh-lbHkPZfvshG1kRNbU%26sid%3D2bc1d200a27410f21cc9cb82dd6b0a89%26sb_price_type%3Dtotal%26%26&ss=Portugal&is_ski_area=&checkin_year=2022&checkin_month=9&checkin_monthday=29&checkout_year=2022&checkout_month=9&checkout_monthday=30&group_adults=1&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&search_pageview_id=75fd75be590201a0&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0&ac_position=1&ac_langcode=pt&ac_click_type=b&dest_id=171&dest_type=country&place_id_lat=39.7891&place_id_lon=-8.07576&search_pageview_id=75fd75be590201a0&search_selected=true&ss_raw=Po'
    
    def __init__(self) -> None:
        state = { 'current_page': 1, 'number_hotels_parsed': 0 }
        super().__init__('Booking', '0.1', state)

    def get_pages_to_scrape(self, driver: driver.Driver) -> Generator[str, None, None]:

        while True:

            # ============================ In fact get page with important information ============================
            driver.driver_get(f"{self.REVIEWS_LINK}&offset={(self.state['current_page'] - 1) * self.OFFSET_JUMP}")
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

            # Check if finished
            upper_limit = get_until_number_places(link_soup)
            if upper_limit < self.state['current_page'] * self.OFFSET_JUMP: break

            # Companies: Get various companies
            hotels_listed = link_soup.find_all('div', attrs={"data-testid": "property-card"})
            filter_out = link_soup.find_all('div', attrs={"data-testid": "property-card"}, class_="c12ee2f811")
            hotels_listed_filtered = [ hotel for hotel in hotels_listed if hotel not in filter_out]
            if len(hotels_listed_filtered) == 0: break
            # Reader's Reviews: Iterate and Get Link
            for _ in range(self.state['number_hotels_parsed']): hotels_listed_filtered.pop(0)
            for hotel_card in hotels_listed_filtered:
                # Update State
                self.state['number_hotels_parsed'] = self.state['number_hotels_parsed'] + 1

                review_item_link = hotel_card.find('a')
                yield f"{review_item_link['href']}"
            
            # Update State
            self.state['current_page'] = self.state['current_page'] + 1
            self.state['number_hotels_parsed'] = 0

    def scrape_page(self, link: str, driver: driver.Driver) -> Generator[ScrapedInfoBooking, None, None]:

        # Get Current Page
        driver.driver_get(link)
        link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

        hotel_name_elem = link_soup.find('h2', class_='hp__hotel-name')
        if hotel_name_elem is None: hotel_name_elem = link_soup.find('h2', class_='pp-header__title')
        hotel_name = hotel_name_elem.get_text().strip().replace('\n', ' ')

        def wait_until_open_overlay(driver: webdriver.Chrome) -> bool:
            link_soup = BeautifulSoup(driver.page_source, 'html.parser')
            slide_window = link_soup.find('div', attrs={"data-id": "hp-reviews-sliding"})
            return slide_window['aria-hidden'] == "false"

        driver.driver_click_css('#guest-featured_reviews__horizontal-block > div > div.hp-featured_reviews-bottom > button', throw_exception=True)
        driver.driver_wait_until(wait_until_open_overlay)

        def wait_until_reviews_loaded(driver: webdriver.Chrome) -> bool:
            link_soup = BeautifulSoup(driver.page_source, 'html.parser')
            reviews = link_soup.find_all('li', class_="review_list_new_item_block")
            return len(reviews) != 0

        # Wait until reviews load
        driver.driver_wait_until(wait_until_reviews_loaded, throw_exception=False)
        # Parse current Click
        link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')
        # Choose correct language
        driver.driver_click_css('#review_lang_filter > button', throw_exception=False)
        driver.driver_click_css('#review_lang_filter > div > div > ul > li:nth-child(2) > button', throw_exception=False)

        running = True
        while running:
            # Wait until reviews load
            driver.driver_wait_until(wait_until_reviews_loaded, throw_exception=False)
            # Parse current Click
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')
            # Iterate Reviews
            for item in link_soup.find_all('div', class_="c-review-block"):
                review_author   : str   = item.find('span', class_="bui-avatar-block__title").text.strip()
                review_score    : float = float(item.find('div', class_="bui-review-score__badge").text.strip().replace(',', '.'))
                review_date     : str   = item.find('span', class_="c-review-block__date").text.strip()
                
                review_texts : List[str] = []
                for review_sub_text_elem in item.find_all('span', class_='c-review__body'):
                    review_sub_text = review_sub_text_elem.text.replace('\n', '').strip()
                    if review_sub_text == 'Não existem comentários disponíveis para esta avaliação.': continue
                    if (not review_sub_text_elem.has_attr('lang')) or (review_sub_text_elem['lang'] != 'pt'): continue
                    review_texts.append(review_sub_text)
                if len(review_texts) == 0: continue
                review_text = ' | '.join(review_texts)
                
                yield ScrapedInfoBooking(hotel_name, BOOKING_SCORE_FLOOR, BOOKING_SCORE_CEIL, review_author, review_text, review_score, review_date)

            # Click next Page
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')
            next_review_page_div = link_soup.find('div', class_="bui-pagination__next-arrow")
            if next_review_page_div is None or 'bui-pagination__item--disabled' in next_review_page_div['class']:
                running = False
            else:
                try: driver.driver_click_css('#review_list_page_container > div.c-pagination > div > div.bui-pagination__nav > div > div.bui-pagination__item.bui-pagination__next-arrow > a')
                except NoSuchElementException: running = False
                except ElementNotInteractableException: running = False

    def callback_accessible(self, page_source: str) -> bool:
        if "Access Denied" in page_source: return False
        elif "This site can’t be reached" in page_source: return False
        elif "Your connection is not private" in page_source: return False
        elif "No internet" in page_source: return False
        elif "This page isn’t working" in page_source: return False
        return True

# ============================================================ MAIN FUNCTIONALITY ============================================================

scraper_to_use : WebScraperBooking = WebScraperBooking()
request_driver : driver.Driver = driver.Driver(rotate_proxies=False, rotate_proxies_rand=False, rotate_user_agents=True, max_requests=200, max_attempts_driver=20)
request_driver.set_callback_accessible(scraper_to_use.callback_accessible)
scraper_valence.run_scraper(scraper_to_use, request_driver)