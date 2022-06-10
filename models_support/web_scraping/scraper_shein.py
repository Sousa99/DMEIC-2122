import json

from typing                             import Any, Generator, List, Optional
from bs4                                import BeautifulSoup

import driver
import scraper

# ============================================================== GLOBAL USAGE ==============================================================

request_driver = driver.Driver()

# ============================================================== AUXILIARY FUNCTIONS ==============================================================

def get_data_variable(soup: BeautifulSoup) -> Optional[Any]:

    for script_item in soup.find_all('script'):
        if 'var gbProductListSsrData = ' not in script_item.text: continue
        for line in script_item.text.splitlines():
            if 'var gbProductListSsrData = ' not in line: continue

            data_variable_json = line.replace('var gbProductListSsrData = ', '')
            data = json.loads(data_variable_json)
            return data

    return None

def get_list_of_goods(data: Any) -> List[str]:

    goods_urls : List[str] = []
    for good in data['results']['goods']:
        goods_urls.append(good['pretreatInfo']['goodsDetailUrl'])
    
    return goods_urls

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

# ============================================================ WEB SCRAPER SPECIALIZED ============================================================

class WebScraperShein(scraper.WebScraper[ScrapedInfoShein]):

    BASE_LINK : str = 'https://pt.shein.com'
    REVIEWS_LINK : str = 'https://pt.shein.com/promotion/pt-dress-sc-02578099.html?ici=pt_tab01navbar03menu01dir01&scici=navbar_WomenHomePage~~tab01navbar03menu01dir01~~3_1_1~~itemPicking_02578099~~~~0&src_module=topcat&src_tab_page_id=page_select_class1654454021946&src_identifier=fc%3DWomen%60sc%3DMAIS%20VOTADO%60tc%3DCOMPRE%20POR%20CATEGORIA%60oc%3DVestidos%60ps%3Dtab01navbar03menu01dir01%60jc%3DitemPicking_02578099&srctype=category&userpath=category-MAIS-VOTADO-Vestidos'

    def __init__(self) -> None:
        super().__init__('Shein')

    def get_pages_to_scrape(self) -> Generator[str, None, None]:

        current_page : int   = 0
        while True:
            current_page = current_page + 1

            # ============================ In fact get page with important information ============================
            request_driver.driver_get(f"{self.REVIEWS_LINK}&page={current_page}")
            link_soup = BeautifulSoup(request_driver.driver_page_source(), 'html.parser')

            print(link_soup)
            exit()

            # Get Variable with Information
            data = get_data_variable(link_soup)
            goods_urls = get_list_of_goods(data)
            if len(goods_urls) == 0: break

            for good_url in goods_urls:
                yield f'{self.BASE_LINK}{good_url}'

    def scrape_page(self, link: str) -> List[ScrapedInfoShein]:

        reviews : List[ScrapedInfoShein] = []

        # Get Current Page
        request_driver.driver_get(link)
        link_soup = BeautifulSoup(request_driver.driver_page_source(), 'html.parser')

        for _ in range(2):

            # Parse current Click
            link_soup = BeautifulSoup(request_driver.driver_page_source(), 'html.parser')
            # Get Global Information
            clothe_title = link_soup.find('meta', { 'property': "og:title" })['content']

            # Iterate Reviews
            for item in link_soup.find_all('div', class_="j-expose__common-reviews__list-item"):
                review_author   : str   = item.find('div', class_="nikename").text.strip()
                review_score    : float = float(item.find('div', class_="rate-star")['aria-label'].replace('Classificação', ''))
                review_text     : str   = item.find('div', class_="rate-des").text.replace('\n', ' ').strip()
                review_date     : str   = item.find('div', class_="date").text.strip()
                
                reviews.append(ScrapedInfoShein(clothe_title, 1, 5, review_author, review_text, review_score, review_date))

            # Click next Page
            request_driver.driver_click_css("[aria-label='Page Next']")

        return reviews

# ============================================================ TEST ZONE ============================================================

scraper_to_use = WebScraperShein()
for page in scraper_to_use.get_pages_to_scrape():
    print(f'⚙️  Page: {page}')
    for review in scraper_to_use.scrape_page(page):
        print(f'  ⚙️  Review: {vars(review)}')

    exit()