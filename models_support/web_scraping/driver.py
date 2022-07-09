
from bs4                                        import BeautifulSoup
from tqdm                                       import tqdm
from fp.fp                                      import FreeProxy
from typing                                     import Callable, List, Optional
from selenium                                   import webdriver
from fake_useragent                             import UserAgent
from selenium.common.exceptions                 import SessionNotCreatedException
from selenium.webdriver.common.by               import By
from selenium.webdriver.support.ui              import WebDriverWait
from selenium.webdriver.common.action_chains    import ActionChains
from selenium.webdriver.chrome.options          import Options

# =============================================================== AUXILIARY FUNCTIONS ===============================================================

# ============================================================== MAIN CLASS DEFINITION ==============================================================

class Driver():

    def __init__(self, headless : bool = False, rotate_proxies : bool = False, rotate_proxies_rand : bool = False,
        rotate_user_agents : bool = False, max_requests : Optional[int] = None, max_attempts_driver: int = 5) -> None:

        self.headless               : bool                              = headless
        self.max_requests           : Optional[int]                     = max_requests
        self.max_attempts_driver    : int                               = max_attempts_driver

        self.current_count_req      : int                               = 0
        self.selenium_webdriver     : Optional[webdriver.Chrome]        = None
        self.proxies_gen            : Optional[FreeProxy]               = None
        self.user_agent_gen         : Optional[UserAgent]               = None

        self.callback_accessible    : Optional[Callable[[str], bool]]   = None

        if rotate_proxies: self.proxies_gen = FreeProxy(rand=rotate_proxies_rand)
        if rotate_user_agents: self.user_agent_gen = UserAgent()

    def set_callback_accessible(self, callback: Callable[[str], bool]) -> None:
        self.callback_accessible = callback

    def generate_new_driver(self) -> None:
        if self.selenium_webdriver is not None: self.driver_quit()
   
        # Definition of Selenium WebDriver Options
        options : Options = Options()
        options.headless = self.headless
        options.add_argument("--window-size=1344,840")

        # Spoof Selenium
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        #options.add_argument('--start-fullscreen')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--incognito")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("disable-infobars")

        # Choose Proxy
        if self.proxies_gen is not None:
            proxy_ip = self.proxies_gen.get().split("://")[1]
            options.add_argument(f'--proxy-server={proxy_ip}')
            webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "httpProxy": proxy_ip,
                "ftpProxy": proxy_ip,
                "sslProxy": proxy_ip,
                "noProxy": None,
                "proxyType": "MANUAL",
                "autodetect": False
            }

            webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
        # Choose User Agents
        if self.user_agent_gen is not None: options.add_argument(f'user-agent={self.user_agent_gen.random}')

        # Generate driver
        self.selenium_webdriver = webdriver.Chrome(options=options)
        if self.max_requests is not None: self.current_count_req = 0

    def driver_get(self, link : str) -> None:

        attempts = 0
        while attempts < self.max_attempts_driver:
        
            try:
                if self.selenium_webdriver is None: self.generate_new_driver()
                elif self.max_requests is not None and self.current_count_req >= self.max_requests: self.generate_new_driver()
                self.current_count_req = self.current_count_req + 1

                attempts = attempts + 1
                self.selenium_webdriver.get(link)
                page_source = self.selenium_webdriver.page_source

                if self.callback_accessible is not None and not self.callback_accessible(page_source):
                    raise Exception("🚨 Page not accessible!")
                
                if attempts > 1: tqdm.write("✅ Eventually webdriver was initialized successfully!")
                return
            
            except SessionNotCreatedException as e:
                tqdm.write("⚠️  Webdriver session could not be created!")
                self.selenium_webdriver = None
                attempts = attempts + 1
            except Exception as e:
                error_message = str(e)
                error_message = error_message[:error_message.find('\n')]
                tqdm.write(f"⚠️  Exception while initializing webdriver: '{error_message}'")
                self.selenium_webdriver.quit()
                self.selenium_webdriver = None
                attempts = attempts + 1
        
        if attempts >= self.max_attempts_driver:
            exit(f"🚨 Driver could not be initialized '{self.max_attempts_driver}' times in a row!")

    def driver_page_source(self) -> str:
        return self.selenium_webdriver.page_source
        
    def driver_click_css(self, css_selector: str, wait: int = 10, throw_exception: bool = True) -> None:
        try:
            element = self.selenium_webdriver.find_element(by=By.CSS_SELECTOR, value=css_selector)
            ActionChains(self.selenium_webdriver).move_to_element(element).click(element).perform()
            self.selenium_webdriver.implicitly_wait(wait)
        except Exception as e:
            if throw_exception: raise(e)

    def driver_wait_until(self, wait_function: Callable[[webdriver.Chrome], bool], wait: int = 10, throw_exception: bool = True) -> None:
        try:
            WebDriverWait(self.selenium_webdriver, wait).until(lambda wd: wait_function(wd))
        except Exception as e:
            if throw_exception: raise(e)

    def driver_get_current_url(self) -> str:
        return self.selenium_webdriver.current_url;

    def driver_quit(self) -> None:
        self.selenium_webdriver.quit()