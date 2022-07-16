from typing import Any, Dict, Generator, Optional
from bs4    import BeautifulSoup

import driver
import scraper
import scraper_valence

# ============================================================== AUXILIARY FUNCTIONS ==============================================================

def get_moview_info(link: str, driver: driver.Driver) -> Optional[Dict[str, Any]]:

    driver.driver_get(link)
    link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

    movie_box = link_soup.find('div', class_='fichatecfilme')
    if movie_box is None: return None
    movie_box_inner = movie_box.findChildren('dd')
    if len(movie_box_inner) < 2: return None

    movie_name = movie_box_inner[0].get_text()
    if len(movie_box_inner) < 2: movie_from = 'Unknown'
    else:
        movie_from_children = movie_box_inner[1].findChildren()
        if movie_from_children is None or len(movie_from_children) == 0: movie_from = 'Unknown'
        else: movie_from = movie_from_children[0].get_text()

    movie_readers_reviews = link_soup.find('section', class_='votosdosleitores')
    if movie_readers_reviews is None: return None
    movie_form = movie_readers_reviews.findChild('form', id='votar')
    if movie_form is None: return None
    movie_scores_inputs = movie_form.findChildren('div', recursive=False)
    if len(movie_scores_inputs) == 0: return None

    movie_score_values = list(map(lambda item: float(item.find('a').text), movie_scores_inputs))
    movie_score_floor = min(movie_score_values)
    movie_score_ceil = max(movie_score_values)
    movie_score_items = movie_form.find('input')
    if movie_score_items is None: return None
    movie_score = float(movie_score_items['value'])

    return { 'movie_name': movie_name, 'movie_from': movie_from,
        'movie_score': movie_score, 'movie_score_floor': movie_score_floor, 'movie_score_ceil': movie_score_ceil }

# =========================================================== SCRAPED INFORMATION CLASS ===========================================================

class ScrapedInfoCineCartaz(scraper.ScrapedInfoValence):

    def __init__(self, movie_name: str, movie_from: str, movie_score: float,
        movie_score_floor: float, movie_score_ceil: float,
        review_from: str, review_txt: str, review_date: str) -> None:
        
        self.movie_name         = movie_name
        self.movie_from         = movie_from
        self.movie_score        = movie_score
        self.movie_score_floor  = movie_score_floor
        self.movie_score_ceil   = movie_score_ceil
        self.review_from        = review_from
        self.review_txt         = review_txt
        self.review_date        = review_date

    def get_text(self) -> str: return self.review_txt

    def get_valence_score(self, limit_floor: float, limit_ceil: float) -> float:

        movie_score_range   = self.movie_score_ceil - self.movie_score_floor
        limit_range         = limit_ceil - limit_floor

        value_normalized    = (self.movie_score - self.movie_score_floor) / (movie_score_range)
        return limit_floor + (value_normalized * limit_range)

    def get_metadata(self) -> Dict[str, Any]:
        return { 'scraper': 'CineCartaz', 'movie_title': self.movie_name, 'movie_author': self.movie_from,
            'reviewer': self.review_from, 'review_date': self.review_date }

# ============================================================ WEB SCRAPER SPECIALIZED ============================================================

class WebScraperCineCartaz(scraper.WebScraper[ScrapedInfoCineCartaz]):

    BASE_LINK : str = 'https://cinecartaz.publico.pt'
    REVIEWS_LINK : str = 'https://cinecartaz.publico.pt/Criticas'

    def __init__(self) -> None:
        super().__init__('CineCartaz', '0.2', { 'current_page': 1, 'number_reviews_parsed': 0 })

    def get_pages_to_scrape(self, driver: driver.Driver) -> Generator[str, None, None]:

        while True:

            # ============================ In fact get page with important information ============================
            driver.driver_get(f"{self.REVIEWS_LINK}?pagina={self.state['current_page']}")
            link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

            # Reader's Reviews: Get and Check if section is present
            reviews_from_readers_section = link_soup.find('section', id='criticas-leitores')
            if reviews_from_readers_section is None: break
            # Reader's Reviews: Get and Check if list element
            reviews_from_readers_list = reviews_from_readers_section.find('ul', recursive=False)
            if reviews_from_readers_list is None: break
            # Reader's Reviews: Get and Check if list items
            reviews_from_readers = reviews_from_readers_list.findChildren(recursive=False)
            if len(reviews_from_readers) == 0: break
            # Reader's Reviews: Iterate and Get Link
            for _ in range(self.state['number_reviews_parsed']): reviews_from_readers.pop(0)
            for review_item in reviews_from_readers:
                # Update State
                self.state['number_reviews_parsed'] = self.state['number_reviews_parsed'] + 1

                review_item_header = review_item.find('h3')
                review_item_link = review_item_header.find('a')
                yield f"{self.BASE_LINK}{review_item_link['href']}"

            # Update State
            self.state['current_page'] = self.state['current_page'] + 1
            self.state['number_reviews_parsed'] = 0

    def scrape_page(self, link: str, driver: driver.Driver) -> Generator[ScrapedInfoCineCartaz, None, None]:
        
        driver.driver_get(link)
        link_soup = BeautifulSoup(driver.driver_page_source(), 'html.parser')

        review_article = link_soup.find('article', class_='critica')
        if review_article is None: return

        review_text_div = review_article.find('div', class_='grid_6 alpha')
        if review_text_div is None: return
        review_text_strings = review_text_div.findAll(text=True)
        review_text = ' '.join(map(lambda string: string.strip(), review_text_strings))

        review_footer = review_article.find('footer')
        if review_footer is None: return
        review_footer_infos = review_footer.find_all('strong')
        if len(review_footer_infos) != 2: return
        review_date = review_footer_infos[0].get_text()
        review_author = review_footer_infos[1].get_text()

        movie_file_item = link_soup.find('ul', class_='fichatec')
        if movie_file_item is None: return
        movie_file_items = movie_file_item.findChildren('li', recursive=False)
        if len(movie_file_items) == 0: return
        movie_item_link = movie_file_items[0].find('a')
        movie_link = f"{self.BASE_LINK}{movie_item_link['href']}"

        movie_info = get_moview_info(movie_link, driver)
        if movie_info is None: return

        yield ScrapedInfoCineCartaz(movie_info['movie_name'], movie_info['movie_from'], movie_info['movie_score'],
            movie_info['movie_score_floor'], movie_info['movie_score_ceil'],
            review_author, review_text, review_date)

    def callback_accessible(self, page_source: str) -> bool:
        if "Access Denied" in page_source: return False
        elif "This site can’t be reached" in page_source: return False
        elif "Your connection is not private" in page_source: return False
        elif "No internet" in page_source: return False
        return True

# ============================================================ MAIN FUNCTIONALITY ============================================================

scraper_to_use : WebScraperCineCartaz = WebScraperCineCartaz()
request_driver : driver.Driver = driver.Driver(max_attempts_driver=20)
request_driver.set_callback_accessible(scraper_to_use.callback_accessible)
scraper_valence.run_scraper(scraper_to_use, request_driver)