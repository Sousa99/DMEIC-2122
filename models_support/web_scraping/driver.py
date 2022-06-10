import random

from bs4                                        import BeautifulSoup
from tqdm                                       import tqdm
from typing                                     import List, Optional, Tuple
from selenium                                   import webdriver
from fake_useragent                             import UserAgent
from selenium.webdriver.common.by               import By
from selenium.webdriver.common.action_chains    import ActionChains
from selenium.webdriver.chrome.options          import Options

# =============================================================== AUXILIARY FUNCTIONS ===============================================================

def scrape_proxies() -> List[Tuple[str, str]]:

    # Create driver and get page
    options : Options = Options()
    options.headless = False
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.socks-proxy.net/")

    proxies : List[Tuple[str, str]] = []

    # Get ips and ports
    table_body_query = "#list > div > div.table-responsive > div > table > tbody"
    element = driver.find_element(by=By.CSS_SELECTOR, value=table_body_query)
    for row_element in element.find_elements(by=By.CSS_SELECTOR, value="tr"):
        table_cells = row_element.find_elements(by=By.CSS_SELECTOR, value="td")
        ip_address, port = table_cells[0].text, table_cells[1].text

        proxies.append((ip_address.strip(), port.strip()))

    driver.quit()
    return proxies

def check_proxies(list_proxies: List[Tuple[str, str]]) -> List[Tuple[str, str]]:

    def valid_proxy(ip_address: str, port: str) -> bool:

        # Create driver and get page
        options : Options = Options()
        options.headless = False
        options.add_argument(f'--proxy-server=http://{ip_address}:{port}')
        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://whatismyipaddress.com/")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response_items = soup.findAll("span", class_="cf-footer-item sm:block sm:mb-1")
            if len(response_items) <= 2: return False 
            ip_address_item = response_items[1]
            ip_address_found = ip_address_item.text.replace('Your IP: ', '').strip()
        
            if ip_address_item is None: return False
            if ip_address_found != ip_address: return False
            tqdm.write(f"🚀 Proxy '{ip_address}:{port}' successful!")
            return True

        except Exception as e: return False
        finally: driver.quit()

    list_proxies = list_proxies[0:2]
    tqdm_iterable = tqdm(list_proxies, desc="🌐 Verifying proxies", leave=False)
    filtered_proxies = list(filter(lambda proxy_item: valid_proxy(proxy_item[0], proxy_item[1]), tqdm_iterable))
    return filtered_proxies

# ============================================================== MAIN CLASS DEFINITION ==============================================================

class Driver():

    def __init__(self, headless : bool = False, rotate_proxies : bool = False,
        rotate_user_agents : bool = False, max_requests : Optional[int] = None) -> None:

        self.headless           : bool                          = headless
        self.max_requests       : Optional[int]                 = max_requests

        self.current_count_req  : int                           = 0
        self.selenium_webdriver : Optional[webdriver.Chrome]    = None
        self.proxies            : Optional[List[str, str]]      = None
        self.user_agent_gen     : Optional[UserAgent]           = None

        if rotate_proxies:
            possible_proxies = scrape_proxies()
            print(f"🌐 Proxies found: '{len(possible_proxies)}'")
            valid_proxies = check_proxies(possible_proxies)
            print(f"🌐 Valid Proxies found: '{len(valid_proxies)}'")
            self.proxies = valid_proxies
        if rotate_user_agents: self.user_agent_gen = UserAgent()

    def generate_new_driver(self) -> None:
        
        # Definition of Selenium WebDriver Options
        options : Options = Options()
        options.headless = self.headless
        options.add_argument("--window-size=1920,1200")

        # Choose Proxy
        if self.proxies is not None and len(self.proxies) > 0:
            ip_address, port = random.choice(self.proxies)
            options.add_argument(f'--proxy-server=http://{ip_address}:{port}')
        # Choose User Agents
        if self.user_agent_gen is not None:
            options.add_argument(f'user-agent={self.user_agent_gen.random}')

        # Generate driver
        self.selenium_webdriver = webdriver.Chrome(options=options)
        if self.max_requests is not None: self.current_count_req = 0

    def driver_get(self, link : str) -> None:
        
        if self.selenium_webdriver is None: self.generate_new_driver()
        if self.current_count_req >= self.max_requests: self.generate_new_driver()
        self.current_count_req = self.current_count_req + 1

        self.selenium_webdriver.get(link)

    def driver_page_source(self) -> str:
        return self.selenium_webdriver.page_source
        
    def driver_click_css(self, css_selector: str, wait: int = 10) -> None:
        element = self.selenium_webdriver.find_element(by=By.CSS_SELECTOR, value=css_selector)
        ActionChains(self.selenium_webdriver).move_to_element(element).click(element).perform()
        self.selenium_webdriver.implicitly_wait(wait)
        
    def driver_quit(self) -> None:
        self.selenium_webdriver.quit()