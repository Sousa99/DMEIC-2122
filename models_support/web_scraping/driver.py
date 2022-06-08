from typing import Optional
from selenium                                   import webdriver
from selenium.webdriver.common.by               import By
from selenium.webdriver.chrome.options          import Options
from selenium.webdriver.common.action_chains    import ActionChains

# ============================================================== MAIN CLASS DEFINITION ==============================================================

class Driver():

    # Definition of max requests before change
    MAX_REQUESTS : Optional[int] = None

    # Definition of Selenium WebDriver Options
    options : Options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1200")

    def __init__(self) -> None:
        self.current_count_req  : int                           = 0
        self.selenium_webdriver : Optional[webdriver.Chrome]    = None

    def generate_new_driver(self) -> None:
        self.selenium_webdriver = webdriver.Chrome(options=self.options)
        if self.MAX_REQUESTS is not None:
            self.current_count_req = self.current_count_req - self.MAX_REQUESTS

    def driver_get(self, link : str) -> None:

        if self.selenium_webdriver is None: self.generate_new_driver()
        if self.MAX_REQUESTS is not None and self.current_count_req >= self.MAX_REQUESTS:
            self.generate_new_driver()
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